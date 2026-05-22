import os
import json
import re
import hashlib
import numpy as np
import faiss
from typing import Any, Dict, List, Optional
from jsonschema import validate, ValidationError
from fastembed import TextEmbedding
from openai import OpenAI
from gensie.agent import GenSIEAgent, Participant, ParticipantInfo, PipelineInfo
from gensie.task import Task
from gensie.usage import UsageTracker
from dotenv import load_dotenv
from logging import getLogger

load_dotenv()
logger = getLogger("gensie")


def parse_robust_json(text: str) -> Dict[str, Any]:
    """
    Robustly extracts JSON from a string using multiple fallback strategies.
    Useful for models that include conversational noise or markdown blocks.
    """
    if not text or not text.strip():
        return {}

    # Strategy 1: Look for markdown code blocks
    code_block_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if code_block_match:
        try:
            return json.loads(code_block_match.group(1))
        except json.JSONDecodeError:
            pass

    # Strategy 2: Look for the first { and last }
    brace_match = re.search(r"(\{.*\})", text, re.DOTALL)
    if brace_match:
        try:
            return json.loads(brace_match.group(1))
        except json.JSONDecodeError:
            pass

    # Strategy 3: Attempt to parse the raw text
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        return {}


def compress_schema_to_ts(schema: Dict[str, Any], indent_level: int = 0, root_schema: Optional[Dict[str, Any]] = None) -> str:
    """
    Compresses a JSON schema into a concise TypeScript type representation.
    """
    if root_schema is None:
        root_schema = schema

    # Handle $ref
    if "$ref" in schema:
        ref_path = schema["$ref"]
        if ref_path.startswith("#/"):
            # Internal reference
            parts = ref_path.split("/")[1:]
            current = root_schema
            for part in parts:
                if part == "$defs" and "$defs" not in current and "definitions" in current:
                    part = "definitions"
                current = current.get(part, {})
            if current and current != schema:
                return compress_schema_to_ts(current, indent_level, root_schema)
        return "any"

    # Handle oneOf, anyOf, allOf
    for logic_key in ["oneOf", "anyOf", "allOf"]:
        if logic_key in schema:
            sub_schemas = schema[logic_key]
            sub_ts = [compress_schema_to_ts(s, indent_level, root_schema) for s in sub_schemas]
            # Filter out duplicates and 'any' if there are more specific types
            unique_ts = sorted(list(set(sub_ts)))
            if "any" in unique_ts and len(unique_ts) > 1:
                unique_ts.remove("any")
            
            separator = " | " if logic_key != "allOf" else " & "
            return separator.join(unique_ts)

    schema_type = schema.get("type", "any")
    
    # Handle Enum
    if "enum" in schema:
        enum_values = schema["enum"]
        return " | ".join([json.dumps(v) for v in enum_values])

    res = "any"
    if schema_type == "object":
        properties = schema.get("properties", {})
        required = set(schema.get("required", []))
        
        if not properties:
            if "additionalProperties" in schema:
                add_prop = schema["additionalProperties"]
                if isinstance(add_prop, dict):
                    res = f"Record<string, {compress_schema_to_ts(add_prop, indent_level, root_schema)}>"
                else:
                    res = "Record<string, any>"
            else:
                res = "Record<string, any>"
        else:
            lines = ["{"]
            indent = "  " * (indent_level + 1)
            for prop, prop_schema in properties.items():
                is_optional = "?" if prop not in required else ""
                prop_ts = compress_schema_to_ts(prop_schema, indent_level + 1, root_schema)
                
                # Add metadata as comments
                metadata = []
                if "format" in prop_schema:
                    metadata.append(f"format: {prop_schema['format']}")
                if "description" in prop_schema:
                    metadata.append(prop_schema["description"])
                
                comment = f" // {'; '.join(metadata)}" if metadata else ""
                lines.append(f"{indent}{prop}{is_optional}: {prop_ts};{comment}")
                
            lines.append("  " * indent_level + "}")
            res = "\n".join(lines)
        
    elif schema_type == "array":
        items = schema.get("items", {})
        item_ts = compress_schema_to_ts(items, indent_level, root_schema)
        if " " in item_ts or "\n" in item_ts:
            res = f"Array<{item_ts}>"
        else:
            res = f"{item_ts}[]"
        
    elif schema_type in ("integer", "number"):
        res = "number"
    elif schema_type == "string":
        res = "string"
    elif schema_type == "boolean":
        res = "boolean"
    
    return res


