# Agent Design: The Lexicon-Grounded Agent

## 1. Overview
The **Lexicon-Grounded Agent** is designed specifically for Small Language Models (SLMs < 14B) to perform high-fidelity structured extraction from messy, multi-lingual, or dialect-heavy text. It addresses the common SLM failure modes of hallucination, "schema-drifting" (inventing new Enum values), and loss of context.

### Design Goals
- **Veracity**: Every value must be justified by a quote.
- **Cross-Lingual Alignment**: Bridges the gap between Spanish source nuances and English schema requirements.
- **Strict Compliance**: 100% adherence to Boolean and Enum constraints.

---

## 2. Core Architecture

The agent operates as a **single-pass extraction engine** with a highly structured prompt that mimics a "Thinking -> Grounding -> Mapping" workflow.

### A. The "Quote-First" Object Structure
Unlike standard JSON extraction where the value is the primary key, Lexicon-Grounded extraction uses a wrapper object for every field.
- **Key Requirement**: The `verbatim_quote` key **must** appear before the `value` key in the JSON object.
- **Why?** This forces the model's auto-regressive generation to attend to the source text *before* it commits to a classification or transformation.

### B. Dialectal Hint Injection
Schema descriptions are augmented with "Lexical Bridges". For example, if the schema requires a "marital_status" Enum, the description includes Spanish synonyms (e.g., *soltero*, *casado*, *unión libre*) to help the SLM map regional variations to the correct English token.

### C. Binary Rigidity Enforcement
The agent employs "Negative Constraint Prompting" and "Value Capping". The prompt explicitly lists forbidden tokens (e.g., "None", "Maybe", "Unknown") for binary/enum fields to prevent the model from hedging.

---

## 3. Detailed Prompt Template

```markdown
### SYSTEM ROLE
You are a High-Precision Extraction Engine. Your task is to extract structured data from the provided TEXT into the specified JSON SCHEMA.

### EXTRACTION RULES (STRICT ADHERENCE REQUIRED)
1. **QUOTE-FIRST RULE**: For EVERY field in the JSON, you must first provide a `verbatim_quote` from the text that justifies the extraction, followed by the `value`.
2. **ZERO TOLERANCE**: For Boolean fields, use ONLY `true` or `false`. For Enum fields, use ONLY the provided options.
3. **NULL HANDLING**: If information is missing, set `verbatim_quote` to null and `value` to null.
4. **LANGUAGE BRIDGE**: Use the dialectal hints in the schema to map Spanish terms to English Enum values.

### SCHEMA
{
  "person": {
    "type": "object",
    "properties": {
      "full_name": {
        "type": "object",
        "properties": {
          "verbatim_quote": { "type": "string" },
          "value": { "type": "string" }
        }
      },
      "employment_status": {
        "type": "object",
        "description": "Hints: 'empleado' -> 'employed', 'desempleado/paro' -> 'unemployed', 'autónomo/cuenta propia' -> 'self_employed'",
        "properties": {
          "verbatim_quote": { "type": "string" },
          "value": { "type": "string", "enum": ["employed", "unemployed", "self_employed"] }
        }
      },
      "is_homeowner": {
        "type": "object",
        "description": "Hints: 'propietario/dueño' -> true, 'inquilino/alquiler' -> false",
        "properties": {
          "verbatim_quote": { "type": "string" },
          "value": { "type": "boolean" }
        }
      }
    }
  }
}

### TEXT
[INSERT TEXT HERE]

### RESPONSE FORMAT
Return ONLY valid JSON.
Example Structure:
{
  "person": {
    "full_name": { "verbatim_quote": "Juan Pérez", "value": "Juan Perez" },
    ...
  }
}
```

---

## 4. Implementation Strategies for Goals

### 1. Quote-First Rule Implementation
In the prompt's `RESPONSE FORMAT` section, provide a "Schema Skeleton" or a "One-Shot Example" that demonstrates the order. 
*   **Prompt Snippet:** `"Ensure that 'verbatim_quote' is the first key in every nested object. This is your evidence. Without evidence, the value is invalid."`

### 2. Dialectal Hint Injection Implementation
The hints are embedded in the `description` field of the JSON Schema. This utilizes the "Instruction Following" capability of SLMs by placing the mapping logic right next to the data field definition.
*   **Technique:** `"(Dialectal Hint: [Synonym 1], [Synonym 2] => [Target Value])"`
*   **Example:** For a field `risk_level`, the hint might be: `"(Hints: 'peligroso', 'riesgoso' -> 'high'; 'seguro', 'bajo' -> 'low')"`

### 3. Binary Rigidity Implementation
To enforce 100% adherence to Enums/Booleans:
*   **The "Forbidden" List:** Add a section: `### FORBIDDEN VALUES: Do not use 'N/A', 'Not Mentioned', 'Unknown', 'Maybe', or '0/1'. Use ONLY the specified Enum/Boolean types.`
*   **Boolean Mapping:** Explicitly state: `If the text implies a 'Yes', the value is 'true'. If 'No', 'false'.`
*   **Schema Constraints:** If using a framework like Pydantic, ensure the generated JSON schema includes `additionalProperties: false` and strict `enum` arrays.

---

## 5. Performance Expectations (SLMs)

| Feature | Impact on Llama 3.2 (1B/3B) | Impact on Hallucination |
| :--- | :--- | :--- |
| **Quote-First** | High: Anchors context window to text. | Reduces "invention" of data. |
| **Dialectal Hints** | High: Simplifies semantic mapping. | Reduces "Classification Errors". |
| **Binary Rigidity** | Moderate: Requires strong instruction following. | Eliminates "Schema Drift". |

## 6. Comparison with Baseline Agents

| Agent | Grounding Method | Constraint Handling |
| :--- | :--- | :--- |
| **Baseline** | Implicit (Internal weights) | Weak (Prone to chatting) |
| **Lexicon-Grounded** | **Explicit (Verbatim Quotes)** | **Rigid (Negative Constraints)** |
