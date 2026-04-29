# Speculative Constrained Decoding Implementation Plan

## 1. Overview
**Speculative Constrained Decoding** is an optimization strategy that accelerates the inference of Small Language Models (SLMs) while guaranteeing 100% adherence to a structured format (like JSON). 

The core challenge with grammar-constrained decoding is the computational overhead added at each token-sampling step. Speculative decoding mitigates this by using a dual-model system:
- **Draft Model**: A tiny, extremely fast model (e.g., Qwen2.5-0.5B) that proposes a sequence of candidate tokens.
- **Target Model**: A larger, more capable SLM (e.g., Qwen2.5-1.5B or 7B) that verifies these candidates in parallel.
- **Constrained Masking**: A JSON-schema-based filter (via FSM) is applied to the Target Model, ensuring that only valid tokens are accepted or generated.

**Benefits:**
- **Reduced Latency**: Can achieve 2x-3x speedup compared to standard constrained decoding.
- **Guaranteed Validity**: Output is forced to match the JSON schema through token-level masking.
- **Resource Efficiency**: Leverages the "wasteful" compute of the target model's forward pass to verify multiple tokens at once.

## 2. Architectural Impact
- **`src/gensie/baseline.py`**: Will house the new `SpeculativeGrammarAgent` and registration in `OfficialParticipant`.
- **Dependency Graph**: Introduction of `transformers`, `outlines`, and `torch` to support local model inference and FSM constraints.
- **Resource Management**: Implementation of lazy-loading for models to manage VRAM/RAM consumption effectively.

## 3. File Operations

### `src/gensie/baseline.py`
- **Add** `SpeculativeGrammarAgent` class.
- **Update** `OfficialParticipant.__init__` to include the `speculative-grammar` pipeline.
- **Update** `OfficialParticipant.get_info` to provide metadata for the new pipeline.

### `pyproject.toml`
- **Add** dependencies: `transformers`, `outlines`, `torch`, `accelerate`.

## 4. Implementation Details

### Choice of Library: `transformers` + `outlines`
The implementation will utilize the `transformers` library's `assisted_generation` feature (which handles the speculative decoding logic) and `outlines` for its highly efficient `JSONLogitsProcessor`.

### Logic for Managing Draft vs. Target Models
1.  **Initialization**: Both models must share the same tokenizer (e.g., the Qwen2.5 family) to ensure token IDs are consistent across models.
2.  **Constraint Integration**: The `outlines` FSM is used to create a `LogitsProcessor` for the target model.
3.  **Generation Loop**: 
    - The Draft Model generates $N$ tokens.
    - The Target Model verifies them in a single forward pass, filtered by the `JSONLogitsProcessor`.
    - If the Draft Model proposes a token that violates the JSON grammar, the Target Model's logit for that token will be $-\infty$, forcing a rejection and a correction to a valid token.

### Proposed Code Structure for `SpeculativeGrammarAgent`

```python
class SpeculativeGrammarAgent(GenSIEAgent):
    def __init__(self, target_id="Qwen/Qwen2.5-1.5B-Instruct", draft_id="Qwen/Qwen2.5-0.5B-Instruct"):
        self.target_id = target_id
        self.draft_id = draft_id
        self._target_model = None
        self._draft_model = None
        self._tokenizer = None
        self._processor_cache = {}

    def _load_models(self):
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch
        if self._target_model is None:
            self._tokenizer = AutoTokenizer.from_pretrained(self.target_id)
            self._target_model = AutoModelForCausalLM.from_pretrained(
                self.target_id, torch_dtype=torch.float16, device_map="auto"
            )
            self._draft_model = AutoModelForCausalLM.from_pretrained(
                self.draft_id, torch_dtype=torch.float16, device_map="auto"
            )

    def run(self, task: Task, model: str) -> Dict[str, Any]:
        from outlines.integrations.transformers import JSONLogitsProcessor
        from transformers import LogitsProcessorList
        import json

        self._load_models()
        
        # Cache the FSM-based logits processor per schema
        schema_key = json.dumps(task.target_schema, sort_keys=True)
        if schema_key not in self._processor_cache:
            self._processor_cache[schema_key] = JSONLogitsProcessor(
                task.target_schema, self._target_model, self._tokenizer
            )
        
        logits_processor = LogitsProcessorList([self._processor_cache[schema_key]])
        prompt = task.get_input_prompt()
        inputs = self._tokenizer(prompt, return_tensors="pt").to(self._target_model.device)

        outputs = self._target_model.generate(
            **inputs,
            assistant_model=self._draft_model,
            logits_processor=logits_processor,
            max_new_tokens=1024,
            do_sample=False, # Speculative decoding is most efficient with greedy/low-temp
            pad_token_id=self._tokenizer.eos_token_id
        )

        result_text = self._tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
        return json.loads(result_text)
```

## 5. Step-by-Step Execution

### Step 1: Dependency Integration
Update `pyproject.toml` to include the necessary stack for local SLM inference.
```bash
uv add transformers outlines torch accelerate
```

### Step 2: Implement the Agent Class
1.  Open `src/gensie/baseline.py`.
2.  Import `LogitsProcessorList` from `transformers` and `JSONLogitsProcessor` from `outlines`.
3.  Implement `SpeculativeGrammarAgent` with lazy loading to ensure the environment remains lightweight if the pipeline isn't used.
4.  Ensure the `run` method correctly handles the `task.target_schema`.

### Step 3: Register the Pipeline
1.  Modify `OfficialParticipant.__init__` in `src/gensie/baseline.py`:
    ```python
    self.pipelines["speculative-grammar"] = SpeculativeGrammarAgent()
    ```
2.  Update `get_info()` to include a description of the speculative strategy.

### Step 4: Verification and Benchmarking
1.  **Schema Adherence**: Run the agent against the `data/dev/` suite. Validate that every output passes `jsonschema` verification.
2.  **Latency Comparison**: Compare the `duration` of the `speculative-grammar` pipeline vs. a non-speculative `grammar-constrained` agent using the same target model.
3.  **Tokenizer Validation**: Ensure the chosen draft and target models have identical vocabularies to prevent decoding errors.

## 6. Testing Strategy
- **Unit Test**: Create `tests/test_speculative_agent.py` to mock model outputs and verify that the `JSONLogitsProcessor` is correctly called within the `generate` loop.
- **Integration Test**: Run `gensie eval --pipeline speculative-grammar --data data/dev/medical_entities_001.json` and verify the results file for parsing success rates and inference speed.
