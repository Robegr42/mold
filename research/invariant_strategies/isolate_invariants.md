# Isolating Invariants for Modular Application

## 1. Isolating Invariants into Discrete, Reusable Python Components

To effectively construct multiple agent architectures that share a foundation of proven prompting strategies (invariants) while retaining their unique reasoning methodologies, we must isolate these invariants using established software design patterns. The two primary invariants identified are **TypeScript Compression** (converting verbose JSON schemas into compact TypeScript interfaces to save tokens and improve structural adherence) and **Extract-or-Null/Dialect-Aware prompt instructions** (strict grounding rules injected into the prompt).

These can be isolated using the following Python components:

*   **Utility Functions / Strategy Classes (Data Transformation):** TypeScript Compression is fundamentally a data transformation step. It does not depend on agent state. Therefore, it is best implemented as a pure utility function or a static method within a Strategy class. This makes it highly testable and reusable across any agent framework.
*   **Mixin Classes (Behavior Injection):** The "Extract-or-Null" and "Dialect-Aware" instructions are modifications to the base prompt. By utilizing Python's multiple inheritance via **Mixins**, we can seamlessly inject these prompt augmentation behaviors into any base agent class. The Mixin pattern allows an agent like `TwoPassReasoningAgent` to inherit standard LLM execution logic from a `BaseAgent`, while pulling in the invariant prompt formatting from an `InvariantPromptMixin`, avoiding deep, rigid inheritance trees.

## 2. Concrete Python Code Examples

### A. Utility for TypeScript Compression
This utility converts a standard JSON Schema into a compact TypeScript representation.

```python
def compress_schema_to_ts(schema: dict) -> str:
    """
    Compresses a JSON Schema dictionary into a concise TypeScript interface string.
    (Simplified for demonstration)
    """
    interface_name = schema.get("title", "Extraction")
    ts_def = f"interface {interface_name} {{\n"
    
    properties = schema.get("properties", {})
    required = schema.get("required", [])
    
    for key, val in properties.items():
        is_optional = "" if key in required else "?"
        # Map basic JSON Schema types to TS types
        js_type = val.get("type", "any")
        ts_type = "string" if js_type == "string" else "number" if js_type in ["integer", "number"] else "any"
        
        # Dialect awareness: explicit nullability
        ts_def += f"  {key}{is_optional}: {ts_type} | null;\n"
        
    ts_def += "}"
    return ts_def
```

### B. Mixin Class for Prompt Invariants
This Mixin handles the injection of the strict Extract-or-Null rules and the dynamically compressed TypeScript dialect.

```python
class InvariantPromptMixin:
    """
    A Mixin that injects core invariant instructions (Extract-or-Null, TS Dialect) 
    into an agent's base system prompt.
    """
    
    def apply_invariants(self, base_prompt: str, target_schema: dict) -> str:
        """
        Augments the given base prompt with strictly enforced invariants.
        """
        ts_schema = compress_schema_to_ts(target_schema)
        
        invariant_instructions = (
            "\n\n=== CORE EXTRACTION INVARIANTS ===\n"
            "1. STRICT EXTRACT-OR-NULL: You must only extract information explicitly stated in the source text. "
            "Do not infer, guess, or hallucinate. If the requested entity or field is not present, you MUST output `null`.\n"
            "2. DIALECT AWARENESS: Your response must strictly adhere to the following TypeScript interface dialect. "
            "Output ONLY valid JSON matching this structure, with no markdown wrappers unless specified:\n"
            f"```typescript\n{ts_schema}\n```\n"
            "===================================="
        )
        
        return f"{base_prompt}\n{invariant_instructions}"
```

## 3. Uniformly Mixing Invariants into Distinct Agent Architectures

By using the Mixin pattern, we can apply these invariants to radically different agent types without interfering with their core logic loops. The Mixin simply provides an `apply_invariants` method that the child agent calls right before dispatching the payload to the LLM.

### Base Agent Definition
```python
class BaseAgent:
    def __init__(self, llm_client):
        self.llm_client = llm_client
        
    def execute_prompt(self, prompt: str) -> str:
        # Mock LLM execution
        return self.llm_client.generate(prompt)
```

### Applying to `TwoPassReasoningAgent`
The `TwoPassReasoningAgent` separates reasoning (Chain of Thought) from extraction. It only needs to apply the invariants to the second (extraction) pass.

```python
class TwoPassReasoningAgent(InvariantPromptMixin, BaseAgent):
    def run(self, source_text: str, schema: dict) -> str:
        # PASS 1: Open-ended Reasoning (No invariants needed here)
        reasoning_prompt = f"Analyze the following text step-by-step to identify key facts:\n\n{source_text}"
        reasoning_output = self.execute_prompt(reasoning_prompt)
        
        # PASS 2: Strict Extraction (Invariants applied here)
        base_extraction_prompt = (
            f"Source Text: {source_text}\n\n"
            f"Analysis: {reasoning_output}\n\n"
            "Based on your analysis and the source text, extract the final data."
        )
        
        # Inject the invariants
        final_prompt = self.apply_invariants(base_extraction_prompt, schema)
        
        return self.execute_prompt(final_prompt)
```

### Applying to `SourceGroundedAgent`
The `SourceGroundedAgent` is a direct, single-pass agent. It applies the invariants immediately to its primary prompt.

```python
class SourceGroundedAgent(InvariantPromptMixin, BaseAgent):
    def run(self, source_text: str, schema: dict) -> str:
        # Single Pass logic
        base_prompt = (
            "You are a strict data extraction assistant. "
            f"Read the following source text carefully:\n\n{source_text}\n\n"
            "Extract the requested data according to the instructions below."
        )
        
        # Uniformly inject the same invariants
        final_prompt = self.apply_invariants(base_prompt, schema)
        
        return self.execute_prompt(final_prompt)
```

### Conclusion
By adopting Mixins (`InvariantPromptMixin`) and Utility transformations (`compress_schema_to_ts`), the extraction rules and schema minimization remain centralized (DRY - Don't Repeat Yourself). Any updates to how we enforce "Extract-or-Null" will immediately cascade to all agent architectures, while preserving their unique control flow and reasoning mechanisms.
