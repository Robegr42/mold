# Llama 3.2 3B Holistic Impact (All Invariants)

## 1. Holistic vs. Baseline vs. Best Invariant
Comparison of applying ALL invariants simultaneously against the No-Invariant (NI) baseline and the best performing individual component discovered in the ablation study.

| Agent | NI Baseline | Best Individual | Full Invariants | Delta (Full vs NI) |
| :--- | :--- | :--- | :--- | :--- |
| Grounded | 0.4881 | 0.5969 (Null) | 0.4957 | +1.5% |
| Auditor | 0.5302 | 0.5712 (TS) | 0.5622 | +6.0% |
| End-Anchored | 0.6179 | 0.6179 (NI) | 0.5961 | **-3.5%** |
| Two-Pass | 0.5977 | 0.6011 (Null) | 0.5528 | **-7.5%** |

## 2. The Over-Optimization Trap
For Llama 3.2 3B, applying the full invariant suite is a **sub-optimal strategy** across all architectures.

- **Synergy Failure:** Invariants do not stack positively. In the Grounded agent, the 22% gain from the Null Rule is almost entirely wiped out when TS and Dialect rules are added.
- **Auditor Stability:** The Auditor is the only agent where holistic invariants remain relatively close to the peak (+6.0% vs baseline), though still lower than TS Schema alone (+7.7%).
- **Degradation of Advanced Agents:** Both End-Anchored and Two-Pass agents see significant regressions with holistic invariants.

## 3. Comparison with previous findings
The initial `invariants_impact_report.md` suggested broad benefits for Grounded and Auditor. This more granular ablation reveals that those benefits were primarily driven by **single components** (Null Rule for Grounded, TS Schema for Auditor) rather than the suite as a whole.
