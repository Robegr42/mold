# GenSIE 2026: Top 5 Agent Implementations

Based on the research findings (summarized in `gensie_research_report.md`) and a review of the reference `BasicAgent` in `src/gensie/baseline.py`, this report proposes 5 new agent architectures. 

## Architectural Constraints & Alignment
Each proposed agent adheres to the following competition constraints:
1. **Offline & Zero-Shot:** Uses only the standard `openai` Python client targeting the local inference endpoint (`OPENAI_BASE_URL`). No internet-dependent frameworks (e.g., LangChain, LlamaIndex) are used.
2. **Model Agnostic:** We cannot assume the backbone model (Qwen, Llama, Salamandra) or rely on proprietary OpenAI model features. The agents use universally supported API features like generic system prompts, basic message formatting, and standard structured output requests where applicable.
3. **Subclassing:** Each approach is presented as a Python class inheriting from `GenSIEAgent` and implementing the `run(self, task: Task, model: str)` method.

---

## 1. Two-Pass "Reason-then-Extract" Agent (`TwoPassReasoningAgent`)

**Research Finding:** SLMs struggle with a "constraint tax" when forced to reason and output strict JSON simultaneously.
**Implementation:** This agent makes two consecutive API calls. The first call asks the model to freely reason about the text and identify values. The second call forces the JSON schema constraint, using the reasoning from the first call as context.

```python
class TwoPassReasoningAgent(GenSIEAgent):
    """
    Decouples reasoning from structured formatting by using a two-pass approach.
    Pass 1: Unconstrained analysis.
    Pass 2: Strict JSON formatting based on Pass 1.
    """
    def __init__(self):
        self.client = OpenAI(
            base_url=os.getenv("OPENAI_BASE_URL"),
            api_key=os.getenv("OPENAI_API_KEY", "sk-dummy"),
        )

    def run(self, task: Task, model: str) -> Dict[str, Any]:
        # Pass 1: Unconstrained Reasoning
        analysis_prompt = (
            f"Analyze the following text and identify all information relevant to this schema: {json.dumps(task.target_schema)}. "
            f"Think step-by-step in Spanish.\n\nText: {task.input_text}"
        )
        
        analysis_response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a data analysis expert. Analyze the text carefully."},
                {"role": "user", "content": analysis_prompt},
            ],
        )
        reasoning = analysis_response.choices[0].message.content

        # Pass 2: Constrained Extraction
        extraction_prompt = (
            f"Given the original text and the analysis below, extract the final JSON.\n"
            f"Original Text: {task.input_text}\n"
            f"Analysis: {reasoning}"
        )
        
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a precise data extraction agent. Output only valid JSON."},
                {"role": "user", "content": extraction_prompt},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {"name": "extraction", "schema": task.target_schema, "strict": True}
            }
        )
        
        return json.loads(response.choices[0].message.content)
```

---

## 2. Source-Grounded Agent (`SourceGroundedAgent`)

**Research Finding:** Hallucinations ("false extractions") are heavily penalized. Grounding responses in exact quotes mitigates this.
**Implementation:** Modifies the system prompt to explicitly enforce an "Extract-or-Null" logic, requiring the model to mentally verify quotes in the text before returning a value. 

```python
class SourceGroundedAgent(GenSIEAgent):
    """
    Forces the model to ground its extraction, heavily emphasizing 'Extract-or-Null' logic 
    to avoid hallucination penalties.
    """
    def __init__(self):
        self.client = OpenAI(
            base_url=os.getenv("OPENAI_BASE_URL"),
            api_key=os.getenv("OPENAI_API_KEY", "sk-dummy"),
        )

    def run(self, task: Task, model: str) -> Dict[str, Any]:
        system_instructions = (
            "You are a strict, skeptical data auditor. Your goal is to extract information into JSON. "
            "CRITICAL RULES: \n"
            "1. Only extract information explicitly stated in the source text. \n"
            "2. If a field's value cannot be confirmed with a direct quote from the text, you MUST return `null`. \n"
            "3. Do not guess, infer, or hallucinate values. "
        )
        
        prompt = task.get_input_prompt()

        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": prompt},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {"name": "grounded_extraction", "schema": task.target_schema, "strict": True}
            }
        )
        return json.loads(response.choices[0].message.content)
```

---

## 3. TypeScript Schema Agent (`TypeScriptSchemaAgent`)

**Research Finding:** TypeScript representations of schemas save 60-70% of prompt tokens compared to raw JSON Schema, significantly boosting the Performance-to-Cost ratio.
**Implementation:** Converts the `task.target_schema` into a pseudo-TypeScript representation before prompting, while still relying on standard JSON structured output from the API.

