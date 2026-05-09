# Scale Sensitivity to Prompt Invariants (1.7B vs 3B)

## 1. Baseline Extraction Capacity
The 1.7B Qwen model consistently outperforms the 3B Llama model in zero-shot structured extraction (NI configuration). This suggests that **training quality and architectural efficiency** (Qwen 3.0 vs Llama 3.2) are more important than parameter scale in the sub-5B range for GenSIE tasks.

| Agent Architecture | Scale Delta (3B vs 1.7B F1) | Sensitivity to Invariants |
| :--- | :--- | :--- |
| **Grounded** | -9.8% (Llama 3B is worse) | **Llama** (Massive gain from Null Rule) |
| **Auditor** | -2.0% (Nearly tied) | **Qwen** (Massive gain from Dialect Rule) |
| **End-Anchored**| -0.1% (Tied) | **Qwen** (Strong gain from Null Rule) |
| **Two-Pass** | -16.5% (Qwen dominates) | **Qwen** (Catastrophic regression from TS Schema) |

## 2. Attention Dilution (Prompt Overload)
Both models show a clear **Attention Dilution** effect when all invariants are applied, but the mechanism differs:

- **1.7B Sensitivity (Qwen):** The smallest model is sensitive to **token noise**. Complex TS schema interfaces (the "TS" invariant) distract the model from the reasoning task, causing massive regressions in Two-Pass.
- **3B Sensitivity (Llama):** The slightly larger model is sensitive to **instruction conflict**. Adding Dialect rules and TS schemas alongside strict Null rules causes the model to "hedge" its bets, diluting the massive benefit of the single Null Rule in Grounded agents.

## 3. Generalization for <14B Models
As models scale toward 7B and 14B, we expect:
1. **Higher Tolerance for Holistic Invariants:** Larger models will likely show the "synergy" we failed to see in the <3B range.
2. **Diminishing Returns from Logical Rules:** The "Null Rule" and "Dialect Rule" are essentially compensatory mechanisms for weak base capability. Larger models (like Qwen3-14B) should internalize these concepts natively, making the invariants redundant or purely formal.
