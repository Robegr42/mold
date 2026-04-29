# Grammar-Constrained Decoding (FST-FSA/PDA) Implementation Plan

## 1. Overview
The **Grammar-Constrained Decoding** strategy (specifically FST-FSA/PDA Composition) addresses the problem of Small Language Models (SLMs) failing to maintain structural integrity in their outputs. Instead of relying on the model to "follow instructions," this method intervenes at the token-sampling level. 

By composing a Finite State Transducer (FST) representing the model's vocabulary with a Finite State Automaton (FSA) or Pushdown Automaton (PDA) representing the target JSON schema, we can calculate a mask of valid tokens at every generation step. This guarantees that the generated sequence is 100% compliant with the schema, effectively eliminating parsing errors.

## 2. Architectural Impact
- **Agent Layer**: A new `GrammarConstrainedAgent` will be added to `src/gensie/baseline.py`. This agent will handle local model loading and constrained generation.
- **Participant Configuration**: The `OfficialParticipant` will be updated to include the `grammar-constrained` pipeline, making it available for evaluation and production.
- **Dependency Management**: The project will require `outlines` and a local inference backend (e.g., `transformers` or `llama-cpp-python`).

## 3. File Operations

### `src/gensie/baseline.py`
- **Modify**: Add `GrammarConstrainedAgent` class.
- **Modify**: Update `OfficialParticipant.__init__` to instantiate the new agent.
- **Modify**: Update `OfficialParticipant.get_info` to include the new pipeline metadata.

### `pyproject.toml`
- **Modify**: Add `outlines`, `transformers`, and `torch` to the `dependencies` list.

## 4. Implementation Details

### Library Choice: `outlines`
`outlines` is the recommended library as it is specifically designed for FST-guided generation and supports JSON schema constraints natively. It works with Hugging Face models and `llama-cpp-python`.

### Class Structure: `GrammarConstrainedAgent`
The agent will implement the `GenSIEAgent` interface. It will lazily load the model and cache generators based on the JSON schema to improve performance during batch processing.

```python
class GrammarConstrainedAgent(GenSIEAgent):
    def __init__(self, model_id: str = "Qwen/Qwen2.5-1.5B-Instruct", device: str = "cpu"):
        self.model_id = model_id
        self.device = device
        self._model = None
        self._generator_cache = {}

    @property
    def model(self):
        import outlines
        if self._model is None:
            # Initialize the outlines model wrapper
            self._model = outlines.models.transformers(self.model_id, device=self.device)
        return self._model

    def run(self, task: Task, model: str) -> Dict[str, Any]:
        import outlines
        import json

        # model_id can be overridden by the 'model' parameter if provided
        target_model_id = model or self.model_id
        
        # Cache generator per schema to avoid recompiling the FSM
        schema_key = json.dumps(task.target_schema, sort_keys=True)
        if schema_key not in self._generator_cache:
            self._generator_cache[schema_key] = outlines.generate.json(
                self.model, 
                task.target_schema
            )
        
        generator = self._generator_cache[schema_key]
        prompt = task.get_input_prompt()
        
        # Perform constrained generation
        # outlines returns the parsed JSON object (dict)
        return generator(prompt)
```

### Integration into `OfficialParticipant`
```python
class OfficialParticipant(Participant):
    def __init__(self):
        self.pipelines = {
            "baseline": BasicAgent(),
            "end-anchored": EndAnchoredAgent(),
            "grammar-constrained": GrammarConstrainedAgent(), # New
        }

    def get_info(self) -> ParticipantInfo:
        return ParticipantInfo(
            # ... existing info ...
            pipelines=[
                # ... existing pipelines ...
                PipelineInfo(
                    name="grammar-constrained",
                    description="Local SLM with token-level FSM constraints for 100% JSON schema adherence.",
                ),
            ],
        )
```

## 5. Step-by-Step Execution

### Step 1: Environment Setup
Add the necessary dependencies to `pyproject.toml` and sync the environment.
```bash
uv add outlines transformers torch
```

### Step 2: Implement the Agent
1.  Open `src/gensie/baseline.py`.
2.  Add `import outlines` (ideally inside methods or protected by try-except to keep the baseline light).
3.  Define `GrammarConstrainedAgent` with the logic for initializing the `outlines` model and utilizing `outlines.generate.json`.
4.  Ensure the agent correctly uses `task.target_schema` and `task.get_input_prompt()`.

### Step 3: Register the Pipeline
1.  Update the `OfficialParticipant` class in `src/gensie/baseline.py`.
2.  Add `"grammar-constrained": GrammarConstrainedAgent()` to the `self.pipelines` dictionary in `__init__`.
3.  Add the corresponding `PipelineInfo` to the `get_info` method.

### Step 4: Optimization (Optional but Recommended)
- Use `llama-cpp-python` as the backend for `outlines` if targetting machines without GPUs.
- Implement a logic to handle very large schemas that might cause slow FSM compilation.

## 6. Verification Strategy

### Structural Validation
Run the new agent on a diverse set of tasks from `data/dev/` and verify that **every** output is a valid JSON object matching the provided schema using the `jsonschema` library.

### Performance Benchmarking
Execute the evaluator to compare the `grammar-constrained` pipeline against the `baseline` (OpenAI).
```bash
gensie eval --pipeline grammar-constrained --data data/dev/legal_contracts_001.json
```

### Unit Testing
Create a new test file `tests/test_grammar_agent.py` to:
1.  Verify that `GrammarConstrainedAgent` correctly loads.
2.  Mock the `outlines` generator to ensure it receives the correct schema and prompt.
3.  Test error handling when a model fails to load or the device is unavailable.
