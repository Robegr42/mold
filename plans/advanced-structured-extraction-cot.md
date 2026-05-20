# Implementation Plan: Advanced Structured Information Extraction for GenSIE

This plan outlines the implementation of model-agnostic structured extraction strategies using Chain-of-Thought (CoT) and Constrained Decoding, as requested for the `gensie` project.

## 1. Objective
Enhance the `gensie` framework with advanced extraction strategies that improve accuracy and reliability across both Small Language Models (SLMs) and large LLMs. The focus is on implementing CoT patterns and ensuring strict schema adherence through constrained decoding and Pydantic validation.

## 2. Architectural Impact
The proposal introduces a modular strategy-based architecture under a new `src/gensie/strategies/` directory. This decouples the extraction logic from the core agent definition, allowing for easy comparison and expansion.

- **`GenSIEAgent` Extension**: New specialized agents will inherit from the base `GenSIEAgent` but will be composed of specific "strategies".
- **Dynamic Schema Modification**: Implementation of utilities to wrap/unwrap Pydantic schemas for internal reasoning.
- **Middleware Integration**: Use of `Instructor` as a bridge between models and Pydantic validation.

## 3. File Operations

### New Files
- `src/gensie/strategies/__init__.py`: Exports the strategy classes.
- `src/gensie/strategies/cot.py`: Implementation of `CoTExternalAgent` and `CoTInternalAgent`.
- `src/gensie/strategies/constrained.py`: Implementation of `ConstrainedAgent` (using `Outlines`/`XGrammar`).
- `src/gensie/utils/schema_utils.py`: Helpers for dynamic Pydantic model creation.
- `tests/test_advanced_strategies.py`: Unit and integration tests for new agents.

### Modified Files
- `src/gensie/eval.py`: (Updated) Extend to support logging of extra metrics (CoT success, token overhead) within the existing evaluation loop.
- `src/gensie/baseline.py`: Register new agents in the `OfficialParticipant` class.
- `pyproject.toml`: Add dependencies: `instructor`, `outlines`, `xgrammar`.

## 4. Step-by-Step Execution

### Step 1: Foundation & Utilities
1. **Dependency Update**: Add `instructor`, `outlines`, and `xgrammar` to `pyproject.toml`.
2. **Schema Utilities**: Create `src/gensie/utils/schema_utils.py` to handle:
   - Dynamic injection of a `"reasoning"` field into a Pydantic model.
   - Filtering out the reasoning field from the final dictionary.

### Step 2: Implementation of CoT Strategies
1. **External CoT (`CoTExternalAgent`)**:
   - Update the prompt to use `<think>` and `<answer>` tags (DeepSeek-R1 style).
   - Implement a robust parser in `cot.py` that extracts the content of `<answer>` while allowing the system to log/debug the content of `<think>`.
2. **Internal CoT (`CoTInternalAgent`)**:
   - Use the schema utility to wrap the `task.target_schema` into a new model containing a `thought_process: str` field.
   - Use `Instructor` to enforce the generation of this internal field.
   - Strip the field before returning the final JSON to the evaluator.

### Step 3: Integration of Constrained Decoding
1. **Constrained Agent (`ConstrainedAgent`)**:
   - Implement a wrapper that detects the model type.
   - For **Local Models (vLLM/Transformers)**: Use `Outlines` to create a guided sampler based on the JSON schema.
   - For **API-based Models (OpenAI/Anthropic)**: Use `Instructor`'s `response_format` or `mode=instructor.Mode.JSON` to leverage provider-native constrained decoding.
2. **XGrammar Support**: Add an option to use `XGrammar` for high-performance logit masking when running via `vLLM`.

### Step 4: Validation & Retry Logic
1. **Instructor Integration**: Wrap the model client using `instructor.patch()` or `instructor.from_openai()`.
2. **Retry Mechanism**: Configure the agents to perform up to 2 retries on Pydantic validation errors, passing the error message back to the model for self-correction.

### Step 5: Evaluation Integration
1. **`src/gensie/eval.py` Updates**: 
   - Ensure the existing evaluation loop can handle and log additional metadata from agents (like thinking tokens).
   - Compare `baseline` vs `reasoning-guided` vs `constrained-cot-internal` on the provided datasets.

## 5. Testing Strategy
1. **Unit Tests**:
   - Validate that `schema_utils` correctly adds/removes fields.
   - Test `parse_cot_tags` with various "dirty" model outputs (missing tags, markdown blocks).
2. **Integration Tests**:
   - Run a subset of `data/dev/` tasks through each strategy using a small model (e.g., `Llama-3.2-3B`).
   - Verify that `ConstrainedAgent` never returns invalid JSON.

## 6. Model Agnostic Approach
To maintain model agnosticism, the agents will use the `OPENAI_BASE_URL` and `OPENAI_API_KEY` pattern. 
- If the URL points to a standard API (OpenAI/Groq), it uses provider-native JSON mode.
- If the URL points to a local `vLLM` or `Ollama` instance, it can optionally trigger `Outlines` or `XGrammar` logic via server-side parameters or client-side logit processing.
