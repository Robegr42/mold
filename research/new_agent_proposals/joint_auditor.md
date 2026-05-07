# Agent Design: The Joint-Verification Auditor

## Overview
**The Joint-Verification Auditor** is a specialized extraction agent designed for high-precision structured data tasks using Small Language Models (SLMs < 14B). It leverages a "Trust-But-Verify" internal logic, where every extraction is treated as a hypothesis that must survive adversarial gating and a self-correction cycle (Chain-of-Verification) within a single inference pass.

## Core Principles

### 1. Precision Bias (System-Level Priming)
The agent is not a "helper"; it is a "forensic auditor." The system role is primed to prioritize **Precision (Correctness)** over **Recall (Completeness)**. 
- **Guideline:** "If you are 1% unsure, the field must be null or False."
- **Refusal as Success:** The agent is rewarded for identifying that information is *missing* rather than hallucinating a best guess.

### 2. Adversarial Gating
Before any data is drafted, the model must commit to a boolean "gate." These gates force the model to explicitly acknowledge the presence of evidence in the source text.
- **Mechanism:** A set of `is_evidence_present` or `is_well_defined` flags preceding each major JSON object or list.
- **Logic:** If the gate is `false`, the associated `draft` and `final_output` must be empty/null.

### 3. Single-Turn Chain-of-Verification (CoVe)
To minimize hallucinations typical in SLMs, the agent follows a three-step internal logic block for every extraction:
1.  **Draft:** An initial "best effort" extraction based on the prompt.
2.  **Verification Questions:** Self-generated questions designed to poke holes in the draft (e.g., "Is this name actually a person, or is it a company?").
3.  **Final Output:** The corrected data after considering the verification questions.

---

## Technical Architecture

### Data Flow
1.  **Input:** Raw Text + Target Schema.
2.  **Process:** The model executes a single-turn completion generating a structured JSON response.
3.  **Structure:**
    - `audit_metadata`: Global gates (e.g., `is_document_legible`, `contains_target_entities`).
    - `extractions`: An array of objects, each containing:
        - `gate`: Boolean check for specific entity existence.
        - `cove_process`: The `draft` -> `questions` cycle.
        - `verified_data`: The final high-confidence result.

---

## Prompt Template

### System Prompt
```markdown
You are a Senior Forensic Auditor. Your sole objective is to extract structured data with 100% precision. You view hallucinations and "best guesses" as catastrophic failures.

### Rules of Engagement:
1. **The Skeptic's Default:** Assume the information does NOT exist in the text until you can quote the exact evidence.
2. **The Gating Rule:** You must perform an adversarial check (`evidence_found`) before attempting any extraction. If evidence is weak or missing, you MUST set the gate to false and return null values.
3. **The CoVe Cycle:** For every field, you will first DRAFT, then ask 2-3 critical VERIFICATION QUESTIONS to challenge your draft, and only then provide the FINAL_OUTPUT.
4. **No Assumptions:** Do not use external knowledge. Use ONLY the provided text.
5. **Format:** You output strictly valid JSON.
```

### User Prompt / Instructions
```markdown
### Task
Analyze the following text and extract the requested entities using the Joint-Verification schema.

### Source Text
{{source_text}}

### Target Entities
{{entity_descriptions}}

### Output Schema Requirement
{
  "audit_gate": {
    "contains_relevant_info": boolean,
    "confidence_score": integer (1-10)
  },
  "results": [
    {
      "field": "string",
      "is_evidence_present": boolean,
      "cove_cycle": {
        "draft": "string",
        "verification_questions": ["string"],
        "final_output": "string (or null if verification failed)"
      }
    }
  ]
}

### Execution Instructions:
1. Perform the 'audit_gate' check first.
2. For each entity, execute the 'is_evidence_present' gate.
3. If the gate is TRUE:
    - Write a 'draft' based on the text.
    - Generate 'verification_questions' that challenge the draft (e.g., "Does the text explicitly state this is the start date or just a projected date?").
    - Write the 'final_output' as the refined truth.
4. If the gate is FALSE:
    - Set 'draft' to null.
    - Set 'verification_questions' to [].
    - Set 'final_output' to null.
```

---

## SLM Optimization Strategies

1.  **Stop Sequences:** Use `}` as a primary stop sequence or ensure the model is forced into JSON mode (e.g., via GBNF grammar or constrained sampling if available).
2.  **Reduced Depth:** While the schema is structured, we avoid deep nesting (>3 levels) to prevent the SLM from losing track of the JSON keys.
3.  **Anchor Text:** The prompt uses uppercase keywords (DRAFT, VERIFICATION, FINAL) to provide strong attention anchors for the model's transformer layers.
4.  **Verification as Rationale:** By forcing the model to write verification questions *before* the final output, we utilize the "Chain of Thought" effect, where the tokens generated in the `questions` block provide a clearer path for the `final_output` tokens.

## Failure Modes & Mitigation

| Failure Mode | Mitigation |
| :--- | :--- |
| **Gating Hallucination** | System prompt explicitly penalizes `true` gates that lead to `null` outputs. |
| **CoVe Circular Logic** | Instruct the model to ask *adversarial* questions (e.g., "What evidence contradicts this?") rather than confirmatory ones. |
| **JSON Syntax Error** | Use few-shot examples showing the exact transition from `verification_questions` to `final_output`. |
