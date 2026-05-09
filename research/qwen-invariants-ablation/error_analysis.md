# RQ4: Error Profile & Hallucination Analysis

## 1. Shift in Error Modes
Unlike the Llama experiment where invariants primarily suppressed hallucinations, for Qwen3-1.7b, invariants (specifically the Null and Dialect rules) acted as **Coherence Boosters**.

| Configuration | Hallucination Frequency | Missing Field Frequency | Micro-F1 Impact |
| :--- | :--- | :--- | :--- |
| **No Invariants** | High (in nested arrays) | Moderate | Baseline |
| **Best Invariant** | Moderate (Reduced) | Low (Significant Reduction) | **Positive (Recall Gain)** |
| **Full Invariants** | High (Resurgence) | Moderate | **Negative (Overload)** |

## 2. Key Observations
- **Recall Gains:** For the Auditor agent, the Null Rule increased Recall from **0.5029 to 0.6138 (+11%)**. This indicates that the rule didn't just suppress wrong info; it helped the model focus on finding the correct info by providing a clearer logical framework.
- **Label Normalization:** The Dialect Rule significantly improved entity labeling similarity scores. By acknowledging Iberian/Latin American differences, the model stayed closer to the schema's terminology, reducing `sim=0.00` errors on rigid labels.
- **Hallucination Resilience:** Qwen 1.7B is naturally prone to "filling the schema" when it gets confused. Single invariants successfully "ground" the model, but full invariants recreate the confusion, leading to a resurgence of hallucinated keys in nested structures.

## 3. Architecture-Specific Shifts
- **End-Anchored:** Showed the best balance. The "Null Rule" + "Anchored Template" created a very high-precision environment (**Precision 0.6896**) with the highest recall in the study (**0.6584**).
- **Auditor:** The audit step became significantly more effective at recovering missing data when the Dialect Rule was provided, suggesting the "red pen" audit is more about semantic matching than strict verification for Qwen.
