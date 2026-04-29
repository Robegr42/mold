# Reasoning-Guided Extraction Implementation Plan

## 1. Overview
The **Reasoning-Guided Extraction** strategy leverages Chain-of-Thought (CoT) prompting to improve the reliability of structured data extraction. By providing a dedicated space for reasoning (wrapped in `<think>` tags), the model can perform entity resolution, relationship mapping, and constraint checking before generating the final JSON output (wrapped in `<answer>` tags). This separation ensures that the internal monologue does not pollute the structured JSON while allowing the model to utilize its reasoning capabilities.

## 2. Architectural Impact
- **Agent Layer:** A new `ThinkingAgent` class will be added to `src/gensie/baseline.py`, inheriting from `GenSIEAgent`.
- **Prompting Layer:** A new utility function `format_thinking_prompt` will be added to `src/gensie/utils/prompts.py` to standardize the prompt structure.
- **Participant Registry:** The `OfficialParticipant` class will be updated to include the `reasoning-guided` pipeline, making it available for evaluation and production.
- **Parsing Logic:** The extraction process will transition from relying on API-level structured outputs to manual regex-based parsing of the model's raw text response.

## 3. Implementation Details for `src/gensie/baseline.py`

### Adding `ThinkingAgent`
A new class `ThinkingAgent` will be implemented to handle the reasoning-extraction lifecycle.

```python
import re
# ... existing imports ...

class ThinkingAgent(GenSIEAgent):
    """
    Agent that performs explicit reasoning before extraction using <think> and <answer> tags.
    """

    def __init__(self):
        self.client = OpenAI(
            base_url=os.getenv("OPENAI_BASE_URL"),
            api_key=os.getenv("OPENAI_API_KEY", "sk-dummy"),
        )

    def run(self, task: Task, model: str) -> Dict[str, Any]:
        """
        Executes extraction by requesting reasoning followed by structured output.
        """
        prompt = format_thinking_prompt(
            instruction=task.instruction,
            schema=task.target_schema,
            input_text=task.input_text,
        )

        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a precise data extraction agent that reasons step-by-step.",
                },
                {"role": "user", "content": prompt},
            ],
            # Note: We avoid response_format="json_object" because the output 
            # contains both reasoning tags and JSON.
        )

        content = response.choices[0].message.content
        return self._parse_response(content)

    def _parse_response(self, content: str) -> Dict[str, Any]:
        """
        Extracts the JSON content from <answer> tags using regex.
        """
        # 1. Try to find content within <answer> tags
        answer_match = re.search(r"<answer>(.*?)</answer>", content, re.DOTALL)
        
        if answer_match:
            json_str = answer_match.group(1).strip()
        else:
            # Fallback: If tags are missing, try to find the first JSON-like block or use the whole string
            json_str = content.strip()

        # 2. Clean up potential markdown code blocks
        json_str = re.sub(r"```json\s*|\s*```", "", json_str).strip()

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            return {
                "error": f"Failed to parse model response: {str(e)}",
                "raw_content": content
            }
```

### Updating `OfficialParticipant`
Modify the `OfficialParticipant` class to register the new pipeline.

```python
class OfficialParticipant(Participant):
    def __init__(self):
        self.pipelines = {
            "baseline": BasicAgent(),
            "end-anchored": EndAnchoredAgent(),
            "reasoning-guided": ThinkingAgent(), # New pipeline
        }

    def get_info(self) -> ParticipantInfo:
        return ParticipantInfo(
            team_name="MOLD Team",
            institution="University of Havana",
            pipelines=[
                # ... existing PipelineInfo entries ...
                PipelineInfo(
                    name="reasoning-guided",
                    description="Strategy using <think> and <answer> tags to perform Chain-of-Thought before extraction.",
                ),
            ],
        )
```

## 4. Details of `format_thinking_prompt` in `src/gensie/utils/prompts.py`

This function will be responsible for creating the prompt that instructs the model on how to use the tags.

```python
def format_thinking_prompt(
    instruction: str, schema: Dict[str, Any], input_text: str
) -> str:
    """
    Formats a prompt that encourages reasoning before extraction.
    """
    schema_json = json.dumps(schema, indent=2)
    
    prompt = (
        "You are tasked with extracting structured data from the following text.\n\n"
        f"### INPUT TEXT\n{input_text}\n\n"
        f"### EXTRACTION INSTRUCTIONS\n{instruction}\n\n"
        f"### TARGET SCHEMA\n{schema_json}\n\n"
        "### YOUR TASK\n"
        "1. Open a <think> tag.\n"
        "2. Analyze the input text step-by-step. Identify entities, resolve references, and plan the JSON structure.\n"
        "3. Close the </think> tag.\n"
        "4. Open an <answer> tag.\n"
        "5. Provide the final extracted JSON object strictly following the schema.\n"
        "6. Close the </answer> tag.\n\n"
        "Ensure that the content inside <answer> is ONLY the JSON object."
    )
    return prompt
```

## 5. Regex-based Parsing Logic
The `ThinkingAgent` will use the following regex patterns to isolate the data:

1.  **Reasoning Extraction (Optional/Logging):**
    `re.search(r"<think>(.*?)</think>", content, re.DOTALL)`
    *Used to capture the internal thought process for debugging or evaluation.*

2.  **Answer Extraction:**
    `re.search(r"<answer>(.*?)</answer>", content, re.DOTALL)`
    *Used to extract the raw string that should contain the JSON.*

3.  **JSON Sanitization:**
    `re.sub(r"```json\s*|\s*```", "", json_str).strip()`
    *Used to remove markdown formatting if the model wraps the JSON in triple backticks despite instructions.*

## 6. Verification Steps
1.  **Unit Testing:** Create a test script that passes a simulated LLM response (containing both tags) to the `_parse_response` method and verifies that it returns the correct dictionary.
2.  **Prompt Inspection:** Manually inspect the output of `format_thinking_prompt` to ensure the schema and instructions are correctly interpolated.
3.  **Integration Run:** Execute the `reasoning-guided` pipeline on a small sample of the `medical_diseases` dataset using `gensie-cli`:
    ```bash
    gensie-cli run --pipeline reasoning-guided --data data/dev/medical_diseases_01.json
    ```
4.  **Performance Comparison:** Compare the F1 scores of the `reasoning-guided` pipeline against the `baseline` and `end-anchored` pipelines using the `gensie-cli eval` command to ensure a measurable improvement in extraction quality.
