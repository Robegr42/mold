# Strategies for Structured Information Extraction with LLMs

This document outlines various strategies and techniques for enforcing strict schema adherence (e.g., JSON) in Large Language Model (LLM) outputs, specifically focusing on methods that **do not require model fine-tuning or weight updates**.

## 1. Grammar-Constrained Decoding

Constrained decoding intervenes directly during the LLM's generation phase by modifying the probability distribution of the next predicted token, ensuring that the model can only generate tokens that conform to a predefined schema or grammar.

### 1.1 FST-FSA Composition
*   **Concept:** The target JSON schema is converted into a regular expression and then compiled into a character-level Finite-State Automaton (FSA). This is composed with a detokenizing Finite-State Transducer (FST) representing the LLM's specific vocabulary.
*   **Mechanics:** At each generation step, the resulting token-accepting FSA evaluates the allowed outbound edges. The logits of any tokens in the LLM's vocabulary that violate the schema constraints are masked out (set to negative infinity).
*   **Advantages:** Guarantees 100% schema adherence. Offline pre-computation of the FST/FSA reduces per-step inference overhead, making it highly efficient for smaller, locally hosted models.

### 1.2 CFG-Guided Decoding (SynCode, XGrammar, Outlines, Guidance)
*   **Concept:** Similar to FSA, but utilizes Context-Free Grammars (CFG) or optimized regular expressions to parse complex nested structures like JSON. 
*   **Mechanics:** Frameworks simultaneously parse the target schema and intercept the LLM's logits at each step. Tools like SynCode pre-compute a Deterministic Finite Automaton (DFA) mask store offline. During generation, an incremental parser tracks the partial output context and performs O(1) lookups in the mask store to filter invalid tokens. Other tools implement "token-healing" or "fast-forwarding" to accelerate generation.
*   **Advantages:** Provides zero-overhead or minimal-overhead constrained decoding, ensuring structural validity without sacrificing token generation speed.

## 2. Advanced Prompt Engineering Techniques

Structuring the prompt effectively can drastically improve an LLM's ability to follow formatting instructions without external constraints, which is especially useful when using API-based models.

### 2.1 End-Anchored Templates & Delimiter Separation
*   **Concept:** A prompt design methodology tailored for messy, long-context documents (like OCR'd PDFs or complex clinical reports).
*   **Mechanics:** 
    *   **Delimiters:** Use strict visual separators (e.g., `===` or `###`) to clearly segregate instructions from the raw input context.
    *   **End-Anchoring:** Place a fully-defined, blank JSON template (the target schema) at the *absolute end* of the prompt.
*   **Advantages:** Combats "context-loss" in smaller models by keeping the desired output structure as the freshest information in the context window right before generation begins.

### 2.2 Prompt Optimization (OPRO) with Rigid Formatting
*   **Concept:** Iteratively refining the natural language instructions within the prompt using an automated optimizer to maximize structural adherence.
*   **Mechanics:** Use "Follow the Format" (FF) or f-String templates to rigidly combine task instructions, the expected JSON schema, and the input context. An optimizer (like OPRO) proposes prompt variations and evaluates them based on JSON validation rewards.
*   **Advantages:** Can achieve near 100% JSON format compliance purely through optimized prompt wording and layout.

## 3. Retrieval-Augmented Generation (RAG) & Context Management

Managing the context provided to the LLM reduces hallucinations and helps the model focus on populating the schema accurately.

### 3.1 RAG-Augmented Few-Shot Extraction
*   **Concept:** Augmenting the prompt with highly relevant context chunks and meticulously crafted few-shot examples.
*   **Mechanics:** 
    1.  Chunk the source document and retrieve the top-K relevant chunks using Hybrid Search (e.g., Dense embeddings + BM25).
    2.  Inject a small, diverse set of input-output examples (few-shot) into the prompt to "lock in" the formatting behavior and edge-case handling.
*   **Advantages:** Few-shot examples effectively bridge the capability gap in smaller models, helping them map complex, messy context into strict JSON schemas reliably.

### 3.2 Domain-Ontology Filtering (Semantic Schema Injection)
*   **Concept:** Translating natural language into structured queries or objects by injecting only a relevant subset of a larger schema into the prompt.
*   **Mechanics:** A filtering module analyzes the user's query and extracts only the relevant subgraph/schema properties from a larger domain ontology. This lightweight "semantic schema" is injected into the prompt along with necessary syntax rules.
*   **Advantages:** Keeps the prompt concise and strictly within the model's limited context window. By providing strict ontological boundaries, it significantly reduces schema-agnostic hallucinations and information overload.