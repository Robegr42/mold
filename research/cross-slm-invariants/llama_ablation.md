# Llama 3.2 3B Ablation Study - Component Impact

## 1. Summary of Individual Invariant Impact (Micro-F1)
Absolute Micro-F1 scores and relative change compared to the NI (No Invariant) baseline.

| Agent | NI (Base) | TS Schema Delta | Null Rule Delta | Dialect Rule Delta |
| :--- | :--- | :--- | :--- | :--- |
| **Grounded** | 0.4881 | -0.0262 (-5.4%) | +0.1088 (+22.3%)| +0.0846 (+17.3%)|
| **Auditor** | 0.5302 | +0.0410 (+7.7%) | -0.0010 (-0.2%) | -0.0014 (-0.3%) |
| **End-Anchored**| 0.6179 | -0.0264 (-4.3%) | -0.0010 (-0.2%) | -0.0219 (-3.5%) |
| **Two-Pass** | 0.5977 | -0.0356 (-5.9%) | +0.0034 (+0.6%) | -0.0536 (-9.0%) |

## 2. Key Findings
- **Grounded Agent Transformation:** Llama 3B's Grounded agent is completely transformed by the logical rules. The **Null Rule** provides a massive **22.3% boost**, essentially moving it from a weak agent to one of the strongest.
- **Auditor Structural Preference:** Unlike the other agents, the Auditor specifically benefits from the **TS Schema compression (+7.7%)**, while logical rules have a negligible or slightly negative impact.
- **Invariants as Noise for Optimized Agents:** For End-Anchored and Two-Pass (the strongest baselines), almost every individual invariant acted as performance-degrading noise. This suggests that these architectures are already "at capacity" for prompt complexity in a 3B model.
- **Dialect Rule Inconsistency:** While the Dialect rule was a major booster for Qwen, it is a significant regression for Llama 3B's Two-Pass agent (-9%).
