# Research Asset: Qualitative Mechanism Analysis (Invariants)

## 1. Hallucination Suppression (The Null Rule)

| Agent | Hallucinations (No Inv) | Hallucinations (With Inv) | Delta |
| :--- | :--- | :--- | :--- |
| Grounded | 8 | 2 | **-75%** |
| Auditor | 22 | 14 | **-36%** |
| Two-Pass | 6 | 20 | **+233%** |

### Observation: The "Two-Pass Inversion"
The `TwoPassAgent` is the only case where invariants *triggered* hallucinations. This is a critical discovery. The `TwoPassAgent` already performs an analysis step in Pass 1. Adding the invariants (TypeScript schema, Null Rule) to the *second* pass (extraction) appears to conflict with the information distilled in the first pass, potentially confusing the model into "over-verifying" and then hallucinating data to fill gaps it now feels pressured to address.

## 2. Rigid Type Matching (Dialect Awareness)

- **Incorrect Mappings:** Remained relatively stable across both groups.
- **Verdict:** Dialect Awareness hints in the `description` fields are likely too "distant" from the attention head when the schema is large. For Llama 3.2 3B, these hints need to be more prominent or interleaved (e.g., Lexicon-Grounded style) to solve mapping errors.

## 3. Structural Adherence (TypeScript compression)

- **Syntax Errors:** All agents maintained 100% JSON valid formats (thanks to `json_schema` response format).
- **Instruction Following:** Invariants improved `End-Anchored` F1 by helping it stay "inside" the target schema bounds during generation, reducing instances where the model ignored the anchor template.
