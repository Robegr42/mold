# Final Implementation Plan: GenSIE Agent Architecture

## Objective
Execute the refactoring of the GenSIE extraction pipeline as outlined in the `gensie_agent_architecture_plan.md`. This involves stripping architectural invariants (TypeScript compression, Extract-or-Null gating, Dialect-Awareness) out of standalone agents and baking them into foundational utilities and mixins. We will then implement three specialized, hardened agents that inherit these invariants.

## Key Files & Context
*   **Target File for Refactoring:** `src/gensie/baseline.py` (contains the legacy `BasicAgent` and `OfficialParticipant` registry).
*   **New Utility File:** `src/gensie/utils/schema.py`
*   **Primary Reference:** `plans/gensie_agent_architecture_plan.md`

## Phase 1: Foundational Invariants

### 1.1 TypeScript Schema Compression Utility
The `TypeScriptSchemaAgent` from early research is demoted to a pure utility function.
*   **Action:** Create `src/gensie/utils/schema.py`.
*   **Implementation:** Implement `compress_schema_to_ts(schema: Dict) -> str`. This function must iterate through a JSON schema and return a concise pseudo-TypeScript string.
*   **Safety:** Must handle basic nested objects and map JSON schema types (`string`, `integer`, `number`) to TypeScript equivalents (`string`, `number`). Optional fields should be marked with `?`.

### 1.2 The `InvariantPromptMixin`
The `DialectAwareAgent` concept and the "Extract-or-Null" rules are consolidated into a mixin.
*   **Action:** Add `InvariantPromptMixin` to `src/gensie/baseline.py` (or a dedicated base classes file if standard in the repo).
*   **Implementation:** Add the method `apply_invariants(self, base_prompt: str, target_schema: dict) -> str`.
*   **Logic:**
    1.  Call `compress_schema_to_ts(target_schema)`.
    2.  Append a strict block to the `base_prompt` containing:
        *   **Extract-or-Null Rule:** "Do not infer or guess. If information is absent, return `null`."
        *   **Dialect Rule:** Instructions to respect Iberian/Latin American synonyms and match the provided TypeScript interface.

## Phase 2: Core Agent Implementation
We will implement three specialized agents. All must inherit from both the project's base agent class (e.g., `GenSIEAgent`) and the new `InvariantPromptMixin`.

### 2.1 `TwoPassAgent`
*   **Goal:** Decouple reasoning from strict formatting.
*   **Pass 1 (Analysis):** Prompt the model to analyze the text step-by-step in Spanish (unconstrained).
*   **Pass 2 (Extraction):** Feed the original text *and* the Pass 1 analysis back to the model. Call `self.apply_invariants()` to inject the strict TS schema and formatting rules into this second prompt. Use `response_format={"type": "json_schema"}`.
*   **Fallback:** If `json_schema` parsing fails locally, catch the exception and retry with `{"type": "json_object"}`.

### 2.2 `GroundedAgent`
*   **Goal:** Force evidence-based extraction.
*   **Implementation:** A single-pass agent. The base prompt instructs the model to act as a "skeptical auditor" and mandates that a source quote must exist to authorize extraction.
*   **Invariant Injection:** Call `self.apply_invariants()` on the prompt before execution to enforce the schema and `null` fallbacks.

### 2.3 `AuditorAgent`
*   **Goal:** Self-correction loop to strike hallucinations.
*   **Pass 1 (Draft):** Generate a preliminary JSON draft (using `json_object` or unconstrained format).
*   **Pass 2 (Audit):** Pass the Draft and the Source text to the model. Instruct it to act as an adversarial inspector, sweeping the draft and replacing any unverified claim with a hard `null`.
*   **Invariant Injection:** Apply the `InvariantPromptMixin` strictly to the Pass 2 audit step to ensure the final output matches the target schema perfectly.

## Phase 3: Pipeline Integration

### 3.1 Update Participant Registry
*   **Action:** Modify the `OfficialParticipant` (or equivalent entry point class) in `src/gensie/baseline.py`.
*   **Implementation:** Register `TwoPassAgent`, `GroundedAgent`, and `AuditorAgent` into the execution flow, replacing the legacy `BasicAgent` or `TypeScriptSchemaAgent` configurations.

## Verification & Testing
1.  **Unit Tests:** Run existing tests in `tests/` to ensure the new agents conform to the `GenSIEAgent` interface and successfully return parsed JSON.
2.  **Fallback Verification:** Explicitly test the try-except fallback from `json_schema` to `json_object` to ensure offline compatibility.
3.  **Schema Check:** Verify that the `compress_schema_to_ts` utility correctly handles nested structures without throwing recursive errors.
