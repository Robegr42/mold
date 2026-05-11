# Ensembling & Compliance Optimization for GenSIE

This report outlines the technical strategy for implementing ensembling and ensuring compliance with hosted inference constraints in the GenSIE Champion modular roadmap.

## 1. Aggregation Logic Implementation

To maximize the stability of structured extraction, we employ a dual-layered aggregation strategy based on the data type of the fields.

### 1.1. Majority Vote (Enums & Booleans)
For categorical and boolean fields, **Field-Level Majority Voting** is the preferred method. This allows the pipeline to construct a "Consensus Object" by taking the most frequent value for each individual field across all ensemble members.

- **Mechanism:**
    1.  Collect $N$ validated Pydantic objects from the ensemble.
    2.  For each field in the schema:
        - If the field is an Enum or Bool, count occurrences.
        - Select the most frequent value (Mode).
        - **Tie-breaking:** If a tie occurs, default to the value from the "primary" (first) model run or the one with the highest self-reported confidence if available.
- **Benefits:** Handles cases where models agree on most fields but hallucinate or fail on one specific attribute.

### 1.2. Embedding Similarity (Free Text)
For free-text fields (e.g., descriptions, summaries), majority voting fails due to semantic variation (paraphrasing). We use **Medoid Selection via Embedding Similarity**.

- **Mechanism:**
    1.  Extract the free-text string from each ensemble member.
    2.  Generate semantic embeddings for each string (using a lightweight model like `all-MiniLM-L6-v2` or the API's embedding endpoint).
    3.  Calculate the **Centroid** (mean vector) of all embeddings in the set.
    4.  Compute the Cosine Similarity between each individual embedding and the Centroid.
    5.  Select the **Medoid**: The actual string whose embedding is closest to the Centroid.
- **Benefits:** This ensures the final output is a coherent, model-generated response (not a mathematical average of characters) that represents the semantic consensus of the ensemble.

---

## 2. API-Native JSON Schema Compliance

To ensure "Hosted Inference" compliance and move away from local-only tools like `llguidance`, the pipeline must utilize provider-native structured output features.

### 2.1. Implementation Strategy
We replace `llguidance` logic with a Pydantic-to-JSON-Schema bridge that targets the following API parameters:

- **OpenAI:** Use `response_format={"type": "json_schema", "json_schema": {"strict": true, "schema": ...}}`.
    - *Constraint:* Avoid using `default`, `format`, or `pattern` in the Pydantic model as OpenAI's "Strict" mode does not support them. These should be moved to the system prompt instructions.
- **Gemini:** Use `response_schema` in the `GenerateContentConfig`.
    - *Constraint:* Use Gemini 2.0+ to ensure support for nested objects and `anyOf` unions.
- **Generic Hosted (vLLM/Groq):** Use the standard `json_schema` tool-calling or response format if available.

### 2.2. Schema Sanitization
To maintain 100% compliance across different hosted providers, a "Sanitizer" should be implemented to:
1.  Strip unsupported JSON Schema keywords (e.g., `additionalProperties: false` is required by OpenAI but might be rejected by others).
2.  Convert complex Pydantic types (e.g., `EmailStr`, `FilePath`) to basic `string` types with instructions in the prompt.
3.  Ensure property ordering is preserved to help the LLM's autoregressive generation.

---

## 3. Optimal Ensemble Size & Performance Limits

The GenSIE task imposes a **32K token limit** and a **60s time limit**.

### 3.1. Ensemble Size Comparison: 2 vs. 3 Runs

| Metric | N=2 Ensemble | N=3 Ensemble |
| :--- | :--- | :--- |
| **Logic** | Requires perfect agreement (2-0) or fallback. | Allows for clear majority (2-1). |
| **Error Correction** | Weak; cannot resolve disagreements. | Strong; can filter out single-model hallucinations. |
| **Token Usage** | ~2x Input + 2x Output. | ~3x Input + 3x Output. |
| **Latency** | Parallel: $\max(T_1, T_2)$. | Parallel: $\max(T_1, T_2, T_3)$. |

### 3.2. Recommendation: N=3 (Parallel)
For the 32K context and 60s limit, **N=3** is the optimal size, provided the following conditions are met:

1.  **Parallel Execution:** Use `asyncio` or Threading to trigger all 3 requests simultaneously. The total latency will be bottlenecked by the single slowest request, which is typically well under 60s for modern providers (e.g., Groq at <10s, Gemini Flash at <15s).
2.  **Prompt Caching:** Utilize "Prompt Caching" (available on OpenAI and Gemini) to reduce the cost and TTFT (Time To First Token) for the 2nd and 3rd runs. This ensures that the 32K context is only processed "at full price" once.
3.  **Token Budgeting:**
    - With $N=3$, the total token usage is roughly $32K \times 3 \approx 96K$ tokens across all calls.
    - *Note:* If the 32K limit is *per task* (cumulative), then $N=1$ or $N=2$ with a smaller model is required. If the limit is *per request context*, $N=3$ is safe.
    - *Action:* If strict cumulative limits apply, use $N=2$ with a higher temperature for the first and a lower temperature for the second to find a "conservative" consensus.

## 4. Summary of Pipeline Stability
To maximize stability within GenSIE limits:
1.  Use **N=3 parallel runs** of a fast model (e.g., Gemini 1.5 Flash or Llama 3 70B on Groq).
2.  Apply **Field-level Majority Vote** for structured data.
3.  Apply **Centroid-Medoid selection** for free-text data.
4.  Ensure **API-native JSON constraints** are used by stripping non-standard Pydantic fields before schema conversion.
