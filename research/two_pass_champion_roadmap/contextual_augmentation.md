# Contextual Augmentation (RAG & Refinement) for Two-Pass Champion

**Target Framework:** GenSIE (General-purpose Schema-guided Information Extraction) Benchmark
**Architecture:** Two-Pass-NI (Non-Interactive: Reasoning Pass $\rightarrow$ Extraction Pass)
**Focus:** Small Language Models (SLMs) with ~32K Token Context Windows

This research document outlines the strategies for contextual augmentation, specifically focusing on Dynamic Few-Shot Retrieval, Token Budgeting, and the ARCHITECT Module, tailored for the Two-Pass extraction paradigm.

---

## 1. Dynamic Few-Shot Retrieval (FAISS/MiniLM) for Dual-Pass

In a Two-Pass architecture, the model's objective shifts significantly between passes. Therefore, the few-shot retrieval strategy must dynamically adjust to support *Analytical Reasoning* in Pass 1 and *Rigid Extraction* in Pass 2.

### A. Pass 1: Analytical Retrieval (The "Thinker")
*   **Goal:** Provide examples of how to traverse complex schemas, handle edge cases, and maintain grounded reasoning.
*   **Embedding Strategy (Dense - MiniLM):** Use dense semantic embeddings (e.g., `all-MiniLM-L6-v2`) focused on the **Schema Definition** and **Constraint Logic**.
*   **Retrieval Target:** Retrieve examples where the schema structure is similar (e.g., deeply nested objects, complex enums). The few-shot example should demonstrate a high-quality Chain-of-Thought (CoT) that explicitly discusses:
    *   How to map ambiguous text to strict enums.
    *   How to detect missing information (grounding/avoiding hallucinations).
*   **Example Prompt Output:** *"The schema asks for `sentiment` (enum: POSITIVE, NEGATIVE). The text says 'acceptable but flawed'. I must reason that this leans NEGATIVE based on the primary constraint."*

### B. Pass 2: Extraction Retrieval (The "Protocol Follower")
*   **Goal:** Provide examples of exact JSON syntax formatting, ensuring zero structural errors.
*   **Embedding Strategy (Sparse/Exact):** Use lexical matching (e.g., BM25) or schema-key overlap.
*   **Retrieval Target:** Retrieve examples that use the exact same field types (Dates, Arrays, Booleans). The example should show how to take the verbose CoT from Pass 1 and compress it into valid JSON.
*   **Example Prompt Output:** *`{"sentiment": "NEGATIVE"}`*

---

## 2. Managing the 32K Token Budget in Two-Pass-NI

The "Two-Pass-NI" architecture heavily strains the context window because Pass 2 must consume the original document, the schema, AND the generated reasoning from Pass 1. A strict token budget is essential.

### The Budget Equation
Assuming a hard limit of $L = 32,000$ tokens, the allocation formula for Pass 2 is:

$T_{total} = T_{system\_prompt} + T_{schema} + T_{document} + T_{pass1\_cot} + T_{few\_shot} + T_{output\_buffer}$

### Typical Allocation (GenSIE Use Case)
1.  **System Prompt & Schema Definition:** ~3,000 tokens (GenSIE schemas can be verbose).
2.  **Input Document:** ~15,000 tokens (Variable, but capped to leave room).
3.  **Pass 1 Reasoning (CoT History):** ~2,500 tokens.
4.  **Output Buffer (JSON):** ~2,500 tokens.
5.  **Subtotal Required:** ~23,000 tokens.

**Remaining Space for Few-Shot Examples:** **~9,000 tokens.**

### Maximum Allowed Examples
*   If an average high-quality few-shot example (Document Snippet + Schema + Reasoning + Output) is roughly 1,500 tokens.
*   **Maximum Limit:** $\lfloor 9,000 / 1,500 \rfloor$ = **6 Examples**.
*   **Safe Limit (85% Rule):** To avoid the "Lost in the Middle" attention degradation, the optimal number of examples is **3 to 4**.

**Dynamic Scaling Heuristic:** The orchestrator must calculate the token length of the input document *before* retrieving examples. If $T_{document} > 20,000$, the system must aggressively prune few-shot examples down to 1 or 0 to prevent context overflow.

---

## 3. Design of the `ARCHITECT` Module

The `ARCHITECT` is a lightweight, pre-processing module designed to generate schema-specific "Reasoning Hints" before Pass 1 begins. By analyzing the JSON Schema in isolation, it provides tactical advice to the SLM, reducing cognitive load and preventing common extraction failures.

### Core Functions of the ARCHITECT
1.  **Schema Ingestion:** It parses the JSON Schema, looking for specific data types, required fields, and nested hierarchies.
2.  **Constraint Distillation:** It translates formal JSON Schema rules (e.g., `pattern: "^\\d{4}-\\d{2}-\\d{2}$"`) into natural language hints (e.g., "Ensure dates are formatted as YYYY-MM-DD").
3.  **Grounded Warning Generation:** It flags fields that are prone to hallucination.

### The "Reasoning Hints" Schema Output
The Architect generates a structured set of instructions injected into the Pass 1 system prompt:

```json
{
  "structural_hints": [
    "The schema requires an array of 'Entities'. Ensure you scan the entire document for multiple occurrences, not just the first one.",
    "The 'location' field is a nested object requiring 'lat' and 'long'. If only a city name is provided, DO NOT hallucinate coordinates; emit null."
  ],
  "field_specific_hints": {
    "birth_date": "Requires ISO-8601 format. You must convert relative text like 'born 20 years ago' into an absolute date if the current year is known, otherwise emit null.",
    "status": "Strict Enum [ACTIVE, INACTIVE]. Map synonyms like 'working' to ACTIVE."
  },
  "grounding_warnings": [
    "CRITICAL: Do not use external knowledge. If the text mentions 'Apple' but does not explicitly state it is a technology company, do not fill the 'industry' field with 'Technology'."
  ]
}
```

### Integration into Pass 1
These hints act as an "Instructional Prefix." When Pass 1 begins its CoT reasoning, it uses the ARCHITECT's hints as an analytical checklist, ensuring that its logic aligns perfectly with the rigid constraints required by GenSIE before any final extraction is attempted.