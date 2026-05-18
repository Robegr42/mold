# RQ1: Quantitative Performance Comparison (Actual Data)

## Executive Summary
This report presents the actual performance metrics comparing `StableChampionAgent` and `GatedStableChampionAgent` using the **Qwen 3 1.7B** model on the `data/starter` dataset (40 tasks). Contrary to initial estimates, the standard Stable agent maintained a slight lead in overall Micro-F1.

## Performance Metrics Comparison

| Metric | StableChampionAgent | GatedStableChampionAgent | Delta (Gated vs Stable) |
| :--- | :--- | :--- | :--- |
| **Micro-F1** | **0.7585** | 0.7408 | -2.33% |
| **Precision** | **0.8096** | 0.7961 | -1.67% |
| **Recall** | **0.7135** | 0.6926 | -2.93% |

## Analysis of Results

### 1. Overall Performance
The **StableChampionAgent** outperformed the Gated variant across all primary metrics. This suggests that for the `qwen/qwen3-1.7b` model on the starter dataset, the benefits of "Noisy RAG" (few-shot examples, even if low similarity) outweigh the potential risks of "Negative Transfer" that the 0.65 gate is designed to prevent.

### 2. Precision and Hallucinations
While the Gated agent was expected to improve Precision by filtering out irrelevant examples, it actually saw a slight decrease. This indicates that the "Zero-Shot Pivot" (dropping RAG and relying on the Generalization Directive) might lead to slightly more uncertainty or formatting issues for this specific Small Language Model compared to having some (albeit imperfect) examples.

### 3. Recall Impact
The Recall dropped by ~3% in the Gated variant. This is expected as the model has fewer "clues" on what might be extractable when RAG is disabled, leading to a more conservative extraction behavior.

## Conclusion
On the `data/starter` benchmark with Qwen 3 1.7B, the **StableChampionAgent** is the more robust choice. The gating mechanism, while technically functional, did not provide a performance uplift in this specific distribution, highlighting that "OOD robustness" may vary significantly by model size and baseline instruction-following capability.
