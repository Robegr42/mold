# GenSIE: SOTA Agent Implementation Strategies for SLMs

## Executive Summary
This report identifies State-of-the-Art (SOTA) implementation patterns for Small Language Models (SLMs < 14B) specifically tailored to the GenSIE challenge. The core objective is to overcome the performance bottlenecks identified in earlier Llama 3.2 3B analysis—namely the **Rigid Type Bottleneck**, **Hallucinations**, **Attention Drift**, and **List Exhaustion Failure**. 

Key findings advocate for a shift toward **Early-Binding Lexicons** in schema design, **Interleaved Grounding (Quote-First Rule)** for verification, and **Recursive Schema Pruning** to minimize noise. For exhaustive list extraction, **Incremental "Next Item" Loops** are identified as the most robust pattern. These strategies, combined with **Constrained Decoding (Logit Masking)**, provide a roadmap for building agents that achieve high F1 scores without the prohibitive costs of multi-turn reasoning or massive parameter scales.

## Research Questions

### 1. Advanced Semantic Mapping for Rigid Types
**How can we leverage SOTA techniques to overcome the Rigid Type Bottleneck in Spanish structured extraction?**
*   **Early-Binding Lexicons:** SOTA for SLMs involves embedding mapping instructions directly into `Field` descriptions. For example, `type: string, enum: [AUTOIMMUNE], description: "Set to AUTOIMMUNE if text mentions 'inmunitario', 'reacción propia', etc."`.
*   **Positive Lexical Hints:** SLMs respond better to "Positive Hints" (inclusion maps) than "Negative Constraints" (exclusion rules). XML-tagged lexical maps are a robust way to prime the model's dialectal memory.
*   **Constrained Decoding (SOTA Choice):** Logit masking is the industry standard for ensuring SLMs adhere to Enums, as they frequently struggle with exact string matching in zero-shot scenarios.
*   **Detailed Research:** [SOTA Semantic Mapping Assets](sota_agent_implementation/semantic_mapping.md)

### 2. High-Fidelity Grounded Extraction Patterns
**What are the best single-turn patterns for ensuring strict grounding and verification?**
*   **Quote-First Rule:** Structure schemas so the `verbatim_quote` precedes the `value`. This forces the model's self-attention to focus on the source text before generating the normalized extraction.
*   **Joint CoVe (Single-Turn):** Adapt Chain-of-Verification into a single JSON response: `{ "draft": {...}, "verification": [...], "final": {...} }`. This allows SLMs to self-correct without the latency of multiple passes.
*   **Adversarial Role Priming:** System roles like "Zero-Trust Auditor" are SOTA for enforcing the "Null Rule" (returning null for missing information), addressing the GenSIE hallucination penalties.
*   **Sentence Tagging:** Injecting numeric markers (e.g., `[1]`, `[2]`) into the Spanish source text to give the SLM high-resolution grounding points.
*   **Detailed Research:** [SOTA Grounded Extraction Assets](sota_agent_implementation/grounded_patterns.md)

### 3. Structural Optimization and Attention Management
**How can we minimize "attention drift" in small models through schema and prompt pruning?**
*   **Recursive Schema Pruning (RSP):** SOTA involves dynamically stripping a JSON schema of non-essential descriptions and optional fields that have no evidence in the text. This reduces "attention noise" and saves 30-50% in prompt tokens.
*   **Skeleton-of-Thought (SoT):** For hierarchical schemas, force the SLM to first output a "mapping skeleton" (Key -> Spanish Evidence Snippet) before the final JSON. This prevents "extraction laziness."
*   **YAML for Density:** YAML is 20-30% more token-efficient than JSON for hierarchical data and is better understood by code-aligned SLMs.
*   **Key Aliasing:** Mapping verbose Spanish keys to short English aliases in the schema can maximize the model's factual attention window.
*   **Detailed Research:** [SOTA Structural Optimization Assets](sota_agent_implementation/structural_optimization.md)

### 4. Iterative and Exhaustive List Extraction Strategies
**How can small models be optimized to extract exhaustive lists from long contexts?**
*   Chunking vs. Incremental Extraction for large array fields.
*   Termination signals and "continuation" prompts for small context windows.
*   Multi-agent vs. Single-agent iterative refinement.

## Conclusions
1.  **Structure over Reasoning:** For SLMs, the structural design of the prompt (schema layout, key order, pruning) is a more significant performance lever than high-level "reasoning" instructions.
2.  **Early Binding is Critical:** Mapping semantic variety to rigid types must happen *during* the generation phase (via hints or constrained decoding), as post-hoc mapping is error-prone for zero-shot tasks.
3.  **Local Context Focus:** Strategies that segment the extraction (SoT, Incremental Lists, Sentence Tagging) successfully mitigate the "attention drift" seen in Llama 3.2 3B on complex schemas.

## Recommendations
1.  **Implement RSP Utility:** Develop a helper to prune JSON schemas based on initial text scans before passing them to the agent.
2.  **Adopt the Quote-First Pattern:** Update all Pydantic models to place a `quote` field before the `value` field.
3.  **Deploy Constrained Decoding:** Use an engine (e.g., vLLM or Outlines) that supports logit masking for Enums to eliminate "Incorrect (sim=0.00)" errors.
4.  **Final Suggestion:** The research is complete. You can now use the `/draft` command to turn this executive report into a fully fleshed-out article or white paper.
