# GenSIE Research: Pre-processing & Retrieval (RAG)

This document outlines the design and implementation strategy for the **Pre-processing & Retrieval (RAG)** component of the GenSIE Champion modular roadmap. The focus is on building a robust, offline-compatible system that optimizes Small Language Model (SLM) performance within a 32K token budget.

---

## 1. The `ARCHITECT` Module: Schema-to-Prompt Translation

The `ARCHITECT` module is responsible for translating technical JSON schemas into natural language instructions that SLMs (e.g., Llama-3-8B, Qwen-2.5-7B) can follow with high fidelity.

### 1.1 Instruction Mapping Logic

The module utilizes a recursive mapping function to convert JSON schema properties into structured instructions.

| JSON Schema Element | Natural Language Instruction Template |
| :--- | :--- |
| **`type: "string"`** | "Provide a text value for '{field}'." |
| **`type: "number"`** | "Provide a numeric value for '{field}'. Do not include units." |
| **`enum: [...]`** | "For '{field}', you MUST choose exactly one from: {list}." |
| **`required: [...]`** | "The following fields are MANDATORY: {fields}." |
| **`format: "date"`** | "Format the date as YYYY-MM-DD." |
| **`description`** | "{description}" (Used as the primary context for the field). |
| **`items` (Array)** | "Provide a list of {item_type}. Each entry should follow the format..." |
| **`minItems`/`maxItems`** | "Provide at least {min} and no more than {max} items." |

### 1.2 Handling Structural Complexity
*   **Hierarchical Nesting:** For nested objects, `ARCHITECT` uses indentation or markdown headers (e.g., `### Section Name`) to maintain structural clarity.
*   **Constraint Aggregation:** It groups constraints at the end of the field description. 
    *   *Example:* "priority (string): The urgency. Choose from [High, Medium, Low]. Mandatory."
*   **Negative Constraints:** For SLMs, explicitly stating what *not* to do is vital. The `ARCHITECT` adds a suffix: *"Do not include any conversational filler, markdown formatting outside the JSON block, or fields not defined in the schema."*

### 1.3 Best Practices for SLMs
*   **Schema Injection:** Rather than just showing the raw JSON, the `ARCHITECT` provides a "Human-Readable Schema Summary" which performs better for 7B-8B parameter models.
*   **Format Anchoring:** Always conclude instructions with: *"Response must be a single valid JSON object."*

---

## 2. Dynamic Few-Shot Retrieval Mechanism

To maximize accuracy while managing the token budget, GenSIE uses a dynamic retrieval pipeline that selects the most relevant examples from a local repository.

### 2.1 Embedding & Indexing (Offline)
*   **Model:** `all-MiniLM-L6-v2`. 
    *   *Why:* 80MB size, high speed on CPU, 384-dimensional vectors.
*   **Storage:** `FAISS` (Facebook AI Similarity Search).
    *   **Index:** `IndexFlatL2` for high precision on datasets up to 100k examples.
*   **Deployment:** Model weights and the FAISS binary index are baked into the Docker image to ensure 100% offline functionality.

### 2.2 Search Strategy: Similarity + MMR
GenSIE employs a two-stage retrieval process:
1.  **Similarity Search:** Retrieve the top $K$ (e.g., $K=50$) candidates using Euclidean distance (L2) from the FAISS index.
2.  **MMR Reranking (Maximal Marginal Relevance):** From the top 50, select the final $N$ examples (e.g., $N=5$) using MMR.
    *   **Formula:** $MMR = \arg\max_{D_i \in R \setminus S} [\lambda \cdot Sim(D_i, Q) - (1-\lambda) \cdot \max_{D_j \in S} Sim(D_i, D_j)]$
    *   **Goal:** Balance relevance to the query ($Q$) with diversity among selected examples ($S$). This prevents the context from being filled with redundant, near-identical examples.
    *   **Lambda ($\lambda$):** Set to `0.6` for an optimal balance of relevance and diversity.

### 2.3 Token Budget Management (32K Window)
With a 32K token budget, the system must carefully allocate space:
*   **Static Components:** System Prompt + Instructions + JSON Schema (approx. 1k - 3k tokens).
*   **Dynamic Component:** Input Document (can be large).
*   **Few-Shot Examples:** The remaining "slack" tokens.

**Budget Logic:**
1.  Calculate tokens for the Input Document and Instructions.
2.  Subtract from 32,000 to find `Remaining_Budget`.
3.  Add few-shot examples one-by-one (starting from highest MMR score) until either:
    *   The `Target_Count` (e.g., 5 examples) is reached.
    *   The next example would exceed 80% of the `Remaining_Budget` (leaving a safety buffer for generation).

---

## 3. Optimal Shot Count: Performance Trade-offs

Research indicates that the "Sweet Spot" for information extraction tasks with SLMs follows a clear curve.

### 3.1 Accuracy vs. Count
*   **0-shot:** High risk of formatting errors and hallucinated keys.
*   **1-shot:** Significant jump in accuracy (often +20%). Establishes the required JSON structure.
*   **3-5 shots:** Peak performance. Captures nuances in field extraction and diverse edge cases (e.g., how to handle missing data).
*   **8+ shots:** Diminishing returns. Performance may plateau or even degrade due to "attention distraction" (Few-Shot Collapse).

### 3.2 Latency and Cost
| Shot Count | Latency Impact | Token Cost | Recommendation |
| :--- | :--- | :--- | :--- |
| 1-shot | Low (+~100ms) | Low | Best for high-throughput batching. |
| **3-5 shots** | **Moderate** | **Medium** | **Recommended for GenSIE.** |
| 10+ shots | High (+1-2s) | High | Not recommended for 32k window. |

### 3.3 Recommendation for GenSIE
**Target 3-5 examples.** This range maximizes the F1-score for extraction while keeping the "prefill" time (encoding tokens) within acceptable limits for a local CPU/GPU environment.

---

## 4. Implementation Roadmap (Docker/Offline)

1.  **Environment Setup:**
    *   Include `sentence-transformers` and `faiss-cpu` in `requirements.txt`.
    *   Use a `DownloadModel` script during Docker build to cache `all-MiniLM-L6-v2`.
2.  **Indexing Service:**
    *   A Python service loads the FAISS index into memory on startup.
    *   Exposes a `retrieve(query, n)` method.
3.  **Architect Service:**
    *   Pure Python class that parses standard JSON schemas and returns a formatted string.
4.  **Integration:**
    *   The `InferenceEngine` calls `ARCHITECT` to get the base prompt.
    *   Calls `RetrievalService` for MMR-selected examples.
    *   Stitches the prompt together, respecting the 32K limit.
