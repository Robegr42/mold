# Research Question 2: Synthetic Example Generation Strategy for SLMs (GenSIE)

## 1. Model Hierarchy: The Teacher-Student Framework

### Teacher (Qwen 2.5 14B) vs. Student (Llama 3.2 3B)
In the GenSIE challenge context, where RAG similarity might be low (e.g., a completely new or niche schema), using a "Medium" model like **Qwen 2.5 14B** to synthesize a "Golden Example" for a "Tiny" model like **Llama 3.2 3B** is a highly effective fallback strategy.

*   **Logic:** The 14B model has a higher "instruction-following" ceiling and better zero-shot understanding of complex JSON schemas. It can "reason" about the schema fields and invent a plausible Spanish text that exercises all those fields.
*   **Latency Impact:**
    *   **Generation Overhead:** Synthesizing a 200-word text + JSON object with a 14B model typically takes 2–5 seconds (depending on hardware and quantization). This is added to the total pipeline latency.
    *   **Mitigation Strategy:** 
        *   **Schema Caching:** Since GenSIE uses schemas at inference time, we can compute a hash of the schema. If we've seen this schema (or a very similar one) before, we retrieve the previously synthesized "Golden Example" from a local cache (e.g., SQLite or Redis) instead of re-generating it.
        *   **Parallelization:** Start the synthetic generation as soon as the RAG retriever returns a "low confidence" score, while the Tiny model is still preparing its prompt context.

## 2. Self-Synthesis: Avoiding the "Hallucination Loop"

Research on models like **Salamandra 7B** (and other <7B SLMs) shows they are prone to "model collapse" and "hallucination loops" when asked to generate their own few-shot examples without external grounding.

### Risks in GenSIE
1.  **Schema Drift:** The model might generate a JSON field that "looks right" but isn't in the schema (e.g., generating `fecha_nacimiento` when the schema asks for `birth_date`).
2.  **Circular Reasoning:** If the model hallucinates a fact in the synthetic text, it will extract it into the JSON, creating a false sense of "correctness" that the model then learns as a pattern for the actual extraction task.

### Strategies for <7B Self-Synthesis
*   **Constrained Generation:** Use the schema's field descriptions as "mandatory anchors" in the synthesis prompt.
*   **Verification Pass:** Ask the model to "List all fields from the schema that are NOT present in your generated text." If the list is not empty, force a re-generation.
*   **Temperature Control:** Use a lower temperature (e.g., 0.2) for the JSON part of the synthesis and a higher temperature (e.g., 0.7) for the natural Spanish text to ensure linguistic diversity without sacrificing schema adherence.

## 3. Prompt Engineering: "Golden Example Synthesis"

To ensure Spanish fluency and 100% schema adherence, the prompt should follow a "Constraint-First" structure.

### Proposed Template (Spanish)

```markdown
### ROL: Experto en Generación de Datos Sintéticos para Extracción de Información
### TAREA: Generar un "Ejemplo Dorado" (Texto + JSON) para el siguiente esquema.

### ESQUEMA JSON:
{{schema_definition}}

### REGLAS CRÍTICAS:
1. El texto DEBE estar en español natural y fluido (evitar traducciones literales del inglés).
2. El texto DEBE contener información real/plausible para CADA campo definido en el esquema.
3. El JSON resultante DEBE ser 100% válido y seguir estrictamente las claves del esquema.
4. Si un campo es opcional y decides no incluirlo, usa `null`.
5. Usa codificación UTF-8 para asegurar el correcto tratamiento de tildes (á, é) y la letra 'ñ'.

### FORMATO DE SALIDA:
Presenta el resultado exactamente así:
---
TEXTO: [Tu texto en español aquí]
JSON: [Tu objeto JSON aquí]
---

### GENERACIÓN:
```

### Addressing the "Hallucination Trap"
The GenSIE challenge includes a "Hallucination Trap" where some fields cannot be answered by the text. To prepare the Student model for this, the Teacher should occasionally be prompted to:
*   *"Genera un ejemplo donde falten intencionalmente 2 campos del esquema, y asegúrate de que en el JSON esos campos sean `null`."*

## 4. Validation & Correction: Lightweight Implementation

### Step 1: Structural Validation (Pre-use)
Before the synthetic example is injected into the few-shot prompt of the Tiny model, it must pass a lightweight validation:
1.  **JSON Load Test:** `json.loads(output)` to catch syntax errors.
2.  **Schema Alignment:** Check if all keys in the generated JSON exist in the target schema.
3.  **Null-Check:** Verify that fields present in the text are not `null` in the JSON.

### Step 2: Self-Correction Pass (The "Trace" Method)
If validation fails, do NOT just ask the model to "Try again." Instead, provide the **Validation Trace**:
*   *Prompt:* "Tu JSON anterior es inválido. Error: Falta la clave 'monto_total'. Corrige el JSON manteniendo el mismo texto."
*   This specific feedback allows even a 3B model to fix formatting errors with high success rates (~90% improvement over generic retries).

### Step 3: Constrained Decoding (The "Nuclear" Option)
In a production-ready GenSIE agent, the synthetic JSON should be generated using **Outlines** or **GBNF grammars**. This bypasses the need for a correction pass by making it mathematically impossible for the model to generate a JSON that violates the schema.

## Summary Table: Strategy per Model Size

| Model Size | Synthesis Strategy | Validation |
| :--- | :--- | :--- |
| **3B (Tiny)** | Avoid self-synthesis; use cached examples or 14B Teacher. | GBNF / Constrained Decoding. |
| **7B (Small)** | Self-synthesis with "Checklist" prompting. | Pydantic + 1 Self-Correction pass. |
| **14B (Medium)** | Teacher for smaller models; high-diversity synthesis. | Pydantic + Multi-agent verification. |
