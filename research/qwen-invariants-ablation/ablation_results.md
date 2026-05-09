# RQ2: Ablation Study - Component Impact Analysis

## 1. Summary of Individual Invariant Impact (F1 Delta)
This table shows the absolute Micro-F1 scores and the relative change compared to the NI (No Invariant) baseline for each component.

| Agent | NI (Base) | TS Schema Delta | Null Rule Delta | Dialect Rule Delta |
| :--- | :--- | :--- | :--- | :--- |
| **Grounded** | 0.5359 | -0.0005 (-0.1%) | -0.0015 (-0.3%) | +0.0000 (0%) |
| **Auditor** | 0.5411 | +0.0399 (+7.4%) | +0.0815 (+15.1%)| +0.0887 (+16.4%)|
| **End-Anchored**| 0.6189 | +0.0356 (+5.8%) | +0.0548 (+8.9%) | +0.0478 (+7.7%) |
| **Two-Pass** | 0.6968 | -0.1471 (-21%) | -0.0124 (-1.8%) | -0.0058 (-0.8%) |

## 2. Key Findings
- **Two-Pass Sensitivity:** The Two-Pass agent is extremely sensitive to prompt noise in its first (reasoning) pass. Adding the TS Schema compression caused a catastrophic **21% drop in F1**. Logical invariants (Null/Dialect) also slightly hindered the reasoning phase.
- **Component Efficacy:** The **Dialect Awareness Rule** and the **Extract-or-Null Rule** are the most powerful components for Qwen3-1.7b, specifically for multi-pass (Auditor) and prompt-optimized (End-Anchored) strategies.
- **Auditor Sensitivity:** The Auditor agent saw a massive **16.4% F1 increase** simply by adding the Dialect Awareness rule. This suggests the second-pass audit is highly sensitive to semantic hints.
- **Grounded Fragility:** The Grounded agent is virtually unaffected or slightly penalized by individual invariants. This architecture's internal constraint (source quotes) may already be at the model's "logic limit," and additional prompt constraints add no value or introduce noise.
- **TS Schema Impact:** TypeScript schema compression is beneficial for Auditor and End-Anchored agents but less impactful than the logical rules (Null/Dialect).

## 3. Recommendation per Component
- **Null Rule:** Retain for Auditor and End-Anchored.
- **Dialect Rule:** Retain for Auditor and End-Anchored.
- **TS Schema:** Retain for End-Anchored (provides structural stability).
