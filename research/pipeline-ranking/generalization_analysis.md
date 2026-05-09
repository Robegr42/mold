# RQ2: Model-Independent Pipeline Hierarchy

## 1. Generalization Matrix
Is it possible to rank these pipelines independently of the model?

| Pipeline | Qwen Rank | Llama Rank | Avg Rank | Variance |
| :--- | :--- | :--- | :--- | :--- |
| **Two-Pass-NI** | 2 | 2 | **2.0** | 0.0 |
| **Grounded-Null** | 1 | 3 | **2.0** | 2.0 |
| **End-Anchored-Null**| 3 | 1 | **2.0** | 2.0 |
| **Auditor-Dialect** | 4 | 4 | **4.0** | 0.0 |

## 2. Qualitative Hierarchy
Based on the average rank and the absolute performance:

1. **The Reliable Strategist: `Two-Pass-NI`**
   - Consistent 2nd place.
   - High performance ceiling.
   - Most robust across parameter scales (1.7B and 3B).

2. **The Specialized High-Performers: `Grounded-Null` and `End-Anchored-Null`**
   - Both can take 1st place depending on the model scale.
   - `Grounded-Null` thrives on 1.7B (where precision gating is key).
   - `End-Anchored-Null` thrives on 3B (where template structural following is more robust).

3. **The Underperformer: `Auditor-Dialect`**
   - Consistently 4th.
   - The multi-pass overhead with semantic rules likely creates too many opportunities for attention dilution on these very small SLMs.

## 3. Verdict
**Yes**, we can establish a stable hierarchy:
- **Tier 1:** `Two-Pass-NI`, `Grounded-Null`, `End-Anchored-Null` (Interchangeable for top spots).
- **Tier 2:** `Auditor-Dialect`.

For a truly model-independent recommendation, **`Two-Pass-NI`** is the safest bet due to zero rank variance.
