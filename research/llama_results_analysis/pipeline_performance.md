# Pipeline Performance Analysis: GenSIE with Llama 3.2 3B

## Overview
This report analyzes the performance of various extraction strategies implemented in `src/gensie/baseline.py`, focusing on why the `two-pass` strategy outperforms others and the specific failure modes of the `end-anchored` approach.

## 1. The Success of the `two-pass` Strategy
The `two-pass` strategy consistently achieves the highest F1 scores (0.6269 on Starter, 0.5713 on Dev). 

### Key Findings:
*   **Cognitive Offloading:** Decoupling the semantic analysis (Pass 1) from the structural formatting (Pass 2) is critical for Small Language Models (SLMs) like Llama 3.2 3B. 
*   **Natural Language Scratchpad:** Pass 1 allows the model to "think" in Spanish, identifying key entities and relations without the syntactic overhead of JSON. This acts as a high-quality "distilled" context for the second pass.
*   **Context Concentration:** By the time the model reaches Pass 2, it has its own summary to work from, reducing the effort needed to scan the original (potentially long) input text.

## 2. The Failure of `end-anchored` on Dev Set
While `end-anchored` performs well on the simple `starter` set (0.6035 F1), it drops significantly on `dev` (0.4619 F1).

### Root Causes:
*   **Schema Complexity Gap:** Starter schemas are flat (L1 complexity), while Dev schemas are hierarchical (L5 complexity) with nested objects and arrays.
*   **Template Length vs. Model Window:** The `generate_blank_template` creates a large boilerplate for complex schemas. For Llama 3.2 3B, a large empty template at the end of a long prompt can lead to "attention drift," where the model loses focus on the original instructions or context.
*   **Missing Reasoning Step:** Unlike `two-pass`, `end-anchored` forces the model to perform extraction and formatting in a single step. On complex schemas, the model's limited "reasoning capacity" is consumed by maintaining JSON syntax, leading to lower semantic accuracy (Recall).

## 3. Impact of `InvariantPromptMixin`
The invariants applied to `two-pass`, `grounded`, and `auditor` provide a significant boost to reliability.

### Observations:
*   **TypeScript Compression:** Replacing verbose JSON Schema with concise TypeScript interfaces reduces token count by ~40-60% for complex schemas, allowing more room for context and analysis.
*   **Strict Grounding (Null Rule):** The explicit "Extract-or-Null" rule is the primary driver of Precision. Without it, the model tends to guess values for missing fields to "complete" the JSON object.
*   **Dialect Awareness:** Crucial for the Spanish-centric GenSIE task. It ensures that regional variations (e.g., Iberian vs. Latin American terms) are correctly mapped to the target schema.

## 4. Suggested Optimizations (No New Components)
*   **Schema-Aware Analysis:** In `TwoPassAgent.run`, Pass 1 should include the compressed TS schema. Currently, Pass 1 is "schema-blind," which might cause it to miss details required by the specific output format.
*   **Hybrid Template:** Combine `two-pass` reasoning with `end-anchored` templates. Instead of a blank template in Pass 2, provide a template "partially filled" or "commented" with the analysis from Pass 1.
*   **Standardizing Invariants:** Apply `InvariantPromptMixin` to the `EndAnchoredAgent` to test if the TS schema and null rules can recover its performance on Dev.
