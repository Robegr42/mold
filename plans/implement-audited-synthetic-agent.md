# Plan: Implement `AuditedSyntheticAgent` and `audited-synthetic` Pipeline

This plan outlines the implementation of a new "Double-Gate" extraction agent that validates synthetic few-shot examples using both semantic similarity and structural integrity checks. This ensures that Small Language Models (SLMs) are protected from "Negative Transfer" caused by low-quality or hallucinated synthetic data.

## 1. Objective
Implement the `AuditedSyntheticAgent` and register the `audited-synthetic` pipeline. The agent will extend the current `SyntheticAnchorAgent` logic by adding a mandatory audit step for synthetic examples, enforcing a **0.70 similarity threshold** and strict **JSON Schema validation**.

## 2. Architectural Impact
- **Enhanced Reliability**: Prevents "Few-Shot Collapse" and "Value Leakage" in SLMs by filtering out semantically drifted synthetic anchors.
- **Double-Gate Architecture**:
    1. **RAG Gate (0.55)**: Attempt to find historical examples.
    2. **Synthetic Audit Gate (0.70)**: If RAG fails, generate synthetic data and verify it against the task input.
- **Immediate Fallback**: Automates a graceful pivot to Zero-Shot extraction if both RAG and Synthetic Audit fail, optimizing token usage.

## 3. File Operations

### Modified Files:
- **`pyproject.toml`**: Add `jsonschema` to the project dependencies.
- **`src/gensie/baseline.py`**:
    - Add `import jsonschema`.
    - Implement the `AuditedSyntheticAgent` class.
    - Update `OfficialParticipant` to include the `audited-synthetic` pipeline.

### New Files:
- **`tests/test_audited_synthetic_agent.py`**: Unit tests for the new agent, covering audit success, similarity failure, and schema failure scenarios.

## 4. Implementation Steps

### Step 1: Update Dependencies
Add `jsonschema` to the `dependencies` list in `pyproject.toml` to support structural validation of synthetic JSON.
```toml
dependencies = [
    ...
    "jsonschema>=4.23.0",
]
```

### Step 2: Implement `AuditedSyntheticAgent` in `src/gensie/baseline.py`
1. **Import jsonschema**: Add `from jsonschema import validate, ValidationError` at the top of the file.
2. **Class Definition**: Create `AuditedSyntheticAgent(GenSIEAgent, InvariantPromptMixin)`.
3. **Audit Logic**: Implement `audit_synthesis(self, task: Task, synthetic: Dict[str, Any]) -> bool`:
    - **Structural Check**: Use `jsonschema.validate` against `task.target_schema`. Catch `ValidationError`.
    - **Semantic Check**:
        - Use `self.rag.model` (`all-MiniLM-L6-v2`) to encode the task query and the synthetic text.
        - Ensure embeddings are normalized.
        - Calculate cosine similarity (dot product).
        - Enforce the **0.70 threshold**.
    - Return `True` only if both checks pass.
4. **Agent Loop (`run` method)**:
    - Attempt Gated RAG (Threshold 0.55).
    - If no relevant examples found, call `architect.synthesize_example`.
    - Call `audit_synthesis`.
    - If audit passes: Use synthetic example as few-shot.
    - If audit fails: Set empty few-shot string and inject a Zero-Shot generalization directive.

### Step 3: Register Pipeline
Update `OfficialParticipant` in `src/gensie/baseline.py`:
- Add `"audited-synthetic": AuditedSyntheticAgent()` to the `pipelines` dictionary.
- Add `PipelineInfo` for `audited-synthetic` to the `get_info()` method.

## 5. Verification & Testing

### Unit Tests (`tests/test_audited_synthetic_agent.py`)
- **`test_audit_synthesis_success`**: Mock embeddings with > 0.70 similarity and valid schema.
- **`test_audit_synthesis_low_similarity`**: Mock embeddings with < 0.70 similarity; verify rejection.
- **`test_audit_synthesis_invalid_schema`**: Provide synthetic JSON that violates `task.target_schema`; verify rejection.
- **`test_run_fallback_to_zeroshot`**: Verify that if `audit_synthesis` returns `False`, the prompt sent to the LLM contains the "Zero-shot extraction" directive and no few-shot examples.

### Integration Validation
- Run the pipeline using the CLI: `gensie run --pipeline audited-synthetic --model <model_name>`.
- Check logs for "Synthetic audit failed similarity check" or "Synthetic audit failed structural check" messages.
