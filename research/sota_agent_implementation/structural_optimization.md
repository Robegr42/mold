# Structural Optimization and Attention Management in SLMs

This report explores State-of-the-Art (SOTA) techniques for optimizing structured extraction in Small Language Models (SLMs < 14B), specifically focusing on **Recursive Schema Pruning**, **Skeleton-of-Thought (SoT)**, and **Compressed Formats**. These techniques are evaluated within the context of the GenSIE challenge (Spanish language, zero-shot schemas, inference-time only).

---

## 1. Recursive Schema Pruning (RSP)

### Concept
Recursive Schema Pruning is a dynamic prompt optimization technique that reduces a large, complex JSON schema into a minimal "active" subset based on the specific input text. For SLMs, where the attention mechanism is easily saturated by "schema noise" (irrelevant fields), RSP is critical for maintaining high F1 scores and reducing token costs.

### Mechanism
The RSP workflow for zero-shot extraction follows these steps:
1.  **Relevance Mapping (Pass 1):** A lightweight "router" (either a smaller model or a semantic search against schema field descriptions) identifies which top-level and nested keys are likely to be present in the source text.
2.  **Recursive Traversal:** The algorithm traverses the full JSON schema tree.
    *   If a node is marked as "irrelevant" and is not a `required` field, it is pruned.
    *   If a node is `required` but its children are irrelevant, only the mandatory skeleton is kept.
    *   $ref pointers are resolved only for the active branches.
3.  **Prompt Injection:** The pruned schema is injected into the final extraction prompt.

### Benefits for SLMs in Spanish
*   **Reduced Attention Noise:** Spanish text is often 20-30% more verbose than English. Pruning the schema compensates for this by freeing up the attention window.
*   **Mitigating "Lost-in-the-Middle":** SLMs (like Llama 3.2 3B) often struggle to extract fields defined in the middle of a large schema. Pruning ensures only high-salience fields exist.
*   **Handling Zero-Shot Complexity:** When a schema is provided zero-shot, the model must "learn" the structure on the fly. A smaller schema reduces the cognitive load of this learning.

---

## 2. Skeleton-of-Thought (SoT) for Extraction

### Adaptation for Structured Data
Traditionally used for parallelizing long-form generation, SoT is adapted for structured extraction to improve recall and reduce "extraction laziness."

**The Two-Stage Workflow:**
*   **Stage 1: Structural Outline (Skeleton):**
    *   **Prompt:** "Extract a list of all entity keys and the literal Spanish snippets from the text that provide evidence for them."
    *   **Goal:** Identify *where* the information is without worrying about the final JSON formatting.
*   **Stage 2: Schema Expansion (The Final JSON):**
    *   **Prompt:** "Using the identified snippets and the provided JSON schema, generate the final structured object."
    *   **Optimization:** This can be parallelized if the schema has independent top-level entities (e.g., `Patient` and `Doctor`).

### Why it works for Spanish SLMs
*   **Evidence Grounding:** By forcing the model to find the Spanish evidence first, it reduces hallucinations caused by the model trying to translate concepts into JSON keys prematurely.
*   **Coherence:** SLMs often lose track of the schema halfway through a long extraction. SoT provides a "map" (the skeleton) that the model follows in the second pass.

---

## 3. Compressed Formats & Attention Management

Small models like Llama 3.2 3B and Qwen 2.5 7B show varying performance based on the output format's "token density."

### Format Comparison (Ranked for SLMs)

| Format | Token Efficiency | SLM Reliability | Notes |
| :--- | :--- | :--- | :--- |
| **YAML** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 20-30% more efficient than JSON. Excellent for nested Spanish entities. |
| **JSON (Minified)** | ⭐⭐ | ⭐⭐⭐⭐⭐ | Standard for tool-calling models. Best adherence but high token overhead. |
| **Markdown Tables**| ⭐ | ⭐⭐ | Very expensive in tokens (`|`, `-`). Avoid for SLMs. |
| **Custom (||)** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Minimal noise but requires a few-shot example to work reliably. |

### Attention Management Strategies
1.  **Key Abbreviation:** In the prompt, map long schema keys (e.g., `descripcion_del_incidente`) to short aliases (e.g., `desc`). Map them back post-extraction.
2.  **Grammar-Constrained Decoding:** Use tools (e.g., `outlines`, `llama-cpp-python`) to force the model to follow the schema. This removes the "formatting" burden from the model's attention, allowing it to focus 100% on the Spanish context.
3.  **Delimiter Optimization:** Use `###` or `---` to clearly separate the Spanish source text, the schema, and the instructions. SLMs are highly sensitive to "context bleed" where they start including parts of the instruction in the extracted values.

---

## 4. Synthesis: SOTA Pipeline for GenSIE

For a Spanish zero-shot context with an SLM like Llama 3.2 3B, the most robust "Structural Optimization" pipeline is:

1.  **Pass 0 (RSP):** Prune the schema to only include fields with semantic relevance to the input text.
2.  **Pass 1 (Skeleton):** Extract a flat list of `(key, evidence_snippet)` in Spanish.
3.  **Pass 2 (Final):** Use the skeleton to populate a **YAML** structure (for efficiency) or **Minified JSON** (for reliability).
4.  **Language Guard:** Keep JSON keys in English (the language of the "structure") while ensuring values are extracted in the original Spanish.

---
*Sources: Ning et al. (2023) "Skeleton-of-Thought"; CDMizer Framework (2025); Lamini SLM Benchmarks.*
