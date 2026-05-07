# GenSIE: Llama Implementation Results Analysis

## Executive Summary
This report analyzes the performance of Llama 3.2 3B on the GenSIE (General-purpose Schema-guided Information Extraction) task. The investigation reveals that the **Two-Pass Strategy** is the most effective approach for small language models, achieving an F1 of 0.6269 on the Starter set and 0.5713 on the Dev set. The success of this strategy is attributed to **cognitive offloading**, where the model first performs natural language reasoning before committing to a structured JSON format. 

Conversely, the **End-Anchored** approach, while simple, suffers from "attention drift" on complex hierarchical schemas. The **Invariant Prompting** (TypeScript schemas, Null Rule, Dialect Awareness) is confirmed as a critical precision guard. Proposed improvements focus on **Schema-Aware Reasoning** and **Hybrid Scaffolding** to boost recall and precision without adding architectural complexity or external dependencies.

## Research Questions

### 1. Analysis of Pipeline Performance
**Why does the `two-pass` strategy work best, and why does `end-anchored` fail on the `dev` set?**
*   **Two-Pass Strength:** Decoupling reasoning from formatting allows the model to use its linguistic "working memory" effectively. Pass 1 acts as a distilled context for Pass 2.
*   **End-Anchored Weakness:** Large blank templates for complex schemas (L5 complexity in Dev) overwhelm the model's limited attention window, leading to lower semantic accuracy.
*   **Detailed Analysis:** [Pipeline Performance Analysis](llama_results_analysis/pipeline_performance.md)

### 2. Evaluating the Impact of Schema Invariants
**How much do the "Extractions Invariants" contribute to success, and can they be applied more effectively?**
*   **TS vs. JSON Schema:** TypeScript interfaces are significantly more token-efficient (~40-60% reduction) and align better with the model's pre-training on code.
*   **The Null Rule:** Essential for suppressing the model's tendency to guess missing information, directly addressing the GenSIE "Hallucination Trap."
*   **Detailed Analysis:** [Impact Analysis: Schema Invariants](llama_results_analysis/schema_invariants.md)

### 3. Optimization without New Components
**What existing logic can be unified or tuned to improve F1?**
*   **Targeted Reasoning:** Pass 1 of the two-pass strategy should be provided with the schema to ensure the analysis is "extraction-aware."
*   **Hybrid Scaffolding:** Using the results of the analysis pass to partially populate or "comment" the response template in Pass 2.
*   **Detailed Analysis:** [Optimization Strategies](llama_results_analysis/optimization_strategies.md)

## Conclusions
1.  **Complexity Inversion:** As schema complexity increases, the benefit of multi-pass reasoning becomes exponential for small models.
2.  **Structural Bias:** LLMs have a strong structural bias toward TypeScript/C-style declarations over verbose JSON-LD or JSON Schema.
3.  **Grounding vs. Generation:** The "Strict Extract-or-Null" rule is the single most important prompt component for maintaining high precision in zero-shot scenarios.

## Recommendations
1.  **Implement Schema-Aware Analysis:** Update `TwoPassAgent` to include the compressed TS schema in Pass 1.
2.  **Unify Invariants:** Apply the `InvariantPromptMixin` to the `EndAnchoredAgent` and `BasicAgent`.
3.  **Hybrid Scaffolding:** Experiment with passing the Pass 1 analysis as "JSON comments" within the Pass 2 template to provide a stronger reasoning-to-structure bridge.
4.  **Final Suggestion:** The research is complete. You can now use the `/draft` command to turn this executive report into a fully fleshed-out system description paper for IberLEF 2026.
