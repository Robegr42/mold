# Research Report: Gated vs. Stable Champion Agent Comparison

## Executive Summary
This report compares the **StableChampionAgent** and the **GatedStableChampionAgent** using the **Qwen 3 1.7B** model on the `data/starter` dataset. The experiment aimed to verify if a **0.65 RAG Similarity Gate** could protect the model from "Negative Transfer" caused by irrelevant retrieved examples. 

**Key Findings:**
1.  **Stable Agent Wins on Performance:** The `StableChampionAgent` achieved a Micro-F1 of **0.7585**, outperforming the Gated agent's **0.7408** (-2.3%).
2.  **Gated Agent Wins on Token Efficiency:** The gating mechanism successfully reduced average token consumption by **2.1%** by pivoting to Zero-Shot mode for 10% of the tasks.
3.  **Threshold Sensitivity:** For this specific SLM (Qwen 3 1.7B), "noisy" RAG examples proved more beneficial than none at all. The 0.65 threshold may be too conservative for small models that require heavy structural grounding.
4.  **Error Trade-offs:** Gating successfully reduces schema-drift hallucinations but increases information omissions (Recall drop).

## Research Questions

### 1. RQ1: Quantitative Extraction Performance
The `StableChampionAgent` demonstrated superior performance across Micro-F1, Precision, and Recall. This suggests that the current starter dataset contains few "truly toxic" OOD examples that would justify a hard gating strategy at 0.65.
- **Detailed Asset:** [rq1_quantitative_performance.md](gated_vs_stable_comparison/rq1_quantitative_performance.md)

### 2. RQ2: Efficiency and Cost-to-Performance Analysis
The `GatedStableChampionAgent` is the more token-efficient architecture, saving significant overhead when RAG is disabled. However, the slightly longer execution time and lower F1 score results in a nearly identical Performance-to-Cost (PTC) ratio (~0.132).
- **Detailed Asset:** [rq2_efficiency_analysis.md](gated_vs_stable_comparison/rq2_efficiency_analysis.md)

### 3. RQ3: Qualitative Robustness and Error Analysis
The 0.65 Similarity Gate is technically sound and triggers appropriately for tasks with low semantic overlap (e.g., specific Legal/Technical sub-domains). The "Zero-Shot Pivot" is a viable fallback strategy, but it requires a more robust "Generalization Directive" or synthetic few-shots to match the performance of RAG-enabled runs.
- **Detailed Asset:** [rq3_robustness_analysis.md](gated_vs_stable_comparison/rq3_robustness_analysis.md)

## Conclusions
The **GatedStableChampionAgent** provides a robust safety mechanism for out-of-distribution (OOD) scenarios but incurs a small performance penalty on "near-distribution" tasks where noisy RAG is still helpful. For the `qwen/qwen3-1.7b` model, the grounding provided by few-shot examples—even imperfect ones—is a critical driver of accuracy. The gating strategy is technically successful but requires threshold tuning based on the specific SLM's zero-shot capabilities.

## Recommendations

### 1. Tune the Gate Threshold
Lower the RAG Similarity Gate from **0.65 to 0.55**. Our data suggests that the model still gains more from low-similarity examples than it loses to negative transfer at the 0.60 range.

### 2. Implement "Architect Few-Shot" Fallback
Instead of pivoting to a pure Zero-Shot mode when the gate triggers, instruct the `ArchitectModule` to generate 1-2 **synthetic few-shot examples** based on the schema. This would provide the structural grounding the SLM needs without the risk of noise from irrelevant real examples.

### 3. Cross-Model Validation
Run this same comparison on **Llama 3.2 3B** and **Gemma 4 E4B**. Larger or more instruction-tuned models might show a greater performance uplift from the 0.65 gate than the 1.7B Qwen model.

### 4. Hybrid Selection
Consider a "Soft Gate" where the agent uses RAG examples but with a modified prompt that explicitly warns the model: *"Note: These examples are semantically distant. Prioritize the current schema over the example structure."*

---
*Research complete. Use the `/draft` command to turn this report into a publication-ready document.*
