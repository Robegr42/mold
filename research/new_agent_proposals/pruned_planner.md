# Agent Design: The Pruned-Hierarchical Planner

## 1. Overview
"The Pruned-Hierarchical Planner" is a specialized agent architecture designed for high-accuracy structured extraction using Small Language Models (SLMs) with fewer than 14 billion parameters (e.g., Llama 3 8B, Mistral 7B). 

SLMs often struggle with large, complex JSON schemas because:
1.  **Negative Constraint Pressure:** The model wastes "attention" on fields that don't exist in the source text.
2.  **Format-Logic Conflict:** Small models often fail to maintain JSON syntax when simultaneously performing complex reasoning or searching for evidence.
3.  **Context Overload:** Dense schemas consume tokens that could be used for reasoning.

The Pruned-Hierarchical Planner solves this through a three-stage pipeline: **Recursive Schema Pruning (RSP)**, **Skeleton-of-Thought (SoT) Evidence Mapping**, and **Hierarchical JSON Synthesis**.

---

## 2. Phase 1: Recursive Schema Pruning (RSP)

### Logic
RSP is a pre-extraction pass where the model evaluates the source text against a full schema and "prunes" (removes) branches that are clearly absent. This minimizes the "search space" for the actual extraction phase.

### Mechanism
- The model is presented with the schema field descriptions and the source text.
- It identifies which top-level and mid-level keys have supporting information.
- It outputs a "Pruned Schema" or a list of "Active Fields".

### RSP Prompt Template
```xml
<system>
You are a Schema Architect. Your task is to analyze the provided [TEXT] and determine which fields from the [FULL_SCHEMA] are present. 
Output ONLY a JSON list of "active_fields" that have evidence in the text.
Include sub-fields only if the parent field is present.
</system>

<full_schema>
{{ schema_json }}
</full_schema>

<text>
{{ source_text }}
</text>

<instruction>
Identify active fields. Be conservative: if a field is not explicitly mentioned, omit it.
</instruction>
```

---

## 3. Phase 2: Hierarchical Planner (Skeleton-of-Thought)

The core extraction uses a **Skeleton-of-Thought (SoT)** approach. Instead of generating JSON directly, the model must first generate an "Evidence Map".

### Stage 1: Evidence Mapping (Key -> Quote)
The model identifies the specific fragment of text that justifies the value for every active field. This grounds the model in the source context before it commits to a specific data format.

### Stage 2: Attention Focus via XML
XML delimiters are used to separate the Reasoning/Evidence phase from the Synthesis phase. This keeps the model's KV cache focused on the relevant context for each step.

### Hierarchical Planner Prompt Template
```xml
<system>
You are a Precision Extraction Agent. Follow these steps:
1. <evidence_map>: For every field in the [PRUNED_SCHEMA], find the exact quote from [SOURCE_TEXT].
2. <json_synthesis>: Generate the final JSON using the quotes and required types.
</system>

<source_text>
{{ source_text }}
</source_text>

<pruned_schema>
{{ pruned_schema_output }}
</pruned_schema>

<task>
Generate the evidence map and then the JSON. Use the format:
<evidence_map>
- Field: "field_name" | Evidence: "..."
</evidence_map>

<json_synthesis>
{ ... }
</json_synthesis>
</task>
```

---

## 4. Detailed Pipeline Flow

1.  **Context Ingestion:** The agent receives `Source Text` and `Full Schema`.
2.  **RSP Pass:** 
    - SLM identifies active keys. 
    - *Programmatic Logic:* If `active_fields` are identified, a new temporary schema is constructed containing only those fields (plus mandatory ones).
3.  **SoT Planner Pass:**
    - The model generates the `<evidence_map>` section. This forces the model to "look" at the text again.
    - The model generates the `<json_synthesis>` section. Because the evidence is now in its immediate "local" context (the output buffer), the final JSON generation is more accurate and less prone to hallucination.
4.  **Validation:** The output is parsed. If `<json_synthesis>` is malformed, the `<evidence_map>` provides a high-quality "hint" for a retry pass.

---

## 5. Why this works for SLMs (< 14B)

-   **RSP reduces Token Load:** Large schemas can be 1k+ tokens. Pruning them down to 200 tokens saves context and reduces the model's confusion.
-   **SoT Decouples Reasoning from Formatting:** Generating JSON is a "syntactic task"; finding evidence is a "semantic task". Forcing them to happen sequentially (Evidence first) prevents the model from failing at syntax because it was struggling with semantics.
-   **XML Delimiters as Anchors:** XML tags act as strong structural markers that SLMs are trained on (especially Instruction-tuned models like Llama 3). They help the model transition between "Reading mode" and "Writing mode".
-   **Hierarchical Order:** By processing the schema from top to bottom (hierarchically), the model maintains the parent-child relationships more effectively than a "flat" extraction approach.

## 6. Comparison with Baseline

| Feature | Baseline Agent | Pruned-Hierarchical Planner |
| :--- | :--- | :--- |
| **Schema Handling** | Passes full schema every time. | Prunes schema based on text (RSP). |
| **Grounding** | Direct JSON generation. | Evidence Map (Key -> Quote) before JSON. |
| **Focus** | Unstructured prompt. | XML-delimited reasoning blocks. |
| **SLM Reliability** | High hallucination on missing fields. | Low hallucination; missing fields are pruned. |
| **Output Speed** | Faster (One pass). | Slower (Multi-step) but higher quality. |
