# RQ2: Efficiency and Cost-to-Performance Analysis

## Executive Summary
This report evaluates the resource efficiency of three extraction architectures. The `StableChampionAgent` provides the best value, achieving the highest Performance-to-Cost (PTC) ratio (0.1324). The `SyntheticAnchorAgent`, while improving accuracy over the gated baseline, is the most resource-intensive due to the overhead of the dynamic synthesis pass.

## Efficiency Metrics Comparison

| Metric | StableChampionAgent | GatedStableChampionAgent | SyntheticAnchorAgent | Best Performer |
| :--- | :---: | :---: | :---: | :---: |
| **Avg Tokens / Task** | 5,728 | **5,607** | 5,739 | GatedStable |
| **Avg Latency / Task** | **22.06s** | 22.53s | 22.92s | StableChampion |
| **Micro-F1** | **0.7585** | 0.7408 | 0.7439 | StableChampion |
| **PTC Ratio (F1/kTok)** | **0.1324** | 0.1321 | 0.1296 | StableChampion |

## Detailed Analysis

### 1. The "Synthesis Tax"
The `SyntheticAnchorAgent` consumes ~2.3% more tokens than the `GatedStableChampionAgent`. This is the cost of the "synthesis pass" where the model generates a structural anchor. Because this pass is a separate inference call, it also increases average latency by ~1.7%. 

### 2. Token Savings vs. Accuracy Loss
The `GatedStableChampionAgent` achieves the lowest token consumption by pruning RAG examples when similarity is low. However, the resulting drop in F1 (from 0.7585 to 0.7408) nullifies the cost savings, leading to a lower PTC ratio than the non-gated agent.

### 3. Performance-to-Cost (PTC) Ranking
1. **StableChampionAgent (0.1324):** The baseline is surprisingly efficient. By including all RAG examples (even noisy ones), it maximizes F1 without requiring extra synthesis steps.
2. **GatedStableChampionAgent (0.1321):** Offers a slight token saving but at a visible accuracy cost.
3. **SyntheticAnchorAgent (0.1296):** Focuses on "high-fidelity" extraction at the expense of efficiency. This agent is optimized for the **Performance Leaderboard**, not the Efficiency Leaderboard.

## Conclusion
If the goal is to maximize the **Efficiency Leaderboard** (PTC Ratio), the **StableChampionAgent** is currently the best choice. The `SyntheticAnchorAgent` provides a "harden" architecture that recovers precision, but the current implementation's synthesis pass is too expensive to be cost-competitive in the current distribution.
