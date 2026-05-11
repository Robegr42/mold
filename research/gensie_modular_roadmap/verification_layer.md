# Verification & Accuracy Layer: Research Report

## 1. Overview
The **Verification & Accuracy Layer** (the "Auditor") is a modular component designed to sit between the initial extraction engine and the final output in the GenSIE (General-purpose Schema-guided Information Extraction) pipeline. Its primary purpose is to cross-examine extracted fields against the source text to eliminate hallucinations and maximize the **Flattened Schema Score (Micro-F1)**.

By treating verification as a separate, pluggable stage, we can optimize the extraction stage for recall and the verification stage for precision.

---

## 2. Modular ReAct Verification Loop
A `ReAct` (Reasoning + Acting) loop allows the Auditor to perform targeted investigations for each extracted value.

### Architecture: The "Pluggable" Auditor
The Auditor is implemented as a wrapper or a post-processor that follows this interface:
```python
class VerificationLayer:
    def verify(self, source_text: str, raw_json: dict, schema: dict) -> dict:
        # 1. Flatten JSON to paths
        # 2. For each field: Run ReAct Loop
        # 3. Re-assemble and return
```

### Field-by-Field Verification Logic
Instead of verifying the entire JSON at once, the loop operates on individual "claims" (path-value pairs).

1.  **Thought:** "The extractor found 'Acme Corp' for `organization.name`. I need to find evidence in the text."
2.  **Action:** Search the `source_text` for the string "Acme Corp" or similar semantic variants.
3.  **Observation:** "Found in sentence: 'The merger with Acme Corp was finalized today.'"
4.  **Verdict:** If the context matches the schema definition, the value is **Confirmed**. If the text is missing or contradicts the value, the value is **Nullified**.

### Implementation Pattern
The loop can be implemented using a **State-Graph** (e.g., LangGraph) where each node represents a field verification.
-   **Entry:** Receive `raw_json`.
-   **Node (AuditField):** LLM analyzes a specific field.
-   **Node (Nullifier):** Logic to strip values that fail audit.
-   **Exit:** Return `verified_json`.

---

## 3. Timeout & Stop Conditions (60s Constraint)
In the GenSIE challenge, a strict 60s timeout is enforced per document. The Verification Layer must be "time-aware."

### Budgeting Strategies
| Phase | Allocation (Typical) | Logic |
| :--- | :--- | :--- |
| **Extraction** | 30s - 40s | Core extraction usually takes the most time. |
| **Verification** | 15s - 20s | The remaining budget is split across high-priority fields. |
| **Buffer** | 5s | Emergency exit to ensure JSON formatting and return. |

### Specific Stop Conditions
1.  **Elapsed Time Check:** Before starting the audit of any field, check `total_elapsed_time`. If `> 50s`, stop auditing and return the current state immediately.
2.  **Field Prioritization:** Not all fields are equal.
    -   **Priority 1:** Rigid Fields (Enums, Numbers, Booleans) — These have strict Exact Match requirements in Micro-F1.
    -   **Priority 2:** Nested Entity Keys — Verifying the 'name' of an entity often validates its children.
    -   **Priority 3:** Free-text Fields — These have semantic similarity thresholds (0.8), giving more leeway for small errors.
3.  **Max-Steps per ReAct Loop:** Limit each field's ReAct loop to 2 iterations (Thought/Action/Observation).

---

## 4. Nullify Logic & Flattened Schema Score
The **Flattened Schema Score (Micro-F1)** heavily penalizes hallucinations (False Positives). 

### The "Better Null than False" Principle
In Micro-F1 calculation:
-   **False Positive (FP):** Model extracts something that isn't in the ground truth. (Loss of Precision)
-   **False Negative (FN):** Model fails to extract something that is in the ground truth. (Loss of Recall)
-   **Null:** If the model returns `null` for a missing field, it is not a TP, but it is also not an FP.

**Strategy:** If the Auditor has <70% confidence in an extraction or cannot find a supporting quote, it should explicitly **Nullify** the field (set to `null` or remove the key).

### Implementation of Nullify Logic
1.  **Audit Prompt:** "You are an Auditor. Your job is to delete information that is not explicitly supported. If you cannot find a direct quote or a very clear inference for [Field], set its value to null. Accuracy is more important than completeness."
2.  **Structural Propagation:** If a required field (e.g., `person.name`) is nullified, the entire parent object (`person`) should be evaluated for removal to maintain schema integrity and avoid further FP penalties for sub-fields.
3.  **F1 Boosting:** By aggressively nullifying doubtful extractions, the system significantly raises its **Precision**. In the GenSIE 2026 metric, high Precision often leads to a higher Micro-F1 than high Recall with low Precision.

---

## 5. Summary Table for Modular Implementation
| Component | Responsibility | Pluggable Strategy |
| :--- | :--- | :--- |
| **JSON Flattener** | Convert JSON to list of field paths. | Pure Python utility. |
| **ReAct Auditor** | Field-by-field evidence retrieval. | LLM-based agent with `search_text` tool. |
| **Budget Manager** | Monitor 60s timeout. | Callback function/Wrapper class. |
| **Nullifier** | Strip unsupported fields. | Post-processing rule engine. |
