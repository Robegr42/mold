# Impact Analysis: Schema Invariants in GenSIE

## 1. TypeScript compressed schema representation
The `InvariantPromptMixin` uses `compress_schema_to_ts` to present the target structure to the model.

### Advantages over JSON Schema:
*   **Token Efficiency:** JSON Schema is highly redundant (keys like `"type"`, `"properties"`, `"description"` repeat constantly). TypeScript interfaces are much more dense.
*   **Pre-training Alignment:** Models like Llama 3.2 3B have seen millions of lines of TypeScript in their training data. They naturally "understand" how to fill a TS interface.
*   **Structural Clarity:** Indentation and curly braces in TS are native "delimiters" that help the model parse the hierarchy of the requested data.

## 2. The "Strict Extract-or-Null" Rule
This invariant addresses the "Hallucination Trap" described in the GenSIE documentation (Section 3.1).

### Mechanism of Action:
*   **Precision Guard:** It explicitly authorizes the model to output `null`. Many models feel a "pressure to respond" and will hallucinate a "best guess" if they think an empty field is a failure.
*   **Grounding Enforcement:** By repeating this rule in the `EXTRACTION INVARIANTS` section, it remains in the model's short-term attention, overriding the default generative behavior.

## 3. Dialect Awareness
GenSIE focuses on Spanish texts from various sources (Wikipedia, blogs, news).

### Importance:
*   **Lexical Mapping:** The model needs to know that if the schema asks for "habitación" and the text says "cuarto", it is a valid extraction.
*   **Semantic Overlap:** This invariant prompts the model to use its internal multilingual/dialectal knowledge to bridge the gap between the schema's "Standard Spanish" and the context's local dialect.

## 4. Effectiveness in Current Results
*   The `two-pass` agent, which uses these invariants, has the highest precision (0.6909 on Starter).
*   The `grounded` agent, which also uses them and *further* mandates source quotes, has lower recall but high precision consistency. This confirms that the invariants are successfully steering the model toward "skeptical" extraction.

## 5. Potential Improvements
*   **Property-Level Invariants:** Instead of a global "Null Rule", add `// MUST be null if not in text` comments directly inside the TypeScript interface for sensitive fields.
*   **Dialect Examples:** Provide 2-3 common regional synonyms (e.g., `ordenador`/`computadora`, `coche`/`auto`) within the invariant description to "prime" the model's dialectal memory.
