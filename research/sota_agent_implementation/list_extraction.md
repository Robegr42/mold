# SOTA: Iterative and Exhaustive List Extraction for SLMs (< 14B)

This report summarizes State-of-the-Art (SOTA) approaches for exhaustive information extraction from lists using Small Language Models (SLMs) with less than 14 billion parameters. It focuses on techniques suitable for the GenSIE challenge: Spanish context, zero-shot schema adherence, and inference-time strategies.

## 1. Incremental Extraction Patterns

SLMs often suffer from "list fatigue" or "positional bias," where they stop extracting after a few items or miss the "tail" of a long list. Incremental patterns break the task into manageable sub-tasks.

### A. Stepwise / "Next Item" Loop
Instead of requesting all items at once, the model is prompted to find the *next* item relative to what has already been extracted.
- **Pattern:** 
  1. `Extract the first [Entity] from the text.`
  2. `I have already found [List]. Extract the very next [Entity] that appears AFTER [Last Item] in the text.`
- **Benefits:** Maximizes focus on local context; prevents the "lost in the middle" phenomenon.
- **Spanish Template:** 
  > "He extraído los siguientes elementos: [LISTA]. Revisa el texto y extrae el **siguiente** [ENTIDAD] que aparezca después de '[ÚLTIMO ELEMENTO]'. Si no hay más, responde 'FIN'."

### B. Sharding with Semantic Overlap
Divide the source document into chunks (e.g., 1000-2000 tokens) with a 10-15% overlap.
- **Why overlap?** To ensure entities or list items split across boundaries are not missed or truncated.
- **Deduplication:** A final "Reduce" pass or a deterministic logic step is used to merge items that appear in the overlap of two chunks.

### C. Field-by-Field / Nested Decomposition
For complex schemas, focus the model's entire attention on one specific field or one list item at a time.
- **SPIRES Pattern:** Extract top-level entity headers first, then recursively "interrogate" the model for details of each header.

---

## 2. Termination Signals

Explicit signals are crucial for automating the extraction loop and ensuring the model has "signed off" on the completeness of the task.

### A. Binary Completion Tokens
- **`[DONE]` / `[FIN]`**: Signals that the scanner has reached the end of the document and no more items exist.
- **`[CONTINUE]` / `[SIGUE]`**: Signals that the output token limit was reached or the model suspects more items remain, triggering a subsequent call.

### B. "Anything Else?" Sentinel
A prompt-based signal where the model must explicitly state "COMPLETE" or "FIN" if no new items are found in a refinement pass.
- **Best Practice:** Use a high-contrast token (like `###TASK_COMPLETE###`) to make it easily parsable by the agent logic.

---

## 3. Recursive Refinement (The "Omission Check")

Recursive refinement is the most effective way to improve **Recall** in SLMs without fine-tuning.

### A. The "Omission Identification" Pass
After the initial extraction, feed the output back to the model with the original text.
- **Prompt Pattern:** "Compare this list with the text. Identify any [Entity] mentioned in the text that is **not** present in the list. Provide only the missing items."
- **Spanish Implementation ("Truco de la segunda pasada"):**
  > "Revisa la lista anterior y compárala con el texto original. ¿Falta algún elemento? Si falta algo, lístalo ahora. Si la lista está completa, responde 'COMPLETA'."

### B. Self-Correction Loops
If the model's output fails a schema validation (e.g., missing a required field in a list object), the error message is fed back to the model to "fix" the specific object.

---

## 4. GenSIE Specific Strategies (Inference-Time)

### A. End-Anchored Prompting (Recency Bias)
To combat the "Lost in the Middle" problem, place the most critical instructions and the JSON Schema at the very end of the prompt.
- **Structure:** 
  1. System Role / Context.
  2. Long Source Text.
  3. **The Anchor:** Specific extraction instructions + JSON Schema + Output Format.

### B. Invariant Prompting
Ensure the extraction logic is robust against variations in the input text format or schema field order.
- **Canonicalization:** Use a post-processing layer or a strict grammar (e.g., Outlines, Guidance) to force the SLM to adhere to a schema, making the output "invariant" to the model's natural language tendencies.

### C. Spanish-Specific Nuances
- **Low Temperature:** Use `0.0` or `0.1` for high-precision extraction.
- **Delimiters:** Use `### TEXTO ###` and `### SCHEMA ###` as SLMs respond well to visual structure.
- **Few-Shot:** Providing 2-3 examples of Spanish extraction (Input -> List) significantly boosts performance in models < 10B (like Llama 3 8B or Qwen 7B).

## 5. Recommended Models for Spanish List Extraction (< 14B)
1. **Qwen 2.5 14B:** SOTA for multilingual structured extraction.
2. **Phi-4 (14B):** High reasoning capabilities for complex "hidden" entities.
3. **Llama 3.1 8B:** Robust Spanish support and excellent JSON formatting adherence.
4. **Mistral NeMo 12B:** Large context window (128k) suitable for long document list extraction.
