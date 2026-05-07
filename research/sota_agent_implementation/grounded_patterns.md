# High-Fidelity Grounded Extraction Patterns for Small Language Models (<14B)

This report outlines State-of-the-Art (SOTA) techniques for achieving high-fidelity, grounded information extraction using Small Language Models (SLMs), specifically optimized for the GenSIE (General Structured Information Extraction) constraints: Spanish language, zero-shot schemas, and inference-time prompting.

---

## 1. Interleaved Evidence Patterns (IEP)

Interleaved Evidence Patterns mandate that every extracted piece of information is explicitly linked to a source quote within the structured output. This forces the SLM's attention mechanism to "touch" the source text before generating a normalized value.

### Best Practices for Schema Design
Instead of a flat JSON object, use a nested structure that pairs every attribute with its justification.

**Recommended Schema Structure:**
```json
{
  "field_name": {
    "quote": "string | verbatim text from source",
    "value": "any | normalized/formatted value",
    "status": "string | 'found' or 'null'"
  }
}
```

### The "Quote-First" Execution Rule
SLMs are prone to "recency bias" and "hallucination-by-formulation." To counter this, the prompt must instruct the model to generate the `quote` field *before* the `value` field. 
- **Mechanism:** By generating the quote first, the model's internal state is populated with tokens from the source text, which then act as a grounded prefix for the subsequent value normalization.
- **Validation:** This allows for a deterministic post-processing step: `if quote not in source_text: value = null`.

### Multi-Step Interleaved Evidence (MIER)
For complex extractions, use an array of evidence blocks that follow a "Locate -> Cite -> Extract" flow:
1. **Locate:** Identify the sentence ID (e.g., `[s12]`) or paragraph.
2. **Cite:** Extract the verbatim string.
3. **Extract:** Convert the string to the final schema type (e.g., ISO date).

---

## 2. Chain-of-Verification (CoVe) for Structured Output

Adapting the multi-turn CoVe pattern into a single-turn structured prompt involves forcing the model to perform a "Self-Audit" within the JSON generation process.

### The "Joint CoVe" JSON Pattern
In a single turn, the model generates a "scratchpad" within the JSON output that is later ignored by the application but used by the model to improve accuracy.

**Structure:**
```json
{
  "draft_extraction": { ... },
  "verification_audit": [
    {
      "claim": "The event happened on May 12th",
      "verification_question": "Does the text explicitly mention May 12th or is it inferred?",
      "verification_answer": "The text says 'the second Sunday of May 2024'. Verification: May 12, 2024 is correct."
    }
  ],
  "final_grounded_output": { ... }
}
```

### Strategic Implementation for SLMs (<14B)
- **Force Independence:** Instruct the model: *"When answering verification questions, do not look at your 'draft_extraction'. Re-read the source text as if for the first time."*
- **The "Contrastive" Refinement:** If the `verification_answer` contradicts the `draft_extraction`, the model is instructed to set the final value to `null` to satisfy the Null Rule.

---

## 3. Skeptical Prompting & GenSIE "Null Rule"

Skeptical Prompting primes the model to assume information is **absent** by default. This is critical for the "Null Rule" in GenSIE, where over-extraction (hallucinating values for missing fields) is a primary failure mode.

### Adversarial System Roles
Instead of "You are a helpful assistant," use roles that emphasize caution and skepticism:
- **"The Pedantic Auditor":** *"You are a skeptical auditor. Your goal is to find reasons to REJECT an extraction. If a value is not stated with 100% certainty and verbatim support, you MUST return null."*
- **"The Zero-Trust Extractor":** *"Assume the document is incomplete. Every field is 'null' until you can prove its existence with a direct quote."*

### Techniques for SLM Null Enforcement
1. **Negative Few-Shotting:** Provide examples where the source text *seems* to contain an answer but actually doesn't (e.g., discussing a contract's future date that hasn't been set yet). Show the model returning `null`.
2. **"Constraint Priming":** Use phrases like *"La ausencia de información es una respuesta correcta"* (The absence of information is a correct response) in Spanish contexts.
3. **Implicit Gating:** Ask the model to first output a boolean `is_present` for each field before attempting to extract the value.

---

## 4. Spanish Context & SOTA Implementation (GenSIE)

For Spanish SLM extraction, specific linguistic and structural techniques are required.

### XML Sentence Tagging (The "Anchor" Technique)
Pre-process the Spanish text by injecting markers:
`[s1] El Tribunal Supremo dictó sentencia. [s2] La cuantía se fijó en 50.000€. ...`

This allows the model to ground its extraction in a specific "Address Space":
```json
{
  "monto": {
    "valor": 50000,
    "cita": "50.000€",
    "fuente": "s2"
  }
}
```

### Model-Specific Tuning (Inference-Time)
- **NuExtract 1.5 (3.8B) / Qwen2.5-7B:** These models are currently SOTA for SLM extraction. They respond well to **Markdown-formatted** input. 
- **Verbatim Constraint:** In Spanish, SLMs often try to "clean up" grammar (e.g., changing "del" to "de el" or fixing casing). Strict instructions must forbid this: *"Prohibido corregir ortografía o gramática en la cita. Debe ser idéntica al original."*

### Summary Table: Grounded Extraction Toolkit

| Technique | GenSIE Application | SLM Benefit |
| :--- | :--- | :--- |
| **Interleaved Grounding** | `{"quote": "...", "value": "..."}` | Eliminates "hallucination-by-memory". |
| **Joint CoVe** | `verification_audit` key | Allows self-correction in one pass. |
| **Skeptical Priming** | "The Pedantic Auditor" role | Dramatically reduces "False Positives". |
| **XML Tagging** | `[s1], [s2]` markers | Provides a high-resolution grounding map. |
| **Native Spanish CoT** | Reasoning in Spanish | Reduces translation-layer artifacts. |