class InvariantPromptMixin:
    """
    Mixin that applies core architectural invariants to an agent's prompt:
    1. TypeScript compressed schema format
    2. Extract-or-Null rule
    3. Dialect Awareness rule
    """
    def apply_invariants(
        self, 
        base_prompt: str, 
        target_schema: dict,
        use_ts: bool = True,
        use_null: bool = True,
        use_dialect: bool = True,
        use_dates: bool = False
    ) -> str:
        ts_schema = compress_schema_to_ts(target_schema) if use_ts else json.dumps(target_schema, indent=2)
        
        sections = []
        if use_ts:
            sections.append(f"1. Target Schema (TypeScript Interface):\n```typescript\n{ts_schema}\n```")
        else:
            sections.append(f"1. Target Schema (JSON Schema):\n```json\n{ts_schema}\n```")
            
        if use_null:
            sections.append(f"2. Extract-or-Null Rule: Extract values that are explicitly stated or strongly implied by the context. If information is definitively absent or cannot be reasonably inferred, return `null`.")
            
        if use_dialect:
            sections.append(f"3. Dialect Rule: Respect Iberian/Latin American synonyms when extracting terms.")
            
        if use_dates:
            sections.append(f"4. Date Formatting Rule: Format all date and time fields according strictly to the schema's expected format (e.g., ISO 8601 YYYY-MM-DD or HH:MM:SS). Ensure lexical precision for these fields.")
            
        invariants = "\n\n--- EXTRACTION INVARIANTS ---\n" + "\n".join(sections)
        return base_prompt + invariants


class RAGModule:
    """Provides dynamic few-shot examples using semantic search (FAISS + FastEmbed)."""
    def __init__(self, data_path: str = "data/dev"):
        cache_dir = os.path.abspath("models")
        # Ensure cache directory exists
        os.makedirs(cache_dir, exist_ok=True)
        
        # We use FastEmbed's implementation of all-MiniLM-L6-v2
        self.model = TextEmbedding(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            cache_dir=cache_dir
        )
        self.index = None
        self.examples = []
        self._initialize_index(data_path)

    def _initialize_index(self, data_path: str):
        if not os.path.exists(data_path):
            logger.warning(f"RAG data path {data_path} not found.")
            return

        texts = []
        for filename in os.listdir(data_path):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(data_path, filename), 'r') as f:
                        data = json.load(f)
                        # We embed the instruction and input_text as the key
                        text = f"Instruction: {data.get('instruction', '')}\nText: {data.get('input_text', '')}"
                        texts.append(text)
                        self.examples.append(data)
                except Exception as e:
                    logger.error(f"Error loading RAG example {filename}: {e}")

        if texts:
            # FastEmbed's .embed() returns a generator of numpy arrays
            embeddings = list(self.model.embed(texts))
            embeddings = np.array(embeddings)
            
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(embeddings.astype('float32'))

    def get_few_shot_examples(self, task: Task, k: int = 3) -> List[Dict[str, Any]]:
        if self.index is None or not self.examples:
            return []
        
        query = f"Instruction: {task.instruction}\nText: {task.input_text}"
        # .embed() returns a generator, so we take the first item
        query_embedding = list(self.model.embed([query]))[0]
        
        D, I = self.index.search(np.array([query_embedding]).astype('float32'), k)
        
        return [self.examples[i] for i in I[0] if i < len(self.examples)]