```python
class TypeScriptSchemaAgent(GenSIEAgent):
    """
    Increases token efficiency by converting verbose JSON Schemas into compact 
    TypeScript interfaces within the prompt context.
    """
    def __init__(self):
        self.client = OpenAI(
            base_url=os.getenv("OPENAI_BASE_URL"),
            api_key=os.getenv("OPENAI_API_KEY", "sk-dummy"),
        )

    def _schema_to_ts(self, schema: Dict) -> str:
        # Simplified pseudo-TypeScript conversion for token efficiency
        # In a real implementation, a recursive parsing function would be used here.
        return str(schema).replace('"', '').replace('{', '{\n').replace(',', ';\n')

    def run(self, task: Task, model: str) -> Dict[str, Any]:
        ts_schema = self._schema_to_ts(task.target_schema)
        prompt = (
            f"Extract data from the text to match the following TypeScript interface:\n"
            f"```typescript\n{ts_schema}\n```\n\n"
            f"Return the data as a valid JSON object.\n\nText: {task.input_text}"
        )

        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert at mapping text to TypeScript interfaces."},
                {"role": "user", "content": prompt},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {"name": "extraction", "schema": task.target_schema, "strict": True}
            }
        )
        return json.loads(response.choices[0].message.content)
```

---

## 4. Skeptical Auditor (Refinement) Agent (`SkepticalAuditorAgent`)

**Research Finding:** Multi-agent refinement (Analysis -> Draft -> Refine) significantly increases accuracy on complex free-text fields evaluated by semantic similarity.
**Implementation:** The agent generates a draft JSON, then passes the draft back to itself, acting as an auditor to "red-line" and remove hallucinated values.

```python
class SkepticalAuditorAgent(GenSIEAgent):
    """
    Uses a self-correction loop where the model audits its own draft extraction against the source text.
    """
    def __init__(self):
        self.client = OpenAI(
            base_url=os.getenv("OPENAI_BASE_URL"),
            api_key=os.getenv("OPENAI_API_KEY", "sk-dummy"),
        )

    def run(self, task: Task, model: str) -> Dict[str, Any]:
        # Step 1: Draft Extraction
        draft_response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Extract data into JSON."},
                {"role": "user", "content": task.get_input_prompt()},
            ],
            response_format={"type": "json_object"} # Using generic json_object for draft
        )
        draft_json = draft_response.choices[0].message.content

        # Step 2: Audit and Refine
        audit_prompt = (
            f"Source Text: {task.input_text}\n\n"
            f"Draft JSON: {draft_json}\n\n"
            f"Audit the draft JSON against the Source Text. If any value in the draft is NOT explicitly "
            f"supported by the text, change it to `null`. Output the final, corrected JSON."
        )

        final_response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a strict data auditor. Remove unsupported claims."},
                {"role": "user", "content": audit_prompt},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {"name": "extraction", "schema": task.target_schema, "strict": True}
            }
        )
        return json.loads(final_response.choices[0].message.content)
```

---

## 5. Dialect-Aware Baseline Agent (`DialectAwareAgent`)

**Research Finding:** Spanish dialectal variations (e.g., *móvil* vs *celular*) and morphosyntactic agreement are critical for the semantic similarity metric.
**Implementation:** A highly tuned, single-pass agent that modifies the standard `BasicAgent` prompt to make the model explicitly aware of Iberian and Latin American synonyms, ensuring high recall without adding extra API calls.

```python
class DialectAwareAgent(GenSIEAgent):
    """
    A highly-efficient, single-pass agent tailored for Spanish text nuances and dialectal variations.
    """
    def __init__(self):
        self.client = OpenAI(
            base_url=os.getenv("OPENAI_BASE_URL"),
            api_key=os.getenv("OPENAI_API_KEY", "sk-dummy"),
        )

    def run(self, task: Task, model: str) -> Dict[str, Any]:
        system_content = (
            "You are a precise data extraction agent specializing in Spanish texts. "
            "Pay close attention to dialectal variations (Iberian vs Latin American, e.g., 'ordenador'/'computadora') "
            "and domain-specific terminology. Link entities carefully respecting gender/number agreement. "
            "If an entity is present under a synonymous term, extract it using the schema's requested terminology. "
            "If the concept is absent, return `null`."
        )

        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": task.get_input_prompt()},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {"name": "dialect_extraction", "schema": task.target_schema, "strict": True}
            }
        )
        return json.loads(response.choices[0].message.content)
```
