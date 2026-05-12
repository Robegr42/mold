# Final Experimental Synthesis Report: Cross-Model Information Extraction

## Executive Summary
This report synthesizes the results of a comprehensive cross-model extraction experiment involving three Small Language Models (SLMs): **Llama 3.2 3B**, **Qwen 3 1.7B**, and **Gemma 4 E4B**. The goal was to identify optimal architectural strategies for structured data extraction in a bilingual (Spanish/English) context.

The experiment evaluated five primary architectures: **Two-Pass**, **Grounded**, **Auditor**, **End-Anchored**, and the **Champion** series (Stable and Slim).

## 1. Quantitative Performance Analysis

### 1.1 Model Performance Overview
Across all experiments, the models demonstrated significant variance in their ability to follow complex extraction instructions:
- **Qwen 3 1.7B**: Paradoxically showed the highest peak performance (F1: 0.7972) when paired with the Stable-Champion pipeline.
- **Gemma 4 E4B**: Demonstrated high stability and strong baseline performance (F1: 0.7799 - 0.7971).
- **Llama 3.2 3B**: Performed well but lagged behind the others in structured output consistency (Peak F1: 0.6965).

### 1.2 Impact of Architectural Invariants
The "Invariants" (TypeScript Schema, Null-Rule, Dialect-Awareness) had a dual impact:
- **Positive**: The **Null-Rule** (Extract-or-Null) was universally beneficial, reducing hallucinations across all models.
- **Negative**: For non-RAG strategies, the combination of **TypeScript Schema** and **Dialect Rules** often led to "instruction bloat," which confused SLMs. The **"ni" (No Invariants)** or **"null" (Null-Rule only)** variants frequently outperformed the "full" invariant versions for simpler architectures.

---

## 2. Top 3 Generalizing Strategies
These strategies showed the highest F1 scores and strongest stability across all three test models.

1.  **Stable-Champion**
    - **Components**: RAG (k=3), Two-Pass Reasoning, Null-Rule Invariant.
    - **Why it works**: It provides necessary context via RAG while decoupling cognitive analysis (Pass 1) from syntax-heavy JSON formatting (Pass 2). By using only the Null-Rule invariant, it avoids overwhelming the model's limited context window.
2.  **Two-Pass (Pure)**
    - **Components**: Analysis (Spanish) -> Structured Extraction.
    - **Why it works**: Even without RAG, the "thought process" pass allows the model to map the input text to the target schema mentally before committing to a JSON structure.
3.  **Grounded**
    - **Components**: Evidence-based auditing (mandatory source quotes).
    - **Why it works**: It forces the model to verify every claim against the input text, which is particularly effective for SLMs prone to "filling the gaps" with hallucinations.

---

## 3. Top 3 Non-RAG Strategies
Strategies that achieve high structural accuracy without the overhead of a retrieval system.

| Strategy | Top Model | F1 Score |
| :--- | :--- | :--- |
| **Two-Pass (-ni / -null)** | Qwen 3 1.7B | **0.7190** |
| **Grounded (-null)** | Qwen 3 1.7B | **0.7055** |
| **End-Anchored (-null)** | Qwen 3 1.7B | **0.6737** |

*Note: F1 scores are derived from the best performing model/variant combination.*

---

## 4. Recommendations for SLM Extraction

### Why these strategies work for SLMs:
1.  **Cognitive Decoupling**: SLMs struggle to reason and format simultaneously. Two-Pass architectures solve this by splitting the task.
2.  **Contextual Anchoring**: RAG provides high-quality examples that act as "in-context weights," steering the model toward the correct output format.
3.  **Constraint Optimization**: SLMs have a "complexity ceiling." Using minimal, high-impact invariants (like the Null-Rule) is more effective than exhaustive prompt engineering.

### Prototypical 'Universal Extraction Strategy':
Based on the data, the most robust "Universal Strategy" for SLMs is:
1.  **Input Augmentation**: Use a RAG module to fetch 2-3 semantically similar examples.
2.  **Reasoning Pass**: Ask the model to analyze the text in its most "comfortable" language (Spanish in this case) and list evidence quotes.
3.  **Extraction Pass**: Perform the final JSON extraction using the reasoning from step 2, enforced by a strict **Null-Rule** (return null if information is missing).
4.  **Schema Formatting**: Use standard JSON Schema instead of TypeScript interfaces to reduce token noise.

---
*End of Report*