class GatedRAGModule(RAGModule):
    """
    Extends RAGModule with a similarity gate.
    If the best match similarity is below the threshold, it returns no examples.
    """
    def get_gated_examples(
        self, 
        task: Task, 
        k: int = 3, 
        threshold: float = 0.55
    ) -> tuple[List[Dict[str, Any]], bool]:
        """
        Retrieves top k examples only if the best match exceeds the threshold.
        Similarity is calculated from L2 distance D as: similarity = 1 - (D/2)
        """
        if self.index is None or not self.examples:
            return [], False
        
        query = f"Instruction: {task.instruction}\nText: {task.input_text}"
        query_embedding = list(self.model.embed([query]))[0]
        
        D, I = self.index.search(np.array([query_embedding]).astype('float32'), k)
        
        if len(D[0]) == 0:
            return [], False
            
        best_distance = D[0][0]
        best_similarity = 1 - (best_distance / 2)
        
        if best_similarity < threshold:
            return [], False
            
        examples = [self.examples[i] for i in I[0] if i < len(self.examples)]
        return examples, True


class ArchitectModule:
    """Generates reasoning hints by analyzing the schema and instruction."""
    def __init__(self, client: OpenAI):
        self.client = client
        self._synthesis_cache = {}

    def get_reasoning_hints(self, task: Task, model: str, lang: str = "Spanish", count: int = 3, usage: Optional[UsageTracker] = None) -> str:
        prompt = (
            f"Analyze the following extraction schema and instruction.\n"
            f"Instruction: {task.instruction}\n"
            f"Schema: {json.dumps(task.target_schema, indent=2)}\n\n"
            f"Provide {count} brief, strategic reasoning hints in {lang} to help an extraction agent avoid common mistakes for this specific schema. "
            f"Focus on field dependencies and grounding."
        )
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert data architect."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200
            )
            if usage:
                usage.add(getattr(response, "usage", None))
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"ArchitectModule error: {e}")
            return "Analice el texto cuidadosamente y asegúrese de que cada campo esté respaldado por evidencia directa."

    def synthesize_example(self, task: Task, model: str, usage: Optional[UsageTracker] = None) -> Optional[Dict[str, Any]]:
        """
        Synthesizes a realistic training example (text + json) for a given task schema.
        Uses an in-memory cache keyed by the MD5 hash of the schema.
        
        Uses 'text' format to avoid complex JSON Schema compatibility issues with $defs nesting.
        """
        schema_str = json.dumps(task.target_schema, sort_keys=True)
        schema_hash = hashlib.md5(schema_str.encode()).hexdigest()

        if schema_hash in self._synthesis_cache:
            return self._synthesis_cache[schema_hash]

        system_prompt = "You are a senior data engineer specializing in high-quality synthetic data generation."
        user_prompt = (
            f"You are a Teacher model creating a high-quality training example for a data extraction task.\n\n"
            f"1. Target Schema:\n{json.dumps(task.target_schema, indent=2)}\n\n"
            f"2. Task Instruction: {task.instruction}\n\n"
            f"Your goal is to generate a realistic Spanish paragraph ('text') and a corresponding valid JSON object ('json') "
            f"that perfectly matches the schema above based on the information in your generated paragraph.\n\n"
            f"Respond strictly with a JSON object in a markdown code block containing two keys: 'text' (string) and 'json' (object)."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        content = None
        try:
            # Initial synthesis pass
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                response_format={"type": "text"}
            )
            if usage:
                usage.add(getattr(response, "usage", None))
            content = response.choices[0].message.content
            result = parse_robust_json(content)

            # Extra validation to trigger self-correction if keys are missing
            if "text" not in result or "json" not in result:
                raise KeyError("Missing 'text' or 'json' keys in synthesis result.")

            self._synthesis_cache[schema_hash] = result
            return result

        except Exception as e:
            logger.warning(f"Synthesis failed, attempting self-correction: {e}")
            # Self-Correction Pass
            correction_messages = messages + [
                {"role": "assistant", "content": content if content else "Error in generation"},
                {"role": "user", "content": f"The previous output was invalid or missing keys. Error: {str(e)}. Please try again, ensuring you return a JSON object with 'text' and 'json' keys in a code block."}
            ]
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=correction_messages,
                    response_format={"type": "text"}
                )
                if usage:
                    usage.add(getattr(response, "usage", None))
                result = parse_robust_json(response.choices[0].message.content)
                if "text" not in result or "json" not in result:
                    raise KeyError("Missing 'text' or 'json' keys after correction.")
                self._synthesis_cache[schema_hash] = result
                return result
            except Exception as final_e:
                logger.error(f"Synthesis self-correction failed: {final_e}")
        
        return None


