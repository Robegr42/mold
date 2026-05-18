# RQ2: Efficiency and Cost-to-Performance Analysis

## Executive Summary
This report analyzes the resource efficiency of the `StableChampionAgent` vs. `GatedStableChampionAgent`. The Gated agent demonstrated a slight reduction in token usage due to its "Zero-Shot Pivot," but this did not translate into a higher Performance-to-Cost (PTC) ratio due to the slight drop in F1 score.

## Efficiency Metrics

| Metric | StableChampionAgent | GatedStableChampionAgent | Delta (Gated vs Stable) |
| :--- | :--- | :--- | :--- |
| **Avg Tokens/Task** | 5,728 | **5,607** | -2.11% |
| **Avg Time/Task** | **22.06s** | 22.53s | +2.13% |
| **Micro-F1** | **0.7585** | 0.7408 | -2.33% |
| **PTC (F1 / kTokens)** | **0.1324** | 0.1321 | -0.23% |

## Detailed Analysis

### 1. Token Consumption
The **GatedStableChampionAgent** consumed ~2% fewer tokens on average. This is directly attributable to the 0.65 similarity gate, which removed few-shot RAG examples from the prompt in approximately 10% of the tasks (4 out of 40). In those specific tasks, token usage dropped by 50-70%.

### 2. Execution Time
Despite lower token counts in some tasks, the Gated agent was slightly slower on average (2.1%). This suggests that "Zero-Shot" reasoning (Pass 1) for this model might be more computationally expensive (generating more "thought" tokens) or prone to longer generation times when it lacks the structural grounding of few-shot examples.

### 3. Performance-to-Cost (PTC) Ratio
The PTC ratio is nearly identical (0.1324 vs 0.1321). While the Gated agent saves money on tokens, the loss in F1 score nullifies the efficiency gain. For the Qwen 3 1.7B model, the Stable agent remains the slightly more "efficient" choice when prioritizing performance per dollar.

## Conclusion
The **GatedStableChampionAgent** successfully reduces token overhead in out-of-distribution (OOD) scenarios. However, for the current `data/starter` distribution, the `StableChampionAgent` provides a slightly better balance of speed and accuracy. The Gated architecture is likely to show its true value in more diverse or "messier" datasets where irrelevant RAG noise is more frequent.
