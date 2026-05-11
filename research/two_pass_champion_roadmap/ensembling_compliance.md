# Ensembling & Hosted Compliance: Two-Pass Champion Roadmap

This report evaluates the feasibility of high-N ensembling and the requirements for 100% hosted inference compliance within the context of the GenSIE (General-purpose Schema-guided Information Extraction) challenge and similar resource-constrained environments.

---

## 1. Ensembling Feasibility: N=3 vs. Survival Constraints

The "Two-Pass" architecture (Extraction + Verification/Refinement) is the current champion for accuracy. However, scaling this to an N=3 ensemble introduces significant overhead.

### Analysis of API Call Volume
| Configuration | Calls per Sample | 150 Samples (Total Calls) | Survival Risk (at 100 RPD) |
| :--- | :---: | :---: | :--- |
| **Two-Pass Baseline** | 2 | 300 | High (Exceeds daily quota) |
| **N=2 Two-Pass Ensemble** | 4 | 600 | Critical (Throttling likely) |
| **N=3 Two-Pass Ensemble** | 6 | 900 | **Extreme** (Immediate failure) |
| **N=3 Single-Pass Ensemble**| 3 | 450 | High |
| **N=1 Two-Pass (Early Exit)**| 1.2* | 180 | Sustainable |

*\*Assuming verification only triggers on low-confidence extraction.*

### Findings & Recommendations
1.  **Quota Constraints:** Under current Gemini 2.5 Pro limits (e.g., 5-15 RPM and ~100-500 RPD), an **N=3 Two-Pass ensemble (6 calls) is not feasible** for a "survival" strategy. It would exhaust daily quotas in less than 20-50 samples.
2.  **Latency vs. Reliability:** While N=3 provides the best "Majority Vote" stability, the additive latency of sequential Two-Pass logic ($T_{P1} + T_{P2}$) multiplied by the cost makes it a "brute-force" approach discouraged by GenSIE.
3.  **The "Survival" Roadmap Priority:**
    *   **N=2 with Tie-Breaker:** Prioritize an **N=2 ensemble** where the second pass acts as a cross-verifier. If Pass 1 and Pass 2 disagree, a third "Tie-breaker" call is made only as needed.
    *   **Single-Pass Verification:** Instead of full N=3 extraction, use **N=3 Verification**. Generate one extraction (Pass 1) and have three lightweight SLMs (e.g., 4-bit quantized Llama 3) vote on the validity of specific fields.

**Verdict:** The roadmap should prioritize **N=2 or a Single-Pass Verification** model to ensure completion of the evaluation set within the 24-hour window.

---

## 2. API-Native `json_schema` Compliance

To achieve "100% Hosted Compliance," the Two-Pass engine must be refactored to use native constrained decoding features (Structured Outputs). This eliminates "parsing retry" calls, saving significant quota.

### Refactoring Requirements by Provider

| Provider | Mechanism | Strictness Requirements |
| :--- | :--- | :--- |
| **OpenAI** | `json_schema` | `"strict": true`, `additionalProperties: false`, all fields `required`. |
| **Anthropic** | `tool_use` / `output_config` | `additionalProperties: false`, all fields `required`. |
| **Gemini** | `response_schema` | Supports `anyOf` and `$ref`. Requires `response_mime_type: application/json`. |
| **Together AI** | `json_schema` | Supports full JSON Schema including regex constraints. |

### Implementation Strategy for Two-Pass
1.  **Schema Transformation:** The engine must automatically inject `"additionalProperties": false` into every object level of the user-provided schema.
2.  **Null-Safety:** Since GenSIE requires `null` for missing information, all fields in the Pydantic models must be marked as `Optional` but included in the `required` array of the JSON Schema (mapping to `type: ["string", "null"]`).
3.  **Pass 2 Injection:** In the Verification pass, the model should be constrained to a *Correction Schema* that only allows outputs relevant to the errors found in Pass 1, rather than a full re-extraction.

---

## 3. Aggregation Logic: Medoid Embedding Similarity

When ensembling structured outputs, simple string merging often breaks JSON integrity. The **Medoid** approach ensures the final output is a valid, coherent JSON produced by one of the models.

### The Medoid Algorithm
Instead of an "average" (Centroid), which might not be valid JSON, we select the **Medoid**—the candidate JSON that is semantically closest to all others.

1.  **Vectorization:** Convert each valid JSON output $J_1, J_2, ... J_N$ into an embedding vector $V_i$.
    *   *Note:* Use a text-embedding model (e.g., `text-embedding-3-small`).
2.  **Distance Matrix:** Compute the pairwise **Cosine Similarity** between all vectors.
3.  **Centrality Score:** For each candidate $i$, calculate the sum of its similarities to all other candidates:
    $$S_i = \sum_{j=1}^{N} \text{sim}(V_i, V_j)$$
4.  **Selection:** The candidate with the **highest $S_i$** is selected as the representative output.

### Advantages for Two-Pass Merging
*   **Logical Consistency:** Unlike field-level voting, the medoid preserves cross-field constraints (e.g., if a `start_date` and `end_date` are logically linked, they are kept together from the same model).
*   **Outlier Rejection:** If one model hallucinates a completely different set of entities, its embedding will be distant from the cluster, and its $S_i$ will be low.
*   **Implementation:**
    ```python
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity

    def aggregate_medoid(json_candidates, embeddings):
        sim_matrix = cosine_similarity(embeddings)
        centrality = sim_matrix.sum(axis=1)
        return json_candidates[np.argmax(centrality)]
    ```

### Summary for Roadmap
The Medoid approach should be the default for N > 2. For N=2, the system should fall back to the "Pass 2" (Verification) output if it successfully validates the "Pass 1" output, as the verifier has the "final word."
