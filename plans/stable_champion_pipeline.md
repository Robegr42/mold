# Implementation Plan: Stable Champion Pipeline

## Objective
Create a `StableChampionAgent` that adapts the streamlined architecture of the `SlimChampionAgent` (RAG-boosted, Two-Pass, no ensembling/auditing) but applies the optimal invariant configuration identified in the `Two-Pass` ablation studies.

Based on the research report and empirical data:
- The base `Two-Pass-NI` (No Invariants) is the most consistent generalizer across model scales.
- However, the `Null Rule` (`use_null=True`) is identified as the "universal suppressor for hallucinations" and the most important component for model-independent gain.
- In the data, `Two-Pass-Null` achieved the highest F1 for Llama 3B (0.601) and strong results for Qwen 1.7B (0.684).

Therefore, the **optimal invariant configuration** for both Phase 1 (Reasoning) and Phase 2 (Extraction) will be:
- `use_ts=False` (Standard JSON Schema instead of TypeScript)
- `use_null=True` (Strict Extract-or-Null rule)
- `use_dialect=False` (No dialect rules)

## Key Files & Context
- `src/gensie/baseline.py`: Location for the new agent class and registry.

## Implementation Steps

### 1. Create `StableChampionAgent`
Add a new class `StableChampionAgent` that inherits from `GenSIEAgent` and `InvariantPromptMixin`.

- **Initialization:**
  - Initialize the OpenAI client.
  - Initialize `RAGModule` and `ArchitectModule`.
  - **Crucially Configure Invariants:** Set `use_ts=False`, `use_null=True`, and `use_dialect=False`.

- **Execution Flow (`run` method):**
  - **Augmentation:** Fetch few-shot examples via `RAGModule` and reasoning hints via `ArchitectModule`.
  - **Pass 1: Unconstrained Analysis (Spanish):**
    - Construct the analysis prompt combining instruction, text, hints, and few-shots.
    - Call `self.apply_invariants` (which will inject the JSON Schema and the Null Rule).
    - Request raw text output (step-by-step reasoning in Spanish).
  - **Pass 2: Strict Extraction:**
    - Construct the extraction prompt containing the instruction, input text, and the Pass 1 analysis.
    - Call `self.apply_invariants` again to reinforce the schema and Null Rule.
    - Execute the API call using strict `json_schema` response format.
    - Implement a fallback to text-based JSON if the strict schema fails.

### 2. Register the Pipeline
Update `OfficialParticipant` in `src/gensie/baseline.py`:
- Add `"stable-champion": StableChampionAgent()` to `self.pipelines`.
- Add a corresponding `PipelineInfo` describing it as "Streamlined architecture using the optimal Two-Pass invariant configuration (Null-Rule only)."

## Verification & Testing
- Use `gensie-cli eval2` with the `stable-champion` pipeline on the starter dataset.
- Confirm that the F1 score aligns with or exceeds the individual `Two-Pass-Null` baseline, benefiting from the added RAG and Architect hints.
