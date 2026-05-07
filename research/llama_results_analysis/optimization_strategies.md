# Optimization Strategies: Improving F1 without New Components

## 1. Schema-Aware Analysis (Two-Pass)
Currently, `TwoPassAgent` performs a generic analysis in Spanish.

### Proposal:
*   Pass 1 should receive the (TS compressed) schema.
*   The system prompt for Pass 1 should be updated from "Analyze the text step-by-step" to "Identify all entities and facts required by the provided schema."
*   **Result:** The analysis will be targeted. Instead of general summary, it will produce a list of "raw findings" that directly map to the schema fields, making Pass 2 almost a purely mechanical mapping task.

## 2. Hybridizing Two-Pass and End-Anchored
The failure of `end-anchored` is due to the lack of reasoning. The success of `two-pass` is due to reasoning.

### Proposal:
*   In Pass 2 of the `TwoPassAgent`, use the `format_end_anchored_prompt` structure but replace the generic `blank_template` with a "hinted template".
*   If the analysis identifies a symptom, put it in the template as a comment: `"symptoms": [/* Found: fiebre, tos */]`.
*   **Result:** This gives the model a strong "scaffold" to follow, combining the reasoning of two-pass with the structural guidance of end-anchored.

## 3. Standardizing the `InvariantPromptMixin`
Currently, `BasicAgent` and `EndAnchoredAgent` do not use the invariants.

### Proposal:
*   Apply the `InvariantPromptMixin` to ALL agents.
*   Specifically, `EndAnchoredAgent` could benefit from the TS schema representation instead of the raw JSON schema it currently uses in its delimiter sections.

## 4. Fine-Tuning the "Strict" Mode
OpenAI's `json_schema` with `strict: True` is a double-edged sword for SLMs.

### Observations:
*   It ensures valid JSON, but if the model is "confused" by the schema vs the text, it might fail to generate anything or fallback to an error.
*   **Optimization:** Ensure the `instruction` and `analysis` in the prompt are extremely clear about the "Null Rule", so the model doesn't feel it must invent data to satisfy the `strict` schema requirements (which often mandate that certain properties be present).