class BasicAgent(GenSIEAgent):
    """
    Reference implementation using OpenAI Structured Outputs.
    Configurable via environment variables:
    - OPENAI_BASE_URL: (Optional) Custom endpoint for local LLMs.
    - OPENAI_API_KEY: (Required) Your API key.
    """

    def __init__(self):
        self.client = OpenAI(
            base_url=os.getenv("OPENAI_BASE_URL"),
            api_key=os.getenv("OPENAI_API_KEY", "sk-dummy"),
        )
        # Tallies token usage for the current task; the server reads it to set
        # the X-GenSIE-Token-Usage response header. Reuse this in your own agent.
        self.usage = UsageTracker()

    def run(self, task: Task, model: str) -> Dict[str, Any]:
        """
        Executes the extraction using OpenAI's response_format for strict schema compliance.
        """
        self.usage.reset()
        prompt = task.get_input_prompt()

        # Call OpenAI with the task's JSON schema
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a precise data extraction agent.",
                },
                {"role": "user", "content": prompt},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "extraction",
                    "schema": task.target_schema,
                    "strict": True,
                },
            },
        )
        self.usage.add(getattr(response, "usage", None))

        # Parse the structured JSON response
        try:
            content = response.choices[0].message.content
            result = json.loads(content)
            # Inject token usage
            if hasattr(response, "usage") and response.usage:
                result["_tokens"] = response.usage.total_tokens
            return result
        except (json.JSONDecodeError, AttributeError, IndexError) as e:
            # Fallback for unexpected API errors
            return {"error": f"Failed to parse model response: {str(e)}"}
        except Exception as e:
            logger.error(str(e))
            return {"error": str(e)}


