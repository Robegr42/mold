# Grammar-Constrained Decoding (FST-FSA/PDA) Implementation Plan (v2)

## 1. Overview
This plan implements the "Automata-based constraints for language model decoding" strategy (arXiv:2407.08103) from scratch in pure Python. The core goal is to bridge the "tokenization gap" using a Finite-State Transducer (FST) that maps the model's vocabulary to a Pushdown Automaton (PDA) representing a JSON schema.

By intervening at the token-selection level, we guarantee 100% adherence to the target JSON schema without relying on the model's instruction-following capabilities.

## 2. Architectural Impact
- **Agent Layer**: A new `GrammarConstrainedAgent` will be added to `src/gensie/baseline.py`.
- **Constraint Engine**: A library-free implementation of PDA and FST mapping will be placed in `src/gensie/utils/constraints.py`.
- **Integration**: The `OfficialParticipant` will be updated to include the `grammar-constrained` pipeline.

## 3. Data Structures & Algorithms

### A. Pushdown Automaton (PDA)
Since JSON is context-free (due to nested objects and arrays), we use a PDA rather than a simple FSA.
- **States**: Represent the current position in the JSON structure (e.g., `EXPECTING_KEY`, `EXPECTING_VALUE`, `EXPECTING_COMMA`).
- **Stack**: Tracks nesting depth and the expected closing character (`}` or `]`).
- **Transitions**: Defined by the JSON Schema (e.g., if in `EXPECTING_KEY`, only valid property names from the schema are allowed).

### B. Vocabulary FST (Transducer)
To handle tokens that might contain multiple characters or partial grammar transitions:
- **Input**: A token ID from the model's vocabulary.
- **Output**: The string representation of that token.
- **Mapping**: For a given PDA state, we pre-calculate which tokens are valid by checking if their string representation is a valid path in the PDA starting from that state.

### C. JSON Schema Compiler
A recursive function that converts a JSON schema into a state-transition graph for the PDA.
- Handles `type: "object"`, `"array"`, `"string"`, `"number"`, `"boolean"`.
- Supports `required` properties and property ordering.

## 4. Implementation Details

### `src/gensie/utils/constraints.py`
```python
class JSONPDA:
    def __init__(self, schema):
        self.states = self._compile_schema(schema)
        self.reset()

    def reset(self):
        self.current_state = "START"
        self.stack = []

    def get_valid_next_chars(self):
        # Returns a set of characters or regexes valid at current state
        pass

    def step(self, char):
        # Updates state and stack based on input character
        pass

class ConstraintEngine:
    def __init__(self, schema, vocabulary):
        self.pda = JSONPDA(schema)
        self.vocabulary = vocabulary # {token_id: string}
        self._cache = {}

    def get_mask(self, pda_state, stack):
        # Implementation of the FST-based valid token set calculation
        # Returns a list of token_ids valid for the current PDA configuration
        pass
```

### `src/gensie/baseline.py`
```python
class GrammarConstrainedAgent(GenSIEAgent):
    def __init__(self, model_id):
        self.client = OpenAI(
            base_url=os.getenv("OPENAI_BASE_URL"),
            api_key=os.getenv("OPENAI_API_KEY", "sk-dummy"),
        )
        self.model_id = model_id
        self.engine = None
```
    def run(self, task: Task, model: str) -> Dict[str, Any]:
        # 1. Initialize Engine with task.target_schema
        # 2. Use a custom loop or logit_bias (if supported per-token)
        # Note: For OpenAI APIs, we may use 'logit_bias' in a per-token loop
        # or implement this for local backends that support LogitsProcessors.
        pass
```

## 5. Step-by-Step Execution

1.  **Core PDA implementation**: Build the base `JSONPDA` class in `src/gensie/utils/constraints.py` that handles basic JSON structure.
2.  **Schema Compiler**: Implement the logic to turn a `json_schema` into PDA states.
3.  **FST Mapping**: Implement the logic to filter a vocabulary based on the PDA state.
4.  **Agent Integration**: Add `GrammarConstrainedAgent` to `src/gensie/baseline.py`.
5.  **Offline Vocabulary**: Use `tiktoken` to load the vocabulary for the target model.

## 6. Verification Strategy

- **Automata Tests**: Unit tests for the PDA with various JSON schemas (nested, empty, complex).
- **Tokenization Tests**: Verify that the FST correctly handles tokens like `": "` or `"},"`.
- **End-to-End**: Run `gensie eval` on the `grammar-constrained` pipeline and verify 100% valid JSON output.
