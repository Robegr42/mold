# Structured Decoding & Schema Representation for GenSIE

This report summarizes research on state-of-the-art structured decoding techniques, their performance implications on high-end hardware like A100 GPUs, token-efficient schema representation formats, and compatibility with local OpenAI-style APIs.

---

## 1. State-of-the-Art Grammar-Constrained Decoding

Grammar-constrained decoding ensures that LLM outputs strictly follow a predefined format (e.g., JSON, YAML, or a custom grammar) by masking out invalid tokens at each sampling step.

### Key Engines and Technologies

| Engine | Core Mechanism | Primary Advantage | Best Use Case |
| :--- | :--- | :--- | :--- |
| **XGrammar** | Pushdown Automaton (PDA) + Adaptive Mask Cache | Highest throughput; near-zero per-token overhead. | Production serving (vLLM, SGLang, TensorRT-LLM). |
| **Outlines** | Finite State Machine (FSM) | High reliability and mature feature set (Regex, Lark). | Scenarios with complex Regex or fixed, reusable schemas. |
| **SGLang** | Compressed FSM (cFSM) + Jump-Forward | Skips model forward passes for deterministic strings (e.g., `{ "id": `). | Speed-critical applications where latency is the bottleneck. |
| **Guidance (LLGuidance)** | Lazy Automaton + Trie Slicer | Near-zero compilation time (no "TTFT tax"). | Dynamic or one-off schemas where every request is different. |
| **GBNF** | Character-level Stack (Context-Free Grammar) | Native to `llama.cpp` and GGUF format. | Local/CPU-based inference or edge devices. |

### Technical Evolution
1.  **Generation 1 (GBNF/Logit Bias):** Manual token manipulation or character-level parsing. High latency and CPU overhead.
2.  **Generation 2 (Outlines/FSM):** Pre-compilation of schemas into FSMs. Fast sampling but extremely slow startup/compilation (can be >30s for complex JSON).
3.  **Generation 3 (XGrammar/LLGuidance):** Lazy compilation and asynchronous masking. Handles large batch sizes and multi-GPU setups without stalling the GPU.

---

## 2. Impact on Inference Latency and Token Efficiency

### Hardware Performance (NVIDIA A100)
On A100 GPUs (80GB), the primary bottleneck for structured decoding was traditionally the **CPU-GPU synchronization**. The GPU would finish a forward pass and wait for the CPU to compute the valid token mask for the next step.

*   **Latency:** Modern engines (XGrammar) reduce this "tax" to ~10μs per token. This is negligible compared to the ~10ms forward pass of a 70B model.
*   **Throughput:** By utilizing bitmask tensors that stay on the GPU, high-throughput engines like **vLLM** can maintain 95%+ of their unconstrained throughput while enforcing strict schemas.
*   **A100 vs H100:** While A100 is highly capable, the H100's faster CPU-GPU link and FP8 support make it the superior choice for high-concurrency structured tasks.

### Token Economics
Structured decoding improves efficiency not by reducing the number of tokens generated, but by **eliminating wasted tokens**:
*   **100% Success Rate:** Guaranteed schema adherence means zero tokens are wasted on "failed" generations or retries.
*   **Entropy Reduction:** By narrowing the search space (masking), the model often converges on the next token with higher confidence, which can slightly reduce "thinking" time in some sampling algorithms.
*   **Jump-Forward Speedup:** SGLang can bypass model computation for structural tokens (brackets, keys), making constrained decoding **20-50% faster** than unconstrained text generation.

---

## 3. Token-Efficient Schema Representation Formats

Choosing the right format for **Schema Definition** (prompting) and **Data Representation** (output) significantly impacts cost and context window usage.

### Schema Definition (Prompting)
When telling the LLM *what* to generate, **JSON Schema** is the least efficient format due to its verbosity.

| Format | Relative Token Cost | Why? |
| :--- | :--- | :--- |
| **TypeScript (TS)** | 1.0x (Baseline) | Concise; LLMs are native-fluent in TS due to training data. |
| **Pydantic/Python** | 1.1x | Similar to TS; uses standard type hints. |
| **JSON Schema** | 3.5x | Extremely verbose keywords (`"properties"`, `"required"`, etc.). |

**Recommendation:** Use TypeScript interfaces or Pydantic models in the prompt to define the structure.

### Data Representation (Payload)
For the actual data being generated or stored:

*   **Minified JSON:** Standard for most APIs. Stripping whitespace saves ~30% compared to "pretty" JSON.
*   **YAML:** Saves 10-20% over JSON by removing braces and quotes. Highly readable for human review.
*   **Markdown Tables/Lists:** Can be 30% more efficient than JSON for flat, repetitive data.
*   **TOON (Token-Oriented Object Notation):** Specialized formats that define keys once and then stream values. Best for large arrays of objects.

---

## 4. Compatibility with OpenAI-Compatible APIs (Offline)

For offline environments (local servers), support for structured decoding varies by backend implementation.

| Server | Parameter | Support Level | Engine |
| :--- | :--- | :--- | :--- |
| **vLLM / Aphrodite** | `response_format` | Full (OpenAI Spec) + `guided_json` | XGrammar / Outlines |
| **Ollama** | `format` / `response_format` | Full (Supports Pydantic/JSON Schema) | Custom/Internal |
| **LM Studio** | `response_format` | Full (Supports `strict: true`) | GBNF / LLGuidance |
| **TGI** | `response_format` | Partial (Uses `value` field for schema) | Outlines |

### Best Practices for Offline Implementation
1.  **Standardize on `response_format`: { "type": "json_schema", ... }**: This is the most portable format across modern local servers.
2.  **Use "Strict" Mode:** Where available (vLLM, LM Studio), enable "strict" to ensure the engine uses grammar-based masking rather than just "hoping" the model follows instructions.
3.  **Schema Caching:** If using TGI or older Outlines-based servers, reuse the same schema for multiple requests to avoid the multi-second compilation delay.
