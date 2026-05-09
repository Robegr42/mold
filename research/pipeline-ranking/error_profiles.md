# RQ4: Error Mode Suppression Profiles

## 1. Top-Ranked Error Profiles
Comparison of the error modes between the model-specific winners.

| Model / Winner | Hallucinations | Missing Fields | Value Drift (Low Sim) |
| :--- | :--- | :--- | :--- |
| **Qwen / Grounded-Null** | **Low** | Low | High (Label categorization) |
| **Llama / End-Anchored-Null** | Moderate | **High** | High (Semantic drift) |

## 2. Qualitative Observations
- **Qwen's Precision:** The combination of `Grounded` (source quotes) and `Null Rule` makes Qwen 1.7B a precision powerhouse. It rarely invents data, and when it fails, it's usually because it couldn't perfectly match a schema label (e.g. `sim=0.35`).
- **Llama's Caution:** `End-Anchored-Null` on Llama 3B is highly conservative. It prefers to leave fields as `null` (high Missing frequency) rather than risk a hallucination. This is the desired behavior for GenSIE, but it explains the lower F1 compared to Qwen.
- **Auditor's Complexity Gap:** The `Auditor-Dialect` pipeline (consistently 4th) suffers from "Over-Correction". In these very small models, the auditor pass often deletes valid data from the draft pass because it fails to semantic-match the evidence correctly, leading to high Missing Field counts without improving Precision enough to compensate.

## 3. Generalization Verdict
The **Null Rule** is the universal error suppressor for SLMs. Whether applied via `Grounded` or `End-Anchored`, it is the single most effective tool for transforming a hallucinating model into a reliable extractor.
