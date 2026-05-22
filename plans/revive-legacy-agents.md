# Plan: Reviving Legacy Agents (EAGLE, SAGE, AURA)

## 1. Objective
Revive the legacy 'end-anchored', 'grounded', and 'auditor' extraction pipelines as standalone agents within the current GenSIE architecture. The revived agents will be named `EAGLEAgent`, `SAGEAgent`, and `AURAAgent` respectively. They will adhere to the new parameterless initialization specification and integrate the optimal invariant configurations identified in recent ablation studies.

## 2. Key Files & Context
- **`src/gensie/baseline.py`**: Target location for the new agents. They will inherit from `GenSIEAgent` and `InvariantPromptMixin`.
- **`src/gensie/eval.py`**: The evaluation logic which introduced constraints like the global Micro-F1 and hard null penalty.

## 3. Proposed Solution

### EAGLEAgent (End-Anchored Generation & Logical Extraction)
- **Architecture**: Appends the target schema at the very end of the prompt to maximize schema adherence (acting as an anchor).
- **Configuration (Parameterless Init)**:
  - `self.use_null = True` (Strongest invariant for End-Anchored, acts as a coherence anchor).
  - `self.use_ts = False` (Optimized for Qwen models <2B which prefer raw JSON schema).
  - `self.use_dialect = False`
  - `self.use_dates = True` (Standard for new eval constraints).

### SAGEAgent (Source-Aligned Grounded Extraction)
- **Architecture**: A single-pass grounded extraction engine that instructs the model to explicitly quote or cite the source text for every extracted field.
- **Configuration (Parameterless Init)**:
  - `self.use_null = True` (Provides a massive precision boost for grounded strategies).
  - `self.use_ts = True` (Optimized for Llama 3B+ models).
  - `self.use_dialect = False`
  - `self.use_dates = True`

### AURAAgent (Automated Understanding & Refinement Auditor)
- **Architecture**: A two-pass architecture featuring an initial draft extraction followed by a rigorous "Skeptical Auditor" pass (ReAct loop) to prune hallucinations.
- **Configuration (Parameterless Init)**:
  - `self.use_null_p1 = False` and `self.use_null_p2 = False` (Aggressive nullification is handled by the auditor logic, not prompt mixins).
  - `self.use_dialect = True` (Critical semantic alignment boost during the audit pass).
  - `self.use_ts = True` (Auditor structure specifically benefits from TS schema compression).
  - `self.use_dates = True`

## 4. Implementation Steps
1. **Agent Definition**: Define `EAGLEAgent`, `SAGEAgent`, and `AURAAgent` classes in `src/gensie/baseline.py`.
2. **Initialization**: Implement the parameterless `__init__` for each, hardcoding the specific optimal invariant flags.
3. **Execution Logic**: Implement the `run` method for each agent, translating their legacy architectures (end-anchoring, grounding instructions, and the audit loop) to use the `client.chat.completions.create` API with `response_format={"type": "json_schema"}` where applicable.
4. **Token Tracking**: Ensure `UsageTracker` is correctly instantiated and updated within the execution loop for all three agents.

## 5. Verification & Testing
- Write unit tests for each agent in `tests/test_agents.py` (or similar) to verify instantiation and basic extraction loops.
- Run `make test` to ensure no regressions.
- Execute local evaluations against `data/starter/` using the `gensie eval` command to verify that the hardcoded invariants result in the expected performance metrics.