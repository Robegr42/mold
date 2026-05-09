# Universal Invariant Guidelines for SLMs (<14B)

## 1. The "Rule of One" for Sub-5B Models
For models between 1B and 5B parameters (Qwen 1.7B, Llama 3B), **never apply more than one logical prompt invariant at a time**.
- **Observation:** Both tested models showed performance peaks with single invariants and consistent regressions when combining them.
- **Action:** Select the single invariant that matches the agent's architecture (see below).

## 2. Architecture-Invariant Binding Matrix
The following table provides the recommended invariant configuration based on agent architecture for SLMs < 14B.

| Architecture | Recommended Invariant | Expected Primary Benefit |
| :--- | :--- | :--- |
| **Grounded** | **Extract-or-Null** | Massive Precision & Recall boost (up to +22% F1). |
| **Auditor** | **Dialect Awareness** | Semantic alignment during the audit pass. |
| **End-Anchored**| **Extract-or-Null** | Coherence anchor for anchored JSON templates. |
| **Two-Pass** | **No Invariants** | Preserve reasoning context in Pass 1. |

## 3. Structural Guidelines (TS vs. JSON)
- **Small SLMs (<2B):** Prefer standard, verbose **JSON Schema**. Compressed TS schemas appear to create token noise that hinders reasoning.
- **Medium SLMs (3B - 14B):** Prefer **TypeScript Interfaces** (Compressed). These models have enough attention heads to leverage the brevity of TS to focus on extraction.

## 4. Predicting 14B Behavior
Based on the trend from 1.7B to 3B, we project that 14B models (e.g., Qwen3-14B) will be the first scale to benefit from **Holistic Invariants**. 
- They should possess the context density to handle 3+ logical rules simultaneously without attention dilution.
- At this scale, invariants transition from "compensatory tools" to "efficiency formalisms".
