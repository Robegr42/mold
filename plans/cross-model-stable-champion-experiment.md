# Rigorous Experiment Plan: Stable-Champion Pipeline Evaluation

## 1. Objective
Evaluate the `stable-champion` pipeline across three target models to establish its performance ceiling and stability compared to the `two-pass-ni` baseline. The experiment specifically investigates the impact of RAG density, reasoning language, and architect hint count on extraction accuracy and efficiency.

### Target Models
- `llama-3.2-3b-instruct`
- `qwen/qwen3-1.7b`
- `google/gemma-4-e4b`

### Evaluation Dataset
- `data/starter/` (40 tasks across Cultural, Legal, Medical, and Technical domains)

---

## 2. Architectural Impact
The experiment leverages the existing `GenSIE` evaluation framework. To support the requested tuning points without creating redundant agent classes, the `StableChampionAgent` and its supporting modules will be updated to support **Environment-Driven Configuration**. This allows the `cli eval2` command to trigger different ablation variants by simply setting environment variables before execution.

---

## 3. File Operations

### `src/gensie/baseline.py`
- **Modify `RAGModule`**: Update `get_few_shot_examples` to accept an optional `k` parameter.
- **Modify `ArchitectModule`**: Update `get_reasoning_hints` to accept `lang` (Spanish/English) and `count` parameters, using a formatted prompt template.
- **Modify `StableChampionAgent`**: 
    - In `__init__`, read `GENSIE_RAG_K`, `GENSIE_REASONING_LANG`, and `GENSIE_HINT_COUNT` from environment variables.
    - Pass these parameters to the RAG and Architect modules during the `run` method.
- **Modify `OfficialParticipant`**: Ensure `stable-champion` and `two-pass-ni` are correctly registered.

---

## 4. Technical Environment Setup

### vLLM / OpenAI Server Configuration
Deploy the models using an OpenAI-compatible server (e.g., vLLM or LiteLLM) to act as the backend for the GenSIE Agent Server.

```bash
# Example vLLM launch for Llama (repeat for other models on different ports or use a gateway)
python -m vllm.entrypoints.openai.api_server \
    --model llama-3.2-3b-instruct \
    --port 8000 \
    --tensor-parallel-size 1
```

### Environment Variables
Configure the connection to the model server:
```bash
export OPENAI_BASE_URL="http://localhost:8000/v1"
export OPENAI_API_KEY="sk-gen-sie-2024"
```

---

## 5. Proposed Ablation/Tuning Matrix

| Variant ID | Pipeline | RAG K | Reason Lang | Hint Count |
| :--- | :--- | :--- | :--- | :--- |
| **V0 (Baseline)** | `two-pass-ni` | N/A | Spanish | N/A |
| **V1 (Champion Default)** | `stable-champion` | 3 | Spanish | 3-5 |
| **V2 (Sparse RAG)** | `stable-champion` | 1 | Spanish | 3-5 |
| **V3 (English Reasoning)** | `stable-champion` | 3 | English | 3-5 |
| **V4 (Minimal Hints)** | `stable-champion` | 3 | Spanish | 1 |
| **V5 (Maximal Hints)** | `stable-champion` | 3 | Spanish | 5 |

---

## 6. Evaluation Sequence (CLI Commands)

### Step 1: Start the Agent Server
```bash
# In a dedicated terminal
uv run python -m gensie.cli serve
```

### Step 2: Execute Baseline Runs
```bash
# Llama 3.2 3B
uv run python -m gensie.cli eval2 --data data/starter/ --pipeline two-pass-ni --model llama-3.2-3b-instruct --output results/baseline_llama.json

# Qwen 3 1.7B
uv run python -m gensie.cli eval2 --data data/starter/ --pipeline two-pass-ni --model qwen/qwen3-1.7b --output results/baseline_qwen.json

# Gemma 4 e4b
uv run python -m gensie.cli eval2 --data data/starter/ --pipeline two-pass-ni --model google/gemma-4-e4b --output results/baseline_gemma.json
```

### Step 3: Execute Tuning Matrix (Example for Llama 3.2 3B)
Repeat this block for each model, adjusting the `--model` flag.

```bash
# V1: Default Champion
export GENSIE_RAG_K=3 GENSIE_REASONING_LANG=Spanish GENSIE_HINT_COUNT=3
uv run python -m gensie.cli eval2 --data data/starter/ --pipeline stable-champion --model llama-3.2-3b-instruct --output results/llama_v1_default.json

# V2: Sparse RAG
export GENSIE_RAG_K=1 GENSIE_REASONING_LANG=Spanish GENSIE_HINT_COUNT=3
uv run python -m gensie.cli eval2 --data data/starter/ --pipeline stable-champion --model llama-3.2-3b-instruct --output results/llama_v2_k1.json

# V3: English Reasoning
export GENSIE_RAG_K=3 GENSIE_REASONING_LANG=English GENSIE_HINT_COUNT=3
uv run python -m gensie.cli eval2 --data data/starter/ --pipeline stable-champion --model llama-3.2-3b-instruct --output results/llama_v3_en.json

# V4/V5: Hint count variation
export GENSIE_RAG_K=3 GENSIE_REASONING_LANG=Spanish GENSIE_HINT_COUNT=1
uv run python -m gensie.cli eval2 --data data/starter/ --pipeline stable-champion --model llama-3.2-3b-instruct --output results/llama_v4_h1.json

export GENSIE_RAG_K=3 GENSIE_REASONING_LANG=Spanish GENSIE_HINT_COUNT=5
uv run python -m gensie.cli eval2 --data data/starter/ --pipeline stable-champion --model llama-3.2-3b-instruct --output results/llama_v5_h5.json
```

---

## 7. Data Collection Strategy

### Primary Metrics
- **Micro-F1 Score**: Calculated via `eval2` to measure overall extraction accuracy.
- **Total Tokens**: Monitored to evaluate the cost of multi-pass reasoning and RAG.
- **Success Rate (Status)**: Percentage of tasks that did not fail due to schema or timeout errors.

### Consistency Analysis
- **Domain Delta**: Compare F1 scores across `cultural`, `legal`, `medical`, and `technical` sub-directories in `data/starter/` to identify domain-specific strengths/weaknesses.
- **Error Characterization**: Utilize the `Errors` column in `eval2` output to categorize failures (e.g., False Positives vs. Null Rule violations).

### Comparison Method
Generate a final comparison table using the `leaderboard` tool:
```bash
uv run python -m gensie.cli leaderboard results/ --plain > results/experiment_summary.md
```

---

## 8. Validation Strategy
1. **Sanity Check**: Verify that `V0` (Baseline) matches historical results for `two-pass-ni`.
2. **Schema Compliance**: Ensure all models maintain >95% valid JSON output under the `stable-champion` configuration.
3. **Reasoning Audit**: Manually inspect a sample of 5 reasoning logs from `V3` (English) vs `V1` (Spanish) to determine if language choice impacts the "thought process" quality in SLMs.
