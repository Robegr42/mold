# GenSIE Challenge: Metric Alignment & Reliability

This report outlines strategies and insights for optimizing Small Language Model (SLM) performance in the GenSIE (General-purpose Schema-guided Information Extraction) task, with a focus on alignment with the "Flattened Schema Scoring" metric and ensuring reliability in Spanish extraction.

---

## 1. Metric Alignment: Flattened Schema Scoring (FSS)

The GenSIE challenge utilizes **Flattened Schema Scoring (FSS)**, reported as a **Micro-F1** score. This metric is designed to handle nested JSON structures while being robust to minor linguistic variations.

### Mechanics
- **JSON Flattening:** The hierarchical JSON output is decomposed into a set of `(path, value)` pairs.
  - *Example:* `{"patient": {"age": 30}}` → `("patient.age", 30)`.
- **Field-Specific Matching:**
  - **Rigid Fields (Boolean, Int, Float, Enum):** Require an **Exact Match**. Errors in these fields are penalized strictly.
  - **Free-text Fields (String):** Evaluated using **Semantic Similarity**.
- **The Similarity Threshold:**
  - A predicted string is counted as a "match" (True Positive) if its semantic similarity to the ground truth is **$\ge 0.8$**.
  - **Reference Model:** `paraphrase-multilingual-MiniLM-L12-v2` or similar Sentence-Transformers.
- **Aggregation:** Micro-F1 is calculated across all flattened paths in the dataset, ensuring that missing a parent key doesn't invalidate correct nested values if the path can still be resolved.

---

## 2. Strategies for Minimizing Hallucinations

GenSIE explicitly penalizes "Null Hallucinations" (extracting a value when the ground truth is `null`).

### A. "Extract-or-Null" Logic
To avoid false extractions, implement a strict "abstention" policy in prompts:
- **Explicit Instruction:** "If the information is not explicitly stated in the source text, return `null`. Do not guess or infer from external knowledge."
- **Low-Friction Exit Ramp:** Providing a specific, allowed value for missing data prevents the model from feeling "forced" to invent an answer.

### B. Negative Few-Shot Grounding
Include examples where the requested information is absent.
- **Example:**
  - *Snippet 1 (Present):* "Paciente de 45 años..." → `age: 45`
  - *Snippet 2 (Absent):* "El paciente ingresa estable..." → `age: null`

### C. Source-to-Value Grounding (Quoting)
Force the model to provide a supporting quote for every extracted value.
- **Instruction:** "For every field, first provide the exact snippet from the text, then the extracted value."
- **Benefit:** If the model cannot find a snippet to copy, it is significantly more likely to return `null`.

### D. Persona and Tone
Set a "Skeptical Auditor" persona. Instruct the model to prioritize **Precision over Recall**.
- **System Message:** "You are a data validation expert. Your goal is 100% precision. Only extract information that is explicitly grounded in the provided text. When in doubt, return null."

---

## 3. Self-Correction vs. Self-Consistency for SLMs

Small Language Models (<14B) face unique reliability trade-offs.

### Self-Consistency (SC)
- **Effectiveness:** High. Sampling multiple paths (N=3 to 5) and taking a majority vote (or the most frequent JSON structure) significantly reduces stochastic hallucinations.
- **Cost:** High (Linear increase in tokens/latency).
- **Use Case:** Critical fields where reliability outweighs cost.

### Self-Correction (SCo)
- **The Sycophancy Problem:** SLMs often agree with a "critic" prompt even if the original output was correct, leading to "correction-induced hallucinations."
- **Solution - Extrinsic Feedback:** Only trigger SCo when a structural error occurs (e.g., invalid JSON or schema violation). Provide the model with the specific error message (e.g., `Invalid type for 'age': expected number, got string`).
- **Intrinsic Correction:** Generally ineffective for SLMs without external grounding.

### Recommendation: Constrained Decoding
Instead of iterative correction, use **Constrained Generation** (e.g., Outlines, GBNF grammars). This guarantees 100% structural validity and schema adherence at 1x cost, allowing the model to focus its capacity on semantic extraction.

---

## 4. Handling Spanish Nuances

### A. Morphosyntactic Agreement
- **Gender and Number:** Spanish requires strict agreement (e.g., *El paciente* vs. *La paciente*). In extraction, SLMs must maintain the gender of the original entity to ensure correct coreference resolution.
- **Scoring Impact:** The 0.8 semantic threshold usually tolerates minor agreement errors (e.g., "médico" vs "médica") but may fail on pluralization if it changes the core meaning.

### B. Dialectal Variations
- **Lexical Diversity:** *Móvil* (Spain) vs. *Celular* (Latin America); *Ordenador* vs. *Computadora*.
- **Strategy:** Use **Dialect-Aware Prompting**. If the source region is known, mention it. Use multilingual embeddings (like the GenSIE reference model) which are typically robust to regional synonyms.

### C. Domain-Specific Terminology
- **Legal (Labour Law):** Focus on morphosyntactic patterns like *Noun + Adjective* (e.g., *contrato indefinido*). Note the lack of standardization in Spanish labour law; prioritize local context.
- **Medical:** Use specialized vocabularies like **SCOVACLIS** for clinical findings. Distinguish between *Observations*, *Findings*, and *Modifiers*.

---

## 5. Implementation Checklist for "Extract-or-Null"

1. **[ ] Schema Definition:** Set `default: null` for all optional fields in the JSON schema.
2. **[ ] Grounding Quote:** Add a `"source_quote"` field to the schema for every extracted entity.
3. **[ ] Thinking Step:** Use a "Thinking-First" approach:
   - Ask: "Is the information for field X present?"
   - If Yes: "Provide the quote."
   - Finally: "Extract the value."
4. **[ ] Multi-Pass Verification:** For high-stakes data, use a second SLM to verify: "Does the extracted value X match the provided quote Y? Yes/No." If No, set to null.

---
*End of Report*
