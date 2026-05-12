# Implementation Plan: Slim Champion Pipeline

## Objective
Create a streamlined version of the Champion pipeline (`SlimChampionAgent`) tailored for small language models (like Llama-3.2-3B). This pipeline removes high-latency, low-diversity mechanisms (Ensembling and ReAct Auditing) while retaining RAG capabilities and integrating the critical `InvariantPromptMixin` for improved grounding.

## Key Files & Context
- `src/gensie/baseline.py`: Location for the new agent class and where it will be registered in `OfficialParticipant`.

## Implementation Steps

### 1. Create `SlimChampionAgent`
Add a new class `SlimChampionAgent` that inherits from `GenSIEAgent` and `InvariantPromptMixin`.

- **Initialization:**
  - Initialize OpenAI client.
  - Initialize `RAGModule` and `ArchitectModule`.
  - Configure to use all invariants (`use_ts=True, use_null=True, use_dialect=True`).

- **Execution Flow (`run` method):**
  - **Augmentation:**
    - Fetch few-shot examples via `RAGModule`.
    - Fetch reasoning hints via `ArchitectModule`.
  - **Pass 1: Unconstrained Analysis (Spanish):**
    - Construct a prompt combining the instruction, input text, RAG examples, and architect hints.
    - Use `apply_invariants` to enforce architectural rules during reasoning.
    - Request step-by-step analysis in Spanish.
    - **Crucially:** Request the output as raw text (not a strict JSON schema) to eliminate reasoning friction for the 3B model.
  - **Pass 2: Strict Extraction:**
    - Construct a prompt containing the original instruction, input text, and the analysis from Pass 1.
    - Use `apply_invariants` to enforce the TS Schema and Extract-or-Null rules.
    - Execute the API call using strict `json_schema` response format.
    - Include a fallback to standard text-based JSON extraction if the strict schema call fails.

### 2. Register the Pipeline
Update the `OfficialParticipant` class in `src/gensie/baseline.py` to register the new pipeline:
- Add `"slim-champion": SlimChampionAgent()` to the `self.pipelines` dictionary.
- Add a corresponding `PipelineInfo` entry in the `get_info` method describing it as a "Streamlined high-accuracy pipeline with RAG and Two-Pass reasoning, optimized for SLMs."

## Verification & Testing
- Run `gensie-cli eval2` with the `slim-champion` pipeline on a known failing task (e.g., `medical_drug_001.json`) to verify that the 45-second timeout is no longer an issue and that the agent completes successfully.
- Run a full evaluation to confirm it outperforms the baseline and the original champion pipeline.
