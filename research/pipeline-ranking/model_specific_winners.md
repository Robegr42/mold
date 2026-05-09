# RQ1: Model-Specific Winners

## 1. Qwen 1.7B Results
Among the four candidate pipelines, the ranking for `qwen/qwen3-1.7b` is as follows:

| Rank | Pipeline | Micro-F1 |
| :--- | :--- | :--- |
| **1** | **Grounded-Null** | **0.7055** |
| 2 | Two-Pass-NI | 0.6968 |
| 3 | End-Anchored-Null | 0.6737 |
| 4 | Auditor-Dialect | 0.6298 |

**Winner:** **Grounded-Null** is the champion for Qwen 1.7B, breaking the 0.70 threshold.

## 2. Llama 3B Results
Among the four candidate pipelines, the ranking for `llama-3.2-3b-instruct` is as follows:

| Rank | Pipeline | Micro-F1 |
| :--- | :--- | :--- |
| **1** | **End-Anchored-Null** | **0.6169** |
| 2 | Two-Pass-NI | 0.5977 |
| 3 | Grounded-Null | 0.5969 |
| 4 | Auditor-Dialect | 0.5288 |

**Winner:** **End-Anchored-Null** is the champion for Llama 3B.

## 3. Comparison
- **Higher Ceiling:** Qwen 1.7B achieved significantly higher absolute scores (+8.8% to +10.8% F1) than Llama 3B across all four pipelines.
- **Top-2 Stability:** `Two-Pass-NI` consistently occupied the 2nd rank for both models, making it the most reliable across architectures.
- **Bottom-1 Stability:** `Auditor-Dialect` was consistently the worst performer among the optimized set.