class MIRAAgent(GenSIEAgent, InvariantPromptMixin):
    """
    Agent that uses a two-pass strategy:
    1. Unconstrained analysis step in Spanish.
    2. Strict extraction using JSON Schema, with a fallback to JSON Object.
    """

    def __init__(self):
        self.client = OpenAI(
            base_url=os.getenv("OPENAI_BASE_URL"),
            api_key=os.getenv("OPENAI_API_KEY", "sk-dummy"),
        )
        self.use_ts = False
        self.use_dialect = False
        self.use_null_p1 = False
        self.use_null_p2 = True
        self.use_dates = False
        self.reasoning_lang = "Spanish"
        
        # Tallies token usage for the current task; the server reads it to set
        # the X-GenSIE-Token-Usage response header. Reuse this in your own agent.
        self.usage = UsageTracker()

    def run(self, task: Task, model: str) -> Dict[str, Any]:
        self.usage.reset()
        # Pass 1: Analysis in the configured reasoning language
        base_pass1_prompt = (
            f"Instruction: {task.instruction}\n\n"
            f"Input Text: {task.input_text}\n\n"
            f"Analyze the text step-by-step to fulfill the instruction."
        )
        
        # Apply invariants to Pass 1 to guide the reasoning process
        pass1_prompt = self.apply_invariants(
            base_pass1_prompt,
            task.target_schema,
            use_ts=self.use_ts,
            use_null=self.use_null_p1,
            use_dialect=self.use_dialect,
            use_dates=self.use_dates
        )
        
        response1 = self.client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": f"You are a helpful assistant. Analyze the following text step-by-step in {self.reasoning_lang} to identify relevant information.",
                },
                {"role": "user", "content": pass1_prompt},
            ],
        )

        
        self.usage.add(getattr(response1, "usage", None))

        analysis = response1.choices[0].message.content

        # Pass 2: Extraction
        # Focus purely on extraction based on the reasoning from Pass 1
        base_pass2_prompt = (
            f"Instruction: {task.instruction}\n\n"
            f"Input Text: {task.input_text}\n\n"
            f"Analysis: {analysis}\n\n"
            f"Extract the requested information."
        )

        pass2_prompt = self.apply_invariants(
            base_pass2_prompt,
            task.target_schema,
            use_ts=self.use_ts,
            use_null=self.use_null_p2,
            use_dialect=self.use_dialect,
            use_dates=self.use_dates
        )
        
        messages2 = [
            {
                "role": "system",
                "content": "You are a precise data extraction agent. Extract the required information into valid JSON.",
            },
            {"role": "user", "content": pass2_prompt},
        ]
        
        # Attempt 1 for Pass 2: json_schema
        try:
            response2 = self.client.chat.completions.create(
                model=model,
                messages=messages2,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "extraction",
                        "schema": task.target_schema,
                        "strict": True,
                    },
                },
            )
            self.usage.add(getattr(response2, "usage", None))
            content = response2.choices[0].message.content
            result = parse_robust_json(content)
            if not result and content.strip():
                raise ValueError("JSON parsing yielded empty result from non-empty content.")
            result["_tokens"] = self.usage.snapshot()["total_tokens"]
            return result
        except Exception as e:
            # Fallback to text
            try:
                response3 = self.client.chat.completions.create(
                    model=model,
                    messages=messages2,
                    response_format={"type": "text"},
                )
                self.usage.add(getattr(response3, "usage", None))
                content = response3.choices[0].message.content
                result = parse_robust_json(content)
                result["_tokens"] = self.usage.snapshot()["total_tokens"]
                return result
            except Exception as fallback_err:
                logger.error(f"Fallback extraction failed: {str(fallback_err)}")
                return {"error": f"Failed fallback extraction: {str(fallback_err)}", "_tokens": self.usage.snapshot()["total_tokens"]}


