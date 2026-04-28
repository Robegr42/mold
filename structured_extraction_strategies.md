# Strategies for Structured Information Extraction with Small Language Models (SLMs)

Small Language Models (SLMs) often lack the raw power and instruction-following consistency of Large Language Models (LLMs), making structured extraction (e.g., JSON adherence) a significant challenge. This report outlines advanced strategies, synthesized from recent research, to achieve high-fidelity structured output with SLMs without model fine-tuning.

## 1. Grammar-Constrained Decoding (Hard Constraints)

Constrained decoding interventions directly at the token-sampling level, ensuring that the model can only generate sequences that conform to a formal grammar or regular expression.

### 1.1 FST-FSA/PDA Composition
*   **Concept:** Treat the problem of tokenization mismatch as an automata theory problem. The character-level JSON schema (FSA/PDA) is composed with a detokenizing Finite-State Transducer (FST) representing the SLM's vocabulary.
*   **Mechanics:**
    *   At each step, the system computes a mask of valid tokens by traversing the resulting token-accepting automaton.
    *   Logits for invalid tokens are masked out ($-\infty$).
    *   Modern implementations (e.g., SynCode, Google DeepMind's FST-based constraints) are 7,000x faster than early methods, making them suitable for real-time SLM inference.
*   **Advantages:** Guarantees 100% schema adherence. Eliminates the need for "token-healing" hacks. Highly effective for SLMs that otherwise fail at syntax.

### 1.2 Speculative Constrained Decoding
*   **Concept:** Use an even smaller, faster "draft" model to generate token candidates that are filtered by constraints and then verified by the target SLM.
*   **Advantages:** Dramatically reduces inference latency while maintaining strict structural validity.

## 2. Reasoning-Guided Extraction (Thinking-First)

Leveraging the reasoning capabilities of SLMs (e.g., Qwen-2.5-Coder-1.5B) by allowing them to "think" before they "extract."

### 2.1 ThinkJSON (Chain-of-Thought Reasoning)
*   **Concept:** Require the model to output a reasoning block (`<think>`) before the actual JSON result (`<answer>`).
*   **Mechanics:**
    *   The prompt instructs the model to explain step-by-step how specific text segments map to individual JSON keys.
    *   This "self-checking" mechanism reduces hallucinations and improves field-mapping accuracy in complex documents.
*   **Application for SLMs:** SLMs often perform significantly better when given "workspace" to resolve mapping logic before committing to a rigid output format.

## 3. Advanced Prompt Engineering Patterns

SLMs are highly sensitive to prompt structure. Rigid templates can compensate for weaker instruction-following.

### 3.1 Follow the Format (FF) vs. f-String
*   **FF Prompting:** A highly rigid structure: `[Instructions] -> [Target Schema] -> [Context] -> [Output Trigger]`.
*   **f-String Prompting:** Variables are embedded naturally within instructions.
*   **Research Finding:** While larger models are flexible, SLMs often benefit from **FF Prompting** or "End-Anchoring," where the target schema is placed at the absolute end of the prompt to combat context-loss.

### 3.2 OPRO (Optimization by PROmpting)
*   **Concept:** Using a larger model (LLM) to iteratively optimize the instruction wording for the SLM based on performance on a validation set.
*   **Results:** OPRO-optimized prompts have achieved near 100% success rates on complex list-generation tasks with SLMs where baseline prompts failed entirely.

## 4. Context & Schema Management

Managing the "load" on the SLM's limited attention window.

### 4.1 RAG-Augmented Few-Shot Extraction
*   **Concept:** Retrieve similar extraction examples from a reference dataset and inject them into the prompt.
*   **Impact:** Seeing a "perfect" extraction of a similar document helps the SLM "lock in" the desired formatting and handle edge cases without needing a complex instruction set.

### 4.2 Domain-Ontology Filtering (Schema Pruning)
*   **Concept:** If the total target schema is large (e.g., hundreds of possible fields), use a lightweight module to extract only the relevant sub-schema for the current context.
*   **Impact:** Prevents "information overload" in the SLM's limited context window and reduces the probability of the model misinterpreting empty or irrelevant fields.

## 5. Hybrid Implementations

The most robust SLM extraction pipelines combine these strategies:
1.  **Schema Pruning** to reduce context noise.
2.  **RAG Few-Shot** to provide formatting anchors.
3.  **FF Prompting** with **End-Anchoring** for structural clarity.
4.  **Chain-of-Thought (ThinkJSON)** to handle logical mapping.
5.  **Grammar-Constrained Decoding** as a final "fail-safe" to ensure 100% parser-ready output.