# Retroactive Architectural Plan: End-Anchored Agent

## 1. Objective
The **End-Anchored Template & Delimiter Separation** strategy is designed to improve the reliability and accuracy of structured data extraction, particularly when dealing with long input texts or complex schemas. 

The primary goals are:
*   **Recency Bias Exploitation:** By placing a blank JSON template at the very end of the prompt, we ensure the model's most recent context is the exact structure it needs to produce.
*   **Clear Contextual Boundaries:** Using consistent visual delimiters (e.g., `###`) to separate instructions, schema definitions, and source text, reducing the risk of the model confusing input data with instructions.
*   **Structural Guidance:** Providing a concrete "fill-in-the-blanks" template alongside the JSON schema to minimize structural errors and hallucinations.

## 2. Architecture
The `EndAnchoredAgent` follows a structured pipeline that combines sophisticated prompt engineering with OpenAI's native schema enforcement.

### Component Overview
*   **Agent Class:** `EndAnchoredAgent` (in `src/gensie/baseline.py`) acts as the orchestrator.
*   **Prompt Engine:** `format_end_anchored_prompt` (in `src/gensie/utils/prompts.py`) transforms task inputs into the final anchored format.
*   **Schema Enforcement:** Uses OpenAI's `json_schema` response format (Structured Outputs) to guarantee that the output matches the `Task`'s target schema.

### Flow Diagram
1.  **Task Input:** Receives a `Task` object containing `instruction`, `target_schema`, and `input_text`.
2.  **Template Generation:** `generate_blank_template` recursively traverses the JSON schema to create a skeleton JSON object.
3.  **Prompt Assembly:** `format_end_anchored_prompt` joins the components using delimiters.
4.  **Inference:** Sends the assembled prompt to the LLM with `strict=True` schema enforcement.
5.  **Parsing:** Standardizes the response into a Python dictionary.

## 3. Implementation Details

### Prompt Construction (`src/gensie/utils/prompts.py`)
The prompt is organized into four distinct sections separated by `###`:
1.  **INSTRUCTIONS:** The high-level goal of the extraction.
2.  **SCHEMA:** The full JSON schema definition for reference.
3.  **CONTEXT:** The raw input text from which data should be extracted.
4.  **RESPONSE TEMPLATE:** A specific instruction to "fill the following JSON template" followed by the `template_json`.

```python
# Example of the final prompt structure:
### INSTRUCTIONS
Extract all mentioned legal entities...

### SCHEMA
{ "type": "object", ... }

### CONTEXT
The contract was signed by...

### RESPONSE TEMPLATE
Please fill the following JSON template based on the CONTEXT above. Provide ONLY the JSON object.
{
  "entities": [
    {
      "name": "",
      "role": ""
    }
  ]
}
```

### Agent Logic (`src/gensie/baseline.py`)
The agent implements the `run` method:
*   It invokes `format_end_anchored_prompt`.
*   It configures the OpenAI client to use `response_format` with `type: "json_schema"`.
*   It includes a system message: `"You are a precise data extraction agent. Your output must be a valid JSON object following the provided template."`

## 4. Verification

### Testing Strategy
The implementation is validated via unit tests in `tests/test_end_anchored_agent.py`.

**Key Test Case:** `test_end_anchored_agent_uses_json_schema`
*   **Mocking:** Uses `unittest.mock.patch` to intercept OpenAI API calls.
*   **Validation:** 
    *   Verifies that `response_format` is set to `json_schema`.
    *   Ensures the `schema` passed to the API matches the task's `target_schema`.
    *   Confirms `strict: True` is enabled for guaranteed compliance.

### Execution
To run the verification:
```bash
pytest tests/test_end_anchored_agent.py
```

### Manual Inspection
The prompt structure can be inspected by calling `format_end_anchored_prompt` directly with sample data to ensure delimiters and template generation are functioning as expected.