class ARCANEAgent(GenSIEAgent, InvariantPromptMixin):
    """
    Implements the Double-Gate Architecture:
    Gate 1: Gated RAG (Threshold 0.55).
    Gate 2: Audited Synthesis (Structural + Semantic Gate >= 0.70).
    Fallback: Zero-Shot Generalization.
    """
    def __init__(self):
        self.client = OpenAI(
            base_url=os.getenv("OPENAI_BASE_URL"),
            api_key=os.getenv("OPENAI_API_KEY", "sk-dummy"),
        )
        self.rag = GatedRAGModule()
        self.architect = ArchitectModule(self.client)
        # Optimal Invariants
        self.use_ts = False
        self.use_dialect = False
        self.use_null_p1 = False
        self.use_null_p2 = True
        self.use_dates = False
        self.reasoning_lang = "Spanish"
        
        # Tallies token usage for the current task; the server reads it to set
        # the X-GenSIE-Token-Usage response header. Reuse this in your own agent.
        self.usage = UsageTracker()

    def _audit_synthesis(self, task: Task, synthetic: Dict[str, Any]) -> bool:
        """
        Validates the synthetic example both structurally and semantically.
        """
        # Structural Check
        try:
            validate(instance=synthetic['json'], schema=task.target_schema)
        except ValidationError:
            logger.warning("Audit failed: Structural validation error in synthetic example.")
            return False

        # Semantic Check
        try:
            input_emb = list(self.rag.model.embed([task.input_text]))[0]
            synth_emb = list(self.rag.model.embed([synthetic['text']]))[0]
            
            # Cosine similarity on normalized vectors
            norm_input = input_emb / (np.linalg.norm(input_emb) + 1e-9)
            norm_synth = synth_emb / (np.linalg.norm(synth_emb) + 1e-9)
            similarity = np.dot(norm_input, norm_synth)
            
            logger.info(f"Audit semantic similarity: {similarity:.4f}")
            return similarity >= 0.70
        except Exception as e:
            logger.error(f"Audit semantic check failed: {e}")
            return False

    def run(self, task: Task, model: str) -> Dict[str, Any]:
        """
        Executes the audited synthesis pipeline.
        """
        self.usage.reset()
        fs_str = ""
        is_zero_shot = False

        # 1. Gate 1: Gated RAG
        few_shots, success = self.rag.get_gated_examples(task, k=1, threshold=0.55)
        
        if success:
            fs_str = "\n".join([f"Example Input: {e['input_text']}\nExample Output: {json.dumps(e['output'])}" for e in few_shots])
        else:
            # 2. Gate 2: Audited Synthesis
            synthetic = self.architect.synthesize_example(task, model, usage=self.usage)
            if synthetic and self._audit_synthesis(task, synthetic):
                fs_str = f"Example Input: {synthetic['text']}\nExample Output: {json.dumps(synthetic['json'])}"
            else:
                # Pivot to Zero-Shot
                fs_str = ""
                is_zero_shot = True

        # 3. Two-Pass logic
        generalization_directive = "This is a zero-shot extraction. Generalize based on the schema and instructions." if is_zero_shot else ""
        
        analysis_prompt = (
            f"Instruction: {task.instruction}\n\n"
            f"Input Text: {task.input_text}\n\n"
            f"Reference Example:\n{fs_str}\n\n"
            f"{generalization_directive}\n"
            f"Analyze the text step-by-step in {self.reasoning_lang} to identify all relevant information before extraction."
        )

        pass1_prompt = self.apply_invariants(
            analysis_prompt,
            task.target_schema,
            use_ts=self.use_ts,
            use_null=self.use_null_p1,
            use_dialect=self.use_dialect,
            use_dates=self.use_dates
        )

        response1 = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": f"You are a strategic analyst. Provide a detailed step-by-step reasoning in {self.reasoning_lang}."},
                {"role": "user", "content": pass1_prompt}
            ]
        )
        
        self.usage.add(getattr(response1, "usage", None))
        analysis = response1.choices[0].message.content

        extraction_prompt = (
            f"Instruction: {task.instruction}\n\n"
            f"Input Text: {task.input_text}\n\n"
            f"Analysis: {analysis}\n\n"
            f"Extract the information strictly according to the schema."
        )
        
        pass2_prompt = self.apply_invariants(
            extraction_prompt,
            task.target_schema,
            use_ts=self.use_ts,
            use_null=self.use_null_p2,
            use_dialect=self.use_dialect,
            use_dates=self.use_dates
        )
        
        try:
            response2 = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a precise data extraction agent. If information is missing, return null."},
                    {"role": "user", "content": pass2_prompt}
                ],
                response_format={"type": "json_schema", "json_schema": {"name": "extraction", "schema": task.target_schema, "strict": True}}
            )
            
            self.usage.add(getattr(response2, "usage", None))
            
            result = parse_robust_json(response2.choices[0].message.content)
            result["_tokens"] = self.usage.snapshot()["total_tokens"]
            return result
        except Exception as e:
            logger.error(f"AuditedSynthetic Pass 2 failed: {e}")
            return {"error": f"Extraction failed: {str(e)}", "_tokens": self.usage.snapshot()["total_tokens"]}


