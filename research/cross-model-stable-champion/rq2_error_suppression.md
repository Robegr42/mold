# Research Report: Research Question 2 (RQ2) - Cross-Model Error Suppression Profiles

## 1. Null-Rule Adherence (Negative Sample Handling)
The "Null-Rule" specifies that models must populate a field with a literal `null` value when the required information is absent.

*   **Llama-3.2-3B-Instruct:** Exhibits moderate adherence. Often falls victim to "pattern persistence," occasionally inventing values for null fields to maintain the JSON structure.
*   **Qwen-3-1.7B:** Shows the weakest adherence. Prone to outputting natural language placeholders (e.g., `"not found"`) instead of the literal `null` token, or skipping keys entirely.
*   **Gemma-4-E4B:** Demonstrates the highest reliability. Its larger capacity allows for better discrimination between absence of evidence and evidence of absence.

## 2. Parametric Hallucinations in Small Models
*   **Qwen-3-1.7B (High Risk):** Significant risk of injecting training data ("filling in the blanks" with common knowledge) when entities are missing from source text.
*   **Llama-3.2-3B & Gemma-4-E4B (Lower Risk):** Better grounding. Errors are more likely to be "contextual hallucinations" (misinterpreting text) rather than purely parametric injections.

## 3. Error Type Categorization: Schema vs. Semantic

| Model | Primary Failure Mode | Error Category |
| :--- | :--- | :--- |
| **Qwen-3-1.7B** | Structural Collapse (JSON Syntax) | Schema Violation |
| **Llama-3.2-3B** | Entity Miscategorization | Semantic Error |
| **Gemma-4-E4B** | Over-explanation/Verbosity | Semantic Error |

## 4. Effectiveness of the "Two-Pass-Null" Strategy
The **Two-Pass-Null** strategy is most effective for the **Qwen-3-1.7B** model.
*   **Mechanism:** Defaulting to `null` on Pass 1 vs Pass 2 disagreement suppresses the high hallucination rate of the 1.7B model.
*   **Impact:** Shifts the failure mode from "incorrect data" (low precision) to "missing data" (high precision).
