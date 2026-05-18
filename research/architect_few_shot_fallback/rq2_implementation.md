# Technical Implementation Details: Architect Few-Shot Fallback

This document outlines the implementation strategy for Research Question 2: "Technical Implementation Details of the Architect Few-Shot Fallback."

## 1. Synthesis Prompt Engineering

To generate high-quality synthetic examples, we use a "Golden Example" pattern. The prompt is designed to produce a "Teacher" level sample that serves as a grounding reference for the SLM.

### The "Synthesis Prompt" Template

```text
System: 
You are an expert data architect specializing in high-fidelity synthetic data generation for structured extraction tasks. 

Task:
Generate a single "Golden Example" consisting of a Spanish input text and its corresponding structured JSON output.

Inputs:
- JSON Schema: {{schema}}
- Extraction Goal: {{task_description}}

Requirements:
1. Spanish Text: Must be a realistic, nuanced, and natural paragraph or dialogue. It should be complex enough to exercise the schema's fields but clear enough for unambiguous extraction.
2. JSON Output: Must be 100% compliant with the provided JSON Schema. Every field defined in the schema that *can* be found in the text must be populated.
3. Language: The input text MUST be in Spanish.

Constraints:
- No conversational filler.
- No markdown code blocks (unless requested).
- Return a single JSON object with two keys: "input_text" and "ground_truth_json".

Output Format:
{{
  "input_text": "...",
  "ground_truth_json": {{ ... }}
}}
```

## 2. Integration: Updating `ArchitectModule`

The `ArchitectModule` will be extended with logic to manage synthetic examples.

### Proposed Class Structure (Python)

```python
import json
import hashlib
from typing import Dict, Any, Optional

class ArchitectModule:
    def __init__(self, teacher_model: str = "gemini-1.5-flash", slm_model: str = "llama-3.2-3b"):
        self.teacher_model = teacher_model
        self.slm_model = slm_model
        self.example_cache: Dict[str, Dict[str, Any]] = {}

    def _get_schema_hash(self, schema: Dict[str, Any]) -> str:
        schema_str = json.dumps(schema, sort_keys=True)
        return hashlib.md5(schema_str.encode()).hexdigest()

    def get_synthetic_example(self, schema: Dict[str, Any], task_description: str) -> Optional[Dict[str, Any]]:
        """
        Orchestrates the generation of a synthetic example.
        """
        schema_hash = self._get_schema_hash(schema)
        
        # 1. Check Cache
        if schema_hash in self.example_cache:
            return self.example_cache[schema_hash]
        
        # 2. Build Prompt
        prompt = self._build_synthesis_prompt(schema, task_description)
        
        # 3. Generate with Teacher Model
        response = self._call_llm(self.teacher_model, prompt)
        
        # 4. Parse and Validate
        try:
            example = self._parse_and_validate(response, schema)
            self.example_cache[schema_hash] = example
            return example
        except ValueError as e:
            # 5. Optional: One-shot Self-Correction
            return self._self_correct_synthesis(response, str(e), schema, task_description)

    def _parse_and_validate(self, response: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        data = json.loads(response)
        if "input_text" not in data or "ground_truth_json" not in data:
            raise ValueError("Missing required keys in synthetic output.")
        
        # Simple schema validation (or use jsonschema library)
        # validate(instance=data["ground_truth_json"], schema=schema)
        
        return data
```

## 3. Logic: Choice of Model

| Approach | Pros | Cons | Decision |
| :--- | :--- | :--- | :--- |
| **Same SLM (Self-Instruct)** | Fast, low cost, aligns with the SLM's "internal world". | High risk of hallucination or schema violation. | Not Recommended for Fallback. |
| **Larger Model (Teacher-Student)** | High quality, 100% schema adherence, natural Spanish. | Higher latency (first call only), higher cost. | **Recommended.** |

**Rationale:** Since the synthesis happens **once per schema** (cached across many inference calls), the overhead of using a "Teacher" model like Gemini 1.5 Flash or Pro is negligible compared to the boost in SLM performance provided by a high-quality few-shot example.

## 4. Error Handling & Robustness

### Self-Correction Flow
If the initial synthesis fails (invalid JSON or schema mismatch):
1. **Log the error.**
2. **Re-prompt the Teacher:** "Your previous output was invalid. Error: [Error Message]. Please regenerate the JSON correctly."
3. **Max Retries:** 1.

### Ultimate Fallback
If self-correction fails:
- **Fallback to Zero-Shot:** The `ArchitectModule` returns `None`. The champion agent then proceeds without the few-shot example, relying solely on reasoning hints.
- **Why?** It is better to have no example than a "broken" one that might confuse the SLM or cause it to crash during parsing.

## 5. Expected Impact
- **Structured Consistency:** Synthetic examples provide a "visual" template for the SLM, drastically reducing syntax errors.
- **Spanish Nuance:** By using a Teacher model, we ensure the SLM sees how Spanish idioms and context should be mapped to the JSON keys.