class VIGILAgent(GenSIEAgent, InvariantPromptMixin):
    """
    Experimental pipeline with Gated RAG and Two-Pass reasoning.
    If similarity is low, it falls back to zero-shot with a generalization directive.
    """
    def __init__(self):
        """Initializes the agent with Gated RAG, Architect module and optimal invariants."""
        self.client = OpenAI(
            base_url=os.getenv("OPENAI_BASE_URL"),
            api_key=os.getenv("OPENAI_API_KEY", "sk-dummy"),
        )
        self.rag = GatedRAGModule()
        self.architect = ArchitectModule(self.client)
        # Optimal Generalizer Configuration
        self.use_ts = False
        self.use_null_p1 = False
        self.use_null_p2 = True
        self.use_dialect = False
        self.use_dates = False
        
        self.rag_k = 3
        self.reasoning_lang = "Spanish"
        self.hint_count = 3
        
        # Tallies token usage for the current task; the server reads it to set
        # the X-GenSIE-Token-Usage response header. Reuse this in your own agent.
        self.usage = UsageTracker()

    def run(self, task: Task, model: str) -> Dict[str, Any]:
        """
        Executes the two-pass extraction logic with a dynamic RAG gate.
        
        If RAG is gated (no relevant examples), it injects a generalization directive.
        Otherwise, it uses the retrieved few-shot examples for pass 1 analysis.
        """
        self.usage.reset()
        
        # 1. Gated Augmentation
        few_shots, is_relevant = self.rag.get_gated_examples(task, k=self.rag_k, threshold=0.55)

        directive = ""
        if not is_relevant:
            fs_str = ""
            directive = "No relevant examples found. Perform zero-shot extraction relying strictly on the schema definitions and reasoning hints."
        else:
            fs_str = "\n".join([f"Example Input: {e['input_text']}\nExample Output: {json.dumps(e['output'])}" for e in few_shots])
        hints = self.architect.get_reasoning_hints(task, model, lang=self.reasoning_lang, count=self.hint_count, usage=self.usage)
        
        # 2. Pass 1: Unconstrained Analysis
        analysis_prompt = (
            f"Instruction: {task.instruction}\n\n"
            f"Input Text: {task.input_text}\n\n"
            f"Strategic Reasoning Hints: {hints}\n\n"
            f"Few-Shot Reference Examples:\n{fs_str}\n\n"
            f"{directive}\n\n"
            f"Analyze the text step-by-step in {self.reasoning_lang} to identify all relevant information before extraction."
        )
        
        pass1_prompt = self.apply_invariants(
            analysis_prompt,
            task.target_schema,
            use_ts=self.use_ts,
            use_null=self.use_null_p1,
            use_dialect=self.use_dialect,
            use_dates=self.use_dates
        )
        
        response1 = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": f"You are a strategic analyst. Provide a detailed step-by-step reasoning in {self.reasoning_lang}."},
                {"role": "user", "content": pass1_prompt}
            ]
        )
        
        self.usage.add(getattr(response1, "usage", None))
        analysis = response1.choices[0].message.content

        # 3. Pass 2: Strict Extraction
        extraction_prompt = (
            f"Instruction: {task.instruction}\n\n"
            f"Input Text: {task.input_text}\n\n"
            f"Analysis: {analysis}\n\n"
            f"Extract the information strictly according to the schema."
        )
        
        pass2_prompt = self.apply_invariants(
            extraction_prompt,
            task.target_schema,
            use_ts=self.use_ts,
            use_null=self.use_null_p2,
            use_dialect=self.use_dialect,
            use_dates=self.use_dates
        )
        
        try:
            response2 = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a precise data extraction agent. If information is missing, return null."},
                    {"role": "user", "content": pass2_prompt}
                ],
                response_format={"type": "json_schema", "json_schema": {"name": "extraction", "schema": task.target_schema, "strict": True}}
            )
            
            self.usage.add(getattr(response2, "usage", None))
            
            result = parse_robust_json(response2.choices[0].message.content)
            result["_tokens"] = self.usage.snapshot()["total_tokens"]
            return result
        except Exception as e:
            logger.error(f"VIGILAgent Pass 2 failed: {e}")
            return {"error": f"Extraction failed: {str(e)}", "_tokens": self.usage.snapshot()["total_tokens"]}


