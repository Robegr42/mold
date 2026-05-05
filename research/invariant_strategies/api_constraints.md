# API Constraints & Implementation Review: Invariant Strategies

This report reviews the constraints and implementations required to apply our invariant strategies (TypeScript compression, Extract-or-Null prompt mixins, and Dialect-awareness) in a minimal, standard OpenAI-compatible API environment. The focus is specifically on optimizing offline Small Language Model (SLM) environments (like vLLM and SGLang) without relying on heavy orchestration frameworks.

## 1. Implementing Invariants with Generic OpenAI API Features

To ensure maximum portability across diverse providers and self-hosted inference servers, all strategies must be executed using purely generic Python constructs and the baseline `openai` client.

### TypeScript Compression
* **Implementation:** Instead of relying on proprietary structural enforcement limits or tool-calling frameworks, JSON/Pydantic schemas are serialized into terse TypeScript interface strings locally in Python. 
* **API Usage:** This TypeScript interface is injected via a string formatting operation directly into the standard `system` role message:
  ```python
  messages = [
      {"role": "system", "content": f"Extract data fitting this interface:\n{ts_schema}"},
      {"role": "user", "content": document_text}
  ]
  ```
* **Why it fits:** It utilizes the universal `messages` payload array without needing specific endpoints, avoiding complex structured parameter mappings that fail on legacy or minimally-compatible SLMs.

### Extract-or-Null Prompt Mixins
* **Implementation:** Append standardized, fallback-aware instructions directly into the prompt using Python string concatenation. For example, "Return exactly `null` if the required entities are not found in the text."
* **API Usage:** The API requires no special "failure mode" configurations. We handle the graceful degradation purely via context. When the model outputs `"null"` or `{ "result": null }`, standard Python `json.loads()` captures the empty state without raising extraction pipeline exceptions.

### Dialect-Awareness
* **Implementation:** Abstract system instructions into a Python dictionary mapping standard model identifiers (e.g., `llama-3`, `qwen`) to specific prompt formatting templates. 
* **API Usage:** Before calling `client.chat.completions.create()`, Python logic selects the correct string template based on the `model` parameter string. This bypasses the need for LangChain's `PromptTemplate` or LlamaIndex's prompt registries.

## 2. Limitations of Offline, SLM-Based Environments (vLLM, SGLang)

Both vLLM and SGLang have introduced robust OpenAI-compatible API layers, but they possess specific constraints regarding structured outputs (`response_format={"type": "json_schema"}`).

### How Structured Outputs Work
Recent versions of vLLM (v0.6.0+) and SGLang support the standard `response_format` payload. Under the hood, they use grammar-guided decoding backends (like **Outlines**, **XGrammar**, or **lm-format-enforcer**). 
* **vLLM:** Compiles the schema into a Finite State Machine (FSM) to mask invalid tokens during sampling.
* **SGLang:** Employs XGrammar by default for Jump-forward optimization and token mask caching.

### Key Limitations
1. **FSM Compilation Latency:** Extremely complex, deeply nested JSON schemas, or those with heavy `anyOf`/regex constraints, can incur significant initial latency spikes because compiling the parsing grammar is computationally heavy.
2. **Version Compatibility:** Older versions of vLLM do not support standard `response_format` and require proprietary `extra_body={"guided_json": schema}` arguments, breaking drop-in OpenAI compatibility.
3. **Context Window Pressures:** While structured generation prevents malformed output, it does not improve the model's *reasoning*. An SLM forced into a complex schema might hallucinate details just to satisfy the schema constraints if it doesn't understand the prompt.

### Fallback Strategies
If strict `json_schema` parsing fails or isn't natively supported:
* **Level 1 (JSON Object Mode):** Fallback to `response_format={"type": "json_object"}` alongside a strong `system` prompt ("Respond ONLY with valid JSON"). This doesn't enforce schema keys but guarantees JSON syntax.
* **Level 2 (Pure Prompting):** Omit `response_format` entirely. Rely on Few-Shot prompting and TypeScript compression within the system prompt to guide the model. Validate the raw string response locally using `json.loads` and Pydantic, executing a basic Python retry-loop if a `ValidationError` occurs.

## 3. Ensuring Independence from External Frameworks and the Internet

To guarantee these implementations are fully autonomous and functional in air-gapped environments:

1. **Standard Library & Minimal Dependencies:**
   * Use strictly `json`, `re`, `dataclasses`, or minimal `pydantic` for data validation. 
   * Exclude `langchain`, `llama_index`, `instructor`, or `marvin`. 
2. **Local Client Initialization:**
   * Initialize the `openai` client to point directly to the `localhost` inference server, ensuring no external telemetry or DNS lookups:
   ```python
   from openai import OpenAI
   client = OpenAI(base_url="http://localhost:8000/v1", api_key="local-offline-key")
   ```
3. **Python-Native Orchestration:**
   * **Retries:** Replace `Tenacity` or framework-level retries with simple `while` loops trapping standard `json.JSONDecodeError` or Pydantic validation errors.
   * **Prompt Chaining:** Pass the output of one API call as the string input to the `messages` array of the next. No DAGs, graphs, or external agentic state machines are required.
