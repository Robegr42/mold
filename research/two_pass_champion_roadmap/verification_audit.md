# Post-Extraction Audit (ReAct Verification) for Two-Pass Champion

## Overview
This document outlines the strategy for implementing a **Post-Extraction Audit** using a **ReAct (Reasoning + Acting) Verification** loop. This audit serves as a third stage in the `Two-Pass-NI` (Negative Invariant) pipeline to further suppress hallucinations, specifically targeting the "Hallucination Traps" prevalent in the GenSIE challenge.

---

## 1. Modular Integration of the ReAct Verification Loop

To maintain the modularity of the `Two-Pass-NI` pipeline, the ReAct Auditor should be implemented as a separate "Verifier" component that acts upon the structured output of the second pass.

### Architectural Flow:
1.  **Pass 1 (Candidate Detection):** Identifies potential entities/slots.
2.  **Pass 2 (Refinement & Invariants):** Maps candidates to schema and applies Negative Invariants (NI).
3.  **Pass 3 (Audit Loop):**
    *   **Input:** Source Text, Pass 2 JSON, Schema.
    *   **Logic:**
        *   Identify "High-Risk" fields: Fields where Pass 2 changed a value significantly or where the model's confidence (if available) was low.
        *   Trigger ReAct: For each high-risk field, initiate a `Thought -> Action -> Observation` cycle.
        *   **Action:** Typically a `search_in_source(field_name, value)` or `verify_grounding(extracted_snippet)` tool call.
        *   **Observation:** The actual snippet or a confirmation that the value is missing.
    *   **Output:** Refined JSON with audited fields.

### Integration Strategy:
*   **Plug-and-Play:** The Auditor should expose a clean `audit(json_data, source_text)` interface. 
*   **Traceability:** Each field modified by the Auditor should include a reasoning trace (e.g., `_audit_log`) for debugging and transparency.

---

## 2. Optimal ReAct Cycle Budget (60s Limit)

Given the strict 60-second wall-clock limit and that `Two-Pass-NI` already consumes 2 API calls, the budget for the ReAct loop must be strictly managed.

### Latency Breakdown:
*   **Initial Overhead:** ~2s (Setup, pre-processing).
*   **Pass 1 (Detection):** 8s - 12s.
*   **Pass 2 (Refinement):** 10s - 15s.
*   **Total Consumed:** ~20s - 30s.
*   **Remaining Budget:** 30s - 40s.

### Recommended Budgeting:
*   **Cycle Limit:** **3 to 5 ReAct turns**.
*   **Parallelism:** Use "Batch-Verification" where the model is asked to verify multiple fields in a single "Action" step to maximize the utility of each call.
*   **Model Selection:** Use a faster, smaller model (e.g., Qwen2.5 3B or Llama 3.2 1B) for the Auditor to minimize TTFT (Time to First Token) and per-step latency.

---

## 3. Emergency Nullification Logic

In the GenSIE challenge, the penalty for a hallucination (filling a field not in text) is significantly higher than the penalty for a missing value (`null`). Thus, the system must prioritize safety when the 60s timeout is imminent.

### Implementation Pattern:
1.  **Global Timer:** Initialize a timer at the start of the entire extraction process.
2.  **The "Safety Buffer":** Set a hard stop at **T = 55 seconds**.
3.  **Logic at Timeout:**
    *   If the ReAct loop is active and hits the safety buffer:
        *   **Abort:** Immediately stop the current generation.
        *   **Nullify:** For any field that was *currently under audit* and not yet confirmed, force its value to `null`.
        *   **Fallback:** Return the last "Safe" version of the JSON (usually the output of Pass 2, with newly audited fields merged).
4.  **In-Prompt Instruction:** Include a system instruction for the Auditor: *"If you are running out of time, prefer outputting `null` for uncertain fields over guessing."*

### Logic Pseudo-code:
```python
def emergency_nullification(current_json, active_audit_fields, start_time):
    elapsed = time.time() - start_time
    if elapsed > 55:
        for field in active_audit_fields:
            current_json[field] = None # Force null for safety
        return current_json
    return current_json
```

---

## 4. Key Takeaways for "Two-Pass Champion"
*   **Precision over Recall:** The Audit loop's primary goal is to *remove* hallucinations (flip values to `null`) rather than finding new ones.
*   **Resource Management:** With only ~30s left for the third pass, every token counts. Use concise prompts and stop sequences to terminate the Auditor's thoughts early.
*   **Stability:** The Emergency Nullification ensures that the system always returns a valid JSON before the platform kills the process at 60s.
