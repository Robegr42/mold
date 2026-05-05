# Efficiency & Token Optimization for GenSIE

This report outlines strategies for maximizing the **Performance-to-Cost Ratio** in Generative Structured Information Extraction (GenSIE) tasks. The primary goal is to achieve high F1 scores while minimizing total token consumption (Input + Reasoning + Output).

---

## 1. Maximizing Performance-to-Cost Ratio (Token ROI)

The Performance-to-Cost ratio is defined as:
$$\text{Efficiency} = \frac{\text{Extraction Quality (F1 Score)}}{\text{Total Tokens Consumed}}$$

### Key Strategies:
*   **Model Routing & Cascading:**
    *   **Small Models first:** Use "budget-tier" models (e.g., GPT-4o-mini, Gemini 1.5 Flash, Llama 3 8B) for simple, high-confidence extractions.
    *   **Escalation Logic:** Only route complex, low-confidence, or multi-step extractions to "frontier" models (e.g., GPT-4o, Claude 3.5 Opus).
    *   **Task-Specific Models:** Utilize models fine-tuned for extraction (e.g., **NuExtract**, **GliNER**) which often outperform general-purpose models at smaller sizes.
*   **Batch Processing:**
    *   Use **Batch APIs** (OpenAI, Anthropic) for non-latency-sensitive tasks to get ~50% cost reduction.
*   **Context Caching:**
    *   For repetitive extraction from the same large document, use **Context Caching** (Gemini/Anthropic) to avoid paying for the same input tokens across multiple calls.
*   **Semantic Caching:**
    *   Store results of previous extractions in a vector database. If a semantically identical text segment appears, retrieve the cached extraction instead of re-processing.

---

## 2. Prompt Compression Techniques for IE

Information Extraction requires **verbatim accuracy**. Aggressive token pruning can be detrimental if it removes entity names or crucial qualifiers.

### Recommended Techniques:
*   **Extractive Compression (e.g., LongLLMLingua):**
    *   **Mechanism:** Identifies and keeps high-perplexity segments relative to the query.
    *   **IE Advantage:** Preserves original sentence structures and entity names better than abstractive (summarization-based) methods.
*   **Instruction-Aware Pruning:**
    *   Tailor the compression based on the schema. If extracting "Financial Totals," prioritize segments containing numbers and currency symbols.
*   **Prompt Minification (Natural Language):**
    *   **"Caveman Prompting":** Strip grammar, filler words ("in order to" -> "to"), and politeness.
    *   **Shorthand:** Use symbols like `&`, `w/`, `re:`, and standard abbreviations for common entity types.

---

## 3. Minimizing Reasoning Overhead: When is CoT Worth it?

Chain-of-Thought (CoT) provides a "thinking" buffer that improves accuracy but increases output tokens by **5x to 7x**.

### Decision Matrix:
| Complexity | Task Type | Recommendation |
| :--- | :--- | :--- |
| **Low** | Simple NER (Dates, Names, Locations) | **Avoid CoT.** Use Direct Extraction. |
| **Medium** | Logical Mapping (e.g., "Assign department based on context") | **Focused CoT.** Only reason about the ambiguous field. |
| **High** | Multi-step inference, self-correction, or conflicting data | **Full CoT.** High token cost is justified by accuracy gain. |

### Optimization: Focused CoT (F-CoT)
Instead of a full "Think through every step" prompt, use a **two-pass extraction**:
1.  **Pass 1 (Cheap Model):** Extract raw relevant snippets.
2.  **Pass 2 (Large Model):** Perform structured extraction from those snippets with minimal reasoning.

---

## 4. Efficient RAG & Dynamic Selection

For large schemas or massive few-shot libraries, "feeding the whole thing" is inefficient and leads to "lost in the middle" degradation.

### Dynamic Few-Shot Selection:
*   Use a **Retriever (BM25 or Embeddings)** to select the top 2-3 examples most semantically similar to the current input.
*   This keeps the prompt lean and provides the model with relevant "in-distribution" examples.

### Dynamic Schema Pruning:
*   **Schema RAG:** Embed the documentation for each field/entity in the schema. Retrieve only the relevant schema parts based on the input text.
*   **Two-Stage Selection:** Use a small model to predict which subset of the schema is relevant (e.g., "From these 100 fields, which 5 are in this receipt?"). Then, use a larger model to extract only those 5.
*   **Deterministic Filtering:** Use keyword matching (e.g., regex for dates/prices) to exclude schema parts that couldn't possibly exist in the text.

---

## 5. Token-Efficient Output Strategies

JSON is verbose due to repeated keys, quotes, and braces.

### Format Comparison (Token Savings vs JSON):
*   **YAML (10–20% savings):** Reduces braces and quotes but remains human-readable.
*   **Markdown-KV (30–40% savings):** Uses `Key: Value` format. Often the best balance of efficiency and LLM stability.
*   **TOON/TRON (40–60% savings):** Specialized notations (e.g., `users[2]{id,name}: 1,Alice 2,Bob`) that eliminate structural repetition.
*   **CSV/TSV (70–80% savings):** Best for tabular data with a flat schema.
*   **Schema Indexing:** Instead of returning full field names like `"purchase_order_number"`, instruct the model to use indices from the prompt: `"1": "PO-99"`.

### Minification:
*   Always instruct the model to produce **minified output** (no newlines/indentation) unless CoT is required.
*   Shorten keys in the schema definition (e.g., `cust_id` instead of `customer_identification_number`).

---

## Summary of Impact

| Technique | Estimated Token Savings | Impact on Quality |
| :--- | :--- | :--- |
| **Model Routing** | 60–90% (Cost) | Neutral to Positive |
| **Markdown-KV Output** | 30–40% | Neutral |
| **Dynamic Few-Shot** | 50–80% | Positive |
| **Focused CoT** | 60–70% (vs Full CoT) | Minimal Loss |
| **Context Caching** | 70–90% (Cost) | Neutral |
