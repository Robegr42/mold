# Efficiency and Cost Analysis: GenSIE with Llama 3.2 3B

## 1. Quantitative Performance Overview
Based on the `eval2` results, we calculated the "F1-per-1k-tokens" ratio to measure the economic viability of each pipeline.

### Starter Dataset
| Pipeline | F1 | Avg Tokens | Avg Time (s) | F1 / 1k Tokens |
| :--- | :---: | :---: | :---: | :---: |
| **Grounded** | 0.5267 | 486.40 | 1.63 | **1.0829** |
| **Baseline** | 0.4910 | 480.03 | 1.27 | 1.0229 |
| **End-Anchored**| 0.5998 | 880.48 | 2.27 | 0.6812 |
| **Auditor** | 0.5889 | 1027.83| 5.29 | 0.5729 |
| **Two-Pass** | 0.5679 | 1388.63| 7.81 | 0.4089 |

### Dev Dataset
| Pipeline | F1 | Avg Tokens | Avg Time (s) | F1 / 1k Tokens |
| :--- | :---: | :---: | :---: | :---: |
| **Grounded** | **0.5531** | 1006.90| 3.22 | **0.5493** |
| **Baseline** | 0.5185 | 1001.28| 3.29 | 0.5178 |
| **End-Anchored**| 0.4794 | 1576.14| 3.81 | 0.3042 |
| **Auditor** | 0.4706 | 1961.15| 7.95 | 0.2400 |
| **Two-Pass** | 0.5248 | 2638.86| 12.71| 0.1989 |

## 2. Key Findings

### The "Grounded" Efficiency Breakthrough
The `GroundedAgent` emerged as the most cost-effective strategy. On the `Dev` set, it achieved the highest absolute F1 (0.5531) while using ~62% fewer tokens and being ~4x faster than the `Two-Pass` agent. This suggests that for SLMs like Llama 3.2 3B, **single-turn verification** (mandating source quotes) is superior to **multi-turn reasoning** (two-pass).

### The "Reasoning Tax"
The `Two-Pass` and `Auditor` strategies carry a heavy "Reasoning Tax." 
*   `Two-Pass` on `Dev` averages 2,638 tokens per task.
*   The execution time jumps to 12.7 seconds.
*   Despite this investment, the F1 (0.5248) is lower than the single-pass `Grounded` agent. This indicates that for Llama 3.2 3B, the quality of "Pass 1 Analysis" might be too low to justify the token cost, or the model is "confused" by its own verbosity.

### Attention Drift in End-Anchored
The `End-Anchored` strategy shows poor scaling. While it performs well on simple schemas (Starter), its efficiency drops by half on Dev. The increased token count (from 880 to 1576) reflects the larger blank templates required for hierarchical schemas, which consumes the model's limited attention window without contributing to reasoning.

## 3. Correlation between Time and TPS
Higher execution time generally correlates with **lower** efficiency (TPS/Token). There is a clear "efficiency plateau" for Llama 3.2 3B around the 1,000-token mark. Beyond this, gains in F1 are marginal or even negative, as seen in the `Auditor` pipeline which has lower F1 than `Baseline` on `Dev` despite double the token usage.

## 4. Recommendations for Resource Optimization
*   **Favor Grounded Single-Pass:** Mandating source quotes within a single structured prompt provides the best grounding-to-cost ratio.
*   **Reduce Multi-Pass Latency:** If multi-pass is required, the "Analysis" pass should be constrained to a bulleted list of facts rather than a full conversational summary.
*   **Avoid Large Templates:** The `end-anchored` template generation should be pruned to only include mandatory fields to save tokens and attention.
