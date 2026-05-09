# RQ3: Performance-to-Cost (P2C) Ratio

## 1. Efficiency Data
Average tokens per task across all successful evaluations on the starter dataset.

| Pipeline | Avg Tokens (Qwen) | Avg Tokens (Llama) | Combined Avg | Performance (Combined F1) |
| :--- | :--- | :--- | :--- | :--- |
| **Grounded-Null** | **903** | **863** | **883** | 0.6512 |
| **Auditor-Dialect**| 1398 | 1379 | 1389 | 0.5793 |
| **End-Anchored-Null**| 1358 | 1354 | 1356 | 0.6453 |
| **Two-Pass-NI** | 1908 | 1671 | 1790 | 0.6472 |

## 2. Efficiency Ranking
1. **`Grounded-Null` (Efficiency Champion):** Lowest token usage (nearly 50% less than Two-Pass) while maintaining Tier-1 performance.
2. **`End-Anchored-Null`:** Moderate efficiency.
3. **`Two-Pass-NI`:** Most expensive in terms of tokens due to the analytical pass.

## 3. Verdict
If cost/latency is a priority, **`Grounded-Null`** is the clear winner for SLMs. It delivers Tier-1 accuracy with the lowest possible computational footprint. **`Two-Pass-NI`** is reliable but requires significantly more context and time.