class EAGLEAgent(GenSIEAgent, InvariantPromptMixin):
    """
    End-Anchored Generation & Logical Extraction (EAGLE).
    Appends the target schema at the very end of the prompt to maximize schema adherence.
    """

    def __init__(self):
        self.client = OpenAI(
            base_url=os.getenv("OPENAI_BASE_URL"),
            api_key=os.getenv("OPENAI_API_KEY", "sk-dummy"),
        )
        self.use_null = True
        self.use_ts = False
        self.use_dialect = False
        self.use_dates = True
        self.usage = UsageTracker()

    def run(self, task: Task, model: str) -> Dict[str, Any]:
        """
        Executes the extraction with the target schema anchored at the end of the prompt.
        """
        self.usage.reset()
        base_prompt = (
            f"Instruction: {task.instruction}\n\n"
            f"Input Text: {task.input_text}\n"
        )

        prompt = self.apply_invariants(
            base_prompt,
            task.target_schema,
            use_ts=self.use_ts,
            use_null=self.use_null,
            use_dialect=self.use_dialect,
            use_dates=self.use_dates
        )

        # End-Anchored strategy: Append the schema at the very end
        schema_json = json.dumps(task.target_schema, indent=2)
        prompt += f"\n\nOutput strictly following this JSON schema:\n```json\n{schema_json}\n```"

        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a precise data extraction agent. Extract the required information into valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "extraction",
                    "schema": task.target_schema,
                    "strict": True,
                },
            },
        )
        self.usage.add(getattr(response, "usage", None))

        try:
            content = response.choices[0].message.content
            result = parse_robust_json(content)
            result["_tokens"] = self.usage.snapshot()["total_tokens"]
            return result
        except Exception as e:
            logger.error(f"EAGLEAgent failed: {e}")
            return {"error": f"Extraction failed: {str(e)}", "_tokens": self.usage.snapshot()["total_tokens"]}


class OfficialParticipant(Participant):
    """
    Standard entry point for the competition.
    Participants can configure their available pipelines here.
    """

    def __init__(self):
        # Registering both base and hardened agents
        self.pipelines = {
            "baseline": BasicAgent(),
            "mira": MIRAAgent(),
            "vigil": VIGILAgent(),
            "arcane": ARCANEAgent(),
            "eagle": EAGLEAgent(),
        }

    def get_info(self) -> ParticipantInfo:
        return ParticipantInfo(
            team_name="MOLD Team",
            institution="University of Havana",
            pipelines=[
                PipelineInfo(
                    name="baseline",
                    description="Reference implementation using OpenAI Structured Outputs.",
                ),
                PipelineInfo(
                    name="mira",
                    description="Strategy that decouples reasoning in Spanish from strict JSON extraction with deterministic null pruning.",
                ),
                PipelineInfo(
                    name="vigil",
                    description="High-accuracy pipeline with Gated RAG, Two-Pass reasoning, and optimal generalizer configuration.",
                ),
                PipelineInfo(
                    name="arcane",
                    description="Double-gate pipeline with structural validation.",
                ),
                PipelineInfo(
                    name="eagle",
                    description="End-anchored extraction strategy for maximizing schema adherence.",
                ),
            ],
        )

    def get_agent(self, pipeline_name: str) -> GenSIEAgent:
        if pipeline_name not in self.pipelines:
            # Fallback to mira if pipeline not found
            return self.pipelines["mira"]
        return self.pipelines[pipeline_name]

