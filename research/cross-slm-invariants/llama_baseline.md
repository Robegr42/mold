# Llama 3.2 3B Baseline Performance (No Invariants)

## 1. Quantitative Metrics (Llama 3B)
Baseline performance on `data/starter/` using `meta-llama/llama-3.2-3b-instruct` without prompt invariants.

| Agent | Precision | Recall | Micro-F1 |
| :--- | :--- | :--- | :--- |
| **Grounded-NI** | 0.5283 | 0.4537 | 0.4881 |
| **Auditor-NI** | 0.5825 | 0.4865 | 0.5302 |
| **End-Anchored-NI** | 0.6582 | 0.5822 | 0.6179 |
| **Two-Pass-NI** | 0.6152 | 0.5812 | 0.5977 |

## 2. Key Observations
- **End-Anchored Superiority:** For Llama 3B, the End-Anchored strategy is the strongest baseline, slightly outperforming the Two-Pass strategy.
- **Lower Ceiling:** Compared to Qwen 1.7B, Llama 3B has a lower performance ceiling across almost all agents (except End-Anchored where they are nearly tied).
- **Two-Pass Efficiency:** The Two-Pass agent shows lower precision than End-Anchored on Llama 3B, suggesting the first pass reasoning might be introducing semantic drift rather than clarifying the task.
