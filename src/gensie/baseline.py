import os
import json
import re
import copy
import time
import hashlib
import threading
import numpy as np
import faiss
from typing import Any, Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from gensie.agent import GenSIEAgent, Participant, ParticipantInfo, PipelineInfo
from gensie.task import Task
from gensie.utils.prompts import (
    format_end_anchored_prompt,
)
from dotenv import load_dotenv
from logging import getLogger
from gensie.utils.schema import compress_schema_to_ts

load_dotenv()
logger = getLogger("gensie")


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
        use_dialect: bool = True
    ) -> str:
        ts_schema = compress_schema_to_ts(target_schema) if use_ts else json.dumps(target_schema, indent=2)
        
        sections = []
        if use_ts:
            sections.append(f"1. Target Schema (TypeScript Interface):\n```typescript\n{ts_schema}\n```")
        else:
            sections.append(f"1. Target Schema (JSON Schema):\n```json\n{ts_schema}\n```")
            
        if use_null:
            sections.append(f"2. Strict Extract-or-Null Rule: Do not infer or guess. If information is absent, return `null`.")
            
        if use_dialect:
            sections.append(f"3. Dialect Rule: Respect Iberian/Latin American synonyms when extracting terms.")
            
        invariants = "\n\n--- EXTRACTION INVARIANTS ---\n" + "\n".join(sections)
        return base_prompt + invariants


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

    def run(self, task: Task, model: str) -> Dict[str, Any]:
        """
        Executes the extraction using OpenAI's response_format for strict schema compliance.
        """
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


class EndAnchoredAgent(GenSIEAgent, InvariantPromptMixin):
    """
    Agent implementing the End-Anchored Template & Delimiter Separation strategy.
    """

    def __init__(self, use_ts=True, use_null=True, use_dialect=True):
        self.client = OpenAI(
            base_url=os.getenv("OPENAI_BASE_URL"),
            api_key=os.getenv("OPENAI_API_KEY", "sk-dummy"),
        )
        self.use_ts = use_ts
        self.use_null = use_null
        self.use_dialect = use_dialect

    def run(self, task: Task, model: str) -> Dict[str, Any]:
        """
        Executes the extraction using a specifically formatted prompt
        that places a blank JSON template at the end.
        """
        base_prompt = format_end_anchored_prompt(
            instruction=task.instruction,
            schema=task.target_schema,
            input_text=task.input_text,
        )
        
        prompt = self.apply_invariants(
            base_prompt, 
            task.target_schema,
            use_ts=self.use_ts,
            use_null=self.use_null,
            use_dialect=self.use_dialect
        )

        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a precise data extraction agent. "
                    "Your output must be a valid JSON object following the provided template.",
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

        try:
            content = response.choices[0].message.content
            result = json.loads(content)
            if hasattr(response, "usage") and response.usage:
                result["_tokens"] = response.usage.total_tokens
            return result
        except (json.JSONDecodeError, AttributeError, IndexError) as e:
            return {
                "error": f"Failed to parse model response: {str(e)}",
                "raw": content if "content" in locals() else None,
            }
        except Exception as e:
            logger.error(str(e))
            return {"error": str(e)}



class TwoPassAgent(GenSIEAgent, InvariantPromptMixin):
    """
    Agent that uses a two-pass strategy:
    1. Unconstrained analysis step in Spanish.
    2. Strict extraction using JSON Schema, with a fallback to JSON Object.
    """

    def __init__(self, use_ts=True, use_null=True, use_dialect=True):
        self.client = OpenAI(
            base_url=os.getenv("OPENAI_BASE_URL"),
            api_key=os.getenv("OPENAI_API_KEY", "sk-dummy"),
        )
        self.use_ts = use_ts
        self.use_null = use_null
        self.use_dialect = use_dialect

    def run(self, task: Task, model: str) -> Dict[str, Any]:
        total_tokens = 0
        # Pass 1: Analysis in Spanish
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
            use_null=self.use_null,
            use_dialect=self.use_dialect
        )
        
        response1 = self.client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Analyze the following text step-by-step in Spanish to identify relevant information.",
                },
                {"role": "user", "content": pass1_prompt},
            ],
        )

        
        if hasattr(response1, "usage") and response1.usage:
            total_tokens += response1.usage.total_tokens

        analysis = response1.choices[0].message.content

        # Pass 2: Extraction
        # Focus purely on extraction based on the reasoning from Pass 1
        final_prompt = (
            f"Instruction: {task.instruction}\n\n"
            f"Input Text: {task.input_text}\n\n"
            f"Analysis: {analysis}\n\n"
            f"Extract the requested information."
        )
        
        messages2 = [
            {
                "role": "system",
                "content": "You are a precise data extraction agent. Extract the required information into valid JSON.",
            },
            {"role": "user", "content": final_prompt},
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
            if hasattr(response2, "usage") and response2.usage:
                total_tokens += response2.usage.total_tokens
            content = response2.choices[0].message.content
            result = json.loads(content)
            result["_tokens"] = total_tokens
            return result
        except Exception as e:
            # Fallback to text
            try:
                response3 = self.client.chat.completions.create(
                    model=model,
                    messages=messages2,
                    response_format={"type": "text"},
                )
                if hasattr(response3, "usage") and response3.usage:
                    total_tokens += response3.usage.total_tokens
                content = response3.choices[0].message.content
                result = json.loads(content)
                result["_tokens"] = total_tokens
                return result
            except Exception as fallback_err:
                logger.error(f"Fallback extraction failed: {str(fallback_err)}")
                return {"error": f"Failed fallback extraction: {str(fallback_err)}", "_tokens": total_tokens}


class GroundedAgent(GenSIEAgent, InvariantPromptMixin):
    """
    Agent that acts as a skeptical auditor, mandating source quotes to authorize extraction.
    """

    def __init__(self, use_ts=True, use_null=True, use_dialect=True):
        self.client = OpenAI(
            base_url=os.getenv("OPENAI_BASE_URL"),
            api_key=os.getenv("OPENAI_API_KEY", "sk-dummy"),
        )
        self.use_ts = use_ts
        self.use_null = use_null
        self.use_dialect = use_dialect

    def run(self, task: Task, model: str) -> Dict[str, Any]:
        total_tokens = 0
        base_prompt = (
            f"You are a skeptical auditor. You must rely ONLY on the provided text.\n"
            f"A source quote MUST exist to authorize any extraction.\n\n"
            f"Instruction: {task.instruction}\n\n"
            f"Input Text: {task.input_text}\n\n"
            f"Extract the requested information."
        )
        
        final_prompt = self.apply_invariants(
            base_prompt, 
            task.target_schema,
            use_ts=self.use_ts,
            use_null=self.use_null,
            use_dialect=self.use_dialect
        )
        
        messages = [
            {
                "role": "system",
                "content": "You are a precise data extraction agent and a skeptical auditor. Mandate source quotes for every field.",
            },
            {"role": "user", "content": final_prompt},
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "extraction",
                        "schema": task.target_schema,
                        "strict": True,
                    },
                },
            )
            if hasattr(response, "usage") and response.usage:
                total_tokens += response.usage.total_tokens
            content = response.choices[0].message.content
            result = json.loads(content)
            result["_tokens"] = total_tokens
            return result
        except Exception as e:
            try:
                response_fb = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    response_format={"type": "text"},
                )
                if hasattr(response_fb, "usage") and response_fb.usage:
                    total_tokens += response_fb.usage.total_tokens
                content = response_fb.choices[0].message.content
                result = json.loads(content)
                result["_tokens"] = total_tokens
                return result
            except Exception as fallback_err:
                logger.error(f"Fallback extraction failed: {str(fallback_err)}")
                return {"error": f"Failed fallback extraction: {str(fallback_err)}", "_tokens": total_tokens}


class AuditorAgent(GenSIEAgent, InvariantPromptMixin):
    """
    Agent that uses a self-correction loop to strike hallucinations.
    1. Pass 1 (Draft): Generate a preliminary JSON draft.
    2. Pass 2 (Audit): Pass the Draft and the Source text to the model to audit it.
    """

    def __init__(self, use_ts=True, use_null=True, use_dialect=True):
        self.client = OpenAI(
            base_url=os.getenv("OPENAI_BASE_URL"),
            api_key=os.getenv("OPENAI_API_KEY", "sk-dummy"),
        )
        self.use_ts = use_ts
        self.use_null = use_null
        self.use_dialect = use_dialect

    def run(self, task: Task, model: str) -> Dict[str, Any]:
        """
        Executes a two-pass extraction: first a draft, then an adversarial audit.
        """
        total_tokens = 0
        # Pass 1: Draft
        pass1_prompt = (
            f"Instruction: {task.instruction}\n\n"
            f"Input Text: {task.input_text}\n\n"
            f"Generate a preliminary JSON draft of the extraction."
        )

        try:
            response1 = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a precise data extraction agent. Generate a preliminary JSON draft.",
                    },
                    {"role": "user", "content": pass1_prompt},
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "extraction_draft",
                        "schema": task.target_schema,
                        "strict": True,
                    },
                },
            )
            if hasattr(response1, "usage") and response1.usage:
                total_tokens += response1.usage.total_tokens
            draft_content = response1.choices[0].message.content
            draft = json.loads(draft_content)
        except Exception:
            # Fallback to text
            response1 = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a precise data extraction agent. Generate a preliminary JSON draft. Respond ONLY with valid JSON.",
                    },
                    {"role": "user", "content": pass1_prompt},
                ],
                response_format={"type": "text"},
            )
            if hasattr(response1, "usage") and response1.usage:
                total_tokens += response1.usage.total_tokens
            draft_content = response1.choices[0].message.content
            draft = json.loads(draft_content)

        # Pass 2: Audit
        audit_prompt = (
            f"Input Text: {task.input_text}\n\n"
            f"Draft: {draft}\n\n"
            f"Audit the draft by comparing it against the source text. "
            f"Replace any unverified claim with null."
        )

        # Apply invariants strictly to the Pass 2 audit step
        final_prompt = self.apply_invariants(
            audit_prompt, 
            task.target_schema,
            use_ts=self.use_ts,
            use_null=self.use_null,
            use_dialect=self.use_dialect
        )

        messages2 = [
            {
                "role": "system",
                "content": "You are an adversarial inspector holding a red pen. "
                "Audit the following draft against the source text. "
                "Strike any information that is not explicitly supported by the text by replacing it with null.",
            },
            {"role": "user", "content": final_prompt},
        ]

        # Attempt 1 for Pass 2: json_schema
        try:
            response2 = self.client.chat.completions.create(
                model=model,
                messages=messages2,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "audit_extraction",
                        "schema": task.target_schema,
                        "strict": True,
                    },
                },
            )
            if hasattr(response2, "usage") and response2.usage:
                total_tokens += response2.usage.total_tokens
            content = response2.choices[0].message.content
            result = json.loads(content)
            result["_tokens"] = total_tokens
            return result
        except Exception as e:
            # Fallback to text
            try:
                response3 = self.client.chat.completions.create(
                    model=model,
                    messages=messages2,
                    response_format={"type": "text"},
                )
                if hasattr(response3, "usage") and response3.usage:
                    total_tokens += response3.usage.total_tokens
                content = response3.choices[0].message.content
                result = json.loads(content)
                result["_tokens"] = total_tokens
                return result
            except Exception as fallback_err:
                logger.error(f"Fallback audit failed: {str(fallback_err)}")
                return {"error": f"Failed fallback audit: {str(fallback_err)}", "_tokens": total_tokens}


class EndAnchoredAgentNI(GenSIEAgent):
    """End-Anchored Agent without invariants."""
    def __init__(self):
        self.client = OpenAI(
            base_url=os.getenv("OPENAI_BASE_URL"),
            api_key=os.getenv("OPENAI_API_KEY", "sk-dummy"),
        )

    def run(self, task: Task, model: str) -> Dict[str, Any]:
        prompt = format_end_anchored_prompt(
            instruction=task.instruction,
            schema=task.target_schema,
            input_text=task.input_text,
        )
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a precise data extraction agent. Your output must be a valid JSON object following the provided template."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_schema", "json_schema": {"name": "extraction", "schema": task.target_schema, "strict": True}},
        )
        result = json.loads(response.choices[0].message.content)
        if hasattr(response, "usage") and response.usage:
            result["_tokens"] = response.usage.total_tokens
        return result

class GroundedAgentNI(GenSIEAgent):
    """Grounded Agent without invariants."""
    def __init__(self):
        self.client = OpenAI(
            base_url=os.getenv("OPENAI_BASE_URL"),
            api_key=os.getenv("OPENAI_API_KEY", "sk-dummy"),
        )

    def run(self, task: Task, model: str) -> Dict[str, Any]:
        prompt = (
            f"You are a skeptical auditor. You must rely ONLY on the provided text.\n"
            f"A source quote MUST exist to authorize any extraction.\n\n"
            f"Instruction: {task.instruction}\n\n"
            f"Input Text: {task.input_text}\n\n"
            f"Extract the requested information."
        )
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a precise data extraction agent and a skeptical auditor. Mandate source quotes for every field."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_schema", "json_schema": {"name": "extraction", "schema": task.target_schema, "strict": True}},
        )
        result = json.loads(response.choices[0].message.content)
        if hasattr(response, "usage") and response.usage:
            result["_tokens"] = response.usage.total_tokens
        return result

class AuditorAgentNI(GenSIEAgent):
    """Auditor Agent without invariants."""
    def __init__(self):
        self.client = OpenAI(
            base_url=os.getenv("OPENAI_BASE_URL"),
            api_key=os.getenv("OPENAI_API_KEY", "sk-dummy"),
        )

    def run(self, task: Task, model: str) -> Dict[str, Any]:
        total_tokens = 0
        # Pass 1: Draft
        pass1_prompt = f"Instruction: {task.instruction}\n\nInput Text: {task.input_text}\n\nGenerate a preliminary JSON draft."
        response1 = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a precise data extraction agent."},
                {"role": "user", "content": pass1_prompt},
            ],
            response_format={"type": "json_schema", "json_schema": {"name": "extraction_draft", "schema": task.target_schema, "strict": True}},
        )
        if hasattr(response1, "usage") and response1.usage:
            total_tokens += response1.usage.total_tokens
        draft = json.loads(response1.choices[0].message.content)

        # Pass 2: Audit
        audit_prompt = f"Input Text: {task.input_text}\n\nDraft: {draft}\n\nAudit the draft and strike unverified claims."
        response2 = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an adversarial inspector holding a red pen."},
                {"role": "user", "content": audit_prompt},
            ],
            response_format={"type": "json_schema", "json_schema": {"name": "audit_extraction", "schema": task.target_schema, "strict": True}},
        )
        if hasattr(response2, "usage") and response2.usage:
            total_tokens += response2.usage.total_tokens
        result = json.loads(response2.choices[0].message.content)
        result["_tokens"] = total_tokens
        return result



class RAGModule:
    """Provides dynamic few-shot examples using semantic search (FAISS + MiniLM)."""
    def __init__(self, data_path: str = "data/dev"):
        model_path = os.path.abspath("models/all-MiniLM-L6-v2")
        if not os.path.exists(model_path):
            raise RuntimeError(f"Required embedding model not found at {model_path}. "
                             "Please run the model localization script first.")
        self.model = SentenceTransformer(model_path)
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
            embeddings = self.model.encode(texts)
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(np.array(embeddings).astype('float32'))

    def get_few_shot_examples(self, task: Task, k: int = 3) -> List[Dict[str, Any]]:
        if self.index is None or not self.examples:
            return []
        
        query = f"Instruction: {task.instruction}\nText: {task.input_text}"
        query_embedding = self.model.encode([query])
        D, I = self.index.search(np.array(query_embedding).astype('float32'), k)
        
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
        threshold: float = 0.65
    ) -> tuple[List[Dict[str, Any]], bool]:
        """
        Retrieves top k examples only if the best match exceeds the threshold.
        Similarity is calculated from L2 distance D as: similarity = 1 - (D/2)
        """
        if self.index is None or not self.examples:
            return [], False
        
        query = f"Instruction: {task.instruction}\nText: {task.input_text}"
        query_embedding = self.model.encode([query])
        D, I = self.index.search(np.array(query_embedding).astype('float32'), k)
        
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

    def get_reasoning_hints(self, task: Task, model: str, lang: str = "Spanish", count: int = 3) -> str:
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
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"ArchitectModule error: {e}")
            return "Analice el texto cuidadosamente y asegúrese de que cada campo esté respaldado por evidencia directa."

    def synthesize_example(self, task: Task, model: str) -> Optional[Dict[str, Any]]:
        """
        Synthesizes a realistic training example (text + json) for a given task schema.
        Uses an in-memory cache keyed by the MD5 hash of the schema.
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
            f"Respond with a JSON object containing two keys: 'text' (string) and 'json' (object)."
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
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            result = json.loads(content)

            # Validation
            if "text" not in result or "json" not in result:
                raise KeyError("Missing 'text' or 'json' keys in synthesis result.")

            self._synthesis_cache[schema_hash] = result
            return result

        except Exception as e:
            logger.warning(f"Synthesis failed, attempting self-correction: {e}")
            # Self-Correction Pass
            correction_messages = messages + [
                {"role": "assistant", "content": content if content else "Error in generation"},
                {"role": "user", "content": f"The previous output was invalid or missing keys. Error: {str(e)}. Please try again, ensuring you return a JSON object with 'text' and 'json' keys."}
            ]
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=correction_messages,
                    response_format={"type": "json_object"}
                )
                result = json.loads(response.choices[0].message.content)
                if "text" in result and "json" in result:
                    self._synthesis_cache[schema_hash] = result
                    return result
            except Exception as final_e:
                logger.error(f"Synthesis self-correction failed: {final_e}")
        
        return None

class ChampionTwoPassEngine:
    """Core engine running the Two-Pass-NI logic with API-native json_schema."""
    def __init__(self, client: OpenAI):
        self.client = client

    def run_pass1(self, task: Task, model: str, hints: str, few_shot: str) -> str:
        messages = [
            {
                "role": "system", 
                "content": f"You are a strategic analyst. Use these hints: {hints}\n\n{few_shot}"
            },
            {
                "role": "user", 
                "content": f"Instruction: {task.instruction}\n\nInput Text: {task.input_text}\n\nAnalyze step-by-step in Spanish."
            }
        ]
        
        # Pass 1 uses a reasoning schema
        reasoning_schema = {
            "type": "object",
            "properties": {
                "thought_process": {"type": "string"},
                "evidence_segments": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["thought_process", "evidence_segments"]
        }
        
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            response_format={"type": "json_schema", "json_schema": {"name": "reasoning", "schema": reasoning_schema, "strict": True}}
        )
        return response.choices[0].message.content, response.usage.total_tokens

    def run_pass2(self, task: Task, model: str, analysis: str, few_shot: str) -> Dict[str, Any]:
        prompt = (
            f"Instruction: {task.instruction}\n\n"
            f"Input Text: {task.input_text}\n\n"
            f"Analysis: {analysis}\n\n"
            f"Few-Shot Examples:\n{few_shot}\n\n"
            f"Extract the information strictly according to the schema."
        )
        
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a precise data extraction agent. If information is missing, return null."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_schema", "json_schema": {"name": "extraction", "schema": task.target_schema, "strict": True}}
        )
        return json.loads(response.choices[0].message.content), response.usage.total_tokens

class ReActAuditor:
    """Pluggable verification loop to verify grounding and nullify hallucinations."""
    def __init__(self, client: OpenAI):
        self.client = client

    def audit(self, task: Task, model: str, extraction: Dict[str, Any], start_time: float) -> Dict[str, Any]:
        audited = copy.deepcopy(extraction)
        keys_to_check = [k for k, v in extraction.items() if v is not None and k != "_tokens"]
        
        # Limit to top 5 fields to stay within time budget
        for key in keys_to_check[:5]:
            if time.time() - start_time > 50: # Hard limit for safety
                break
                
            value = audited[key]
            prompt = (
                f"Text: {task.input_text}\n\n"
                f"Extracted Field: {key}\n"
                f"Extracted Value: {value}\n\n"
                f"Does the text explicitly support this extraction? If yes, provide the quote. If no or inferred, answer 'NULLIFY'."
            )
            
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a critical auditor. Be strict. Better null than false."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=100
                )
                if "NULLIFY" in response.choices[0].message.content.upper():
                    audited[key] = None
            except:
                continue
                
        return audited

class ConsensusAggregator:
    """Medoid selection for ensembling."""
    def __init__(self):
        model_path = os.path.abspath("models/all-MiniLM-L6-v2")
        if not os.path.exists(model_path):
            raise RuntimeError(f"Required embedding model not found at {model_path}. "
                             "Please run the model localization script first.")
        self.model = SentenceTransformer(model_path)

    def aggregate(self, candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not candidates:
            return {}
        if len(candidates) == 1:
            return candidates[0]
            
        json_strs = [json.dumps(c, sort_keys=True) for c in candidates]
        embeddings = self.model.encode(json_strs)
        
        # Calculate similarity matrix
        sim_matrix = np.dot(embeddings, embeddings.T)
        # Sum similarities for each candidate
        sim_sums = sim_matrix.sum(axis=1)
        # Select medoid
        medoid_idx = np.argmax(sim_sums)
        
        return candidates[medoid_idx]

class ChampionAgent(GenSIEAgent):
    """The Two-Pass Champion Agent."""
    def __init__(self):
        self.client = OpenAI(
            base_url=os.getenv("OPENAI_BASE_URL"),
            api_key=os.getenv("OPENAI_API_KEY", "sk-dummy"),
        )
        self.rag = RAGModule()
        self.architect = ArchitectModule(self.client)
        self.engine = ChampionTwoPassEngine(self.client)
        self.auditor = ReActAuditor(self.client)
        self.aggregator = ConsensusAggregator()

    def run(self, task: Task, model: str) -> Dict[str, Any]:
        start_time = time.time()
        total_tokens = 0
        
        # 1. Augmentation
        few_shots = self.rag.get_few_shot_examples(task)
        fs_str = "\n".join([f"Example: {json.dumps(e)}" for e in few_shots])
        hints = self.architect.get_reasoning_hints(task, model)
        
        # 2. Parallel Ensemble (N=2)
        def run_single_pipeline():
            tokens = 0
            analysis, t1 = self.engine.run_pass1(task, model, hints, fs_str)
            extraction, t2 = self.engine.run_pass2(task, model, analysis, fs_str)
            return extraction, t1 + t2

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(run_single_pipeline) for _ in range(2)]
            results = []
            for f in futures:
                try:
                    res, tokens = f.result(timeout=45) # Leave room for auditor
                    results.append(res)
                    total_tokens += tokens
                except:
                    continue
        
        if not results:
            return {"error": "Pipeline timeout or failure", "_tokens": total_tokens}
            
        # 3. Consensus
        winner = self.aggregator.aggregate(results)
        
        # 4. Audit
        final_result = self.auditor.audit(task, model, winner, start_time)
        final_result["_tokens"] = total_tokens
        
        return final_result

class SlimChampionAgent(GenSIEAgent, InvariantPromptMixin):
    """
    Streamlined high-accuracy pipeline with RAG and Two-Pass reasoning.
    Optimized for small models by removing ensembling and auditing friction.
    """
    def __init__(self, use_ts=True, use_null=True, use_dialect=True):
        self.client = OpenAI(
            base_url=os.getenv("OPENAI_BASE_URL"),
            api_key=os.getenv("OPENAI_API_KEY", "sk-dummy"),
        )
        self.rag = RAGModule()
        self.architect = ArchitectModule(self.client)
        self.use_ts = use_ts
        self.use_null = use_null
        self.use_dialect = use_dialect
        
        # Environment-driven configuration for tuning
        self.rag_k = int(os.getenv("GENSIE_RAG_K", "3"))
        self.reasoning_lang = os.getenv("GENSIE_REASONING_LANG", "Spanish")
        self.hint_count = int(os.getenv("GENSIE_HINT_COUNT", "3"))

    def run(self, task: Task, model: str) -> Dict[str, Any]:
        total_tokens = 0
        
        # 1. Augmentation
        few_shots = self.rag.get_few_shot_examples(task, k=self.rag_k)
        fs_str = "\n".join([f"Example Input: {e['input_text']}\nExample Output: {json.dumps(e['output'])}" for e in few_shots])
        hints = self.architect.get_reasoning_hints(task, model, lang=self.reasoning_lang, count=self.hint_count)
        
        # 2. Pass 1: Unconstrained Analysis
        analysis_prompt = (
            f"Instruction: {task.instruction}\n\n"
            f"Input Text: {task.input_text}\n\n"
            f"Strategic Reasoning Hints: {hints}\n\n"
            f"Few-Shot Reference Examples:\n{fs_str}\n\n"
            f"Analyze the text step-by-step in {self.reasoning_lang} to identify all relevant information before extraction."
        )
        
        pass1_prompt = self.apply_invariants(
            analysis_prompt,
            task.target_schema,
            use_ts=self.use_ts,
            use_null=self.use_null,
            use_dialect=self.use_dialect
        )
        
        response1 = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": f"You are a strategic analyst. Provide a detailed step-by-step reasoning in {self.reasoning_lang}."},
                {"role": "user", "content": pass1_prompt}
            ]
        )
        
        if hasattr(response1, "usage") and response1.usage:
            total_tokens += response1.usage.total_tokens
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
            use_null=self.use_null,
            use_dialect=self.use_dialect
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
            
            if hasattr(response2, "usage") and response2.usage:
                total_tokens += response2.usage.total_tokens
            
            result = json.loads(response2.choices[0].message.content)
            result["_tokens"] = total_tokens
            return result
        except Exception as e:
            logger.error(f"SlimChampion Pass 2 failed: {e}")
            # Final fallback
            return {"error": f"Extraction failed: {str(e)}", "_tokens": total_tokens}

class StableChampionAgent(GenSIEAgent, InvariantPromptMixin):
    """
    Robust high-accuracy pipeline with RAG and Two-Pass reasoning.
    Optimized as a 'Safe Generalizer' using the optimal Two-Pass invariant (Null Rule only).
    """
    def __init__(self):
        self.client = OpenAI(
            base_url=os.getenv("OPENAI_BASE_URL"),
            api_key=os.getenv("OPENAI_API_KEY", "sk-dummy"),
        )
        self.rag = RAGModule()
        self.architect = ArchitectModule(self.client)
        # Optimal Generalizer Configuration (from research)
        self.use_ts = False
        self.use_null = True
        self.use_dialect = False
        
        # Environment-driven configuration for tuning
        self.rag_k = int(os.getenv("GENSIE_RAG_K", "3"))
        self.reasoning_lang = os.getenv("GENSIE_REASONING_LANG", "Spanish")
        self.hint_count = int(os.getenv("GENSIE_HINT_COUNT", "3"))

    def run(self, task: Task, model: str) -> Dict[str, Any]:
        total_tokens = 0
        
        # 1. Augmentation
        few_shots = self.rag.get_few_shot_examples(task, k=self.rag_k)
        fs_str = "\n".join([f"Example Input: {e['input_text']}\nExample Output: {json.dumps(e['output'])}" for e in few_shots])
        hints = self.architect.get_reasoning_hints(task, model, lang=self.reasoning_lang, count=self.hint_count)
        
        # 2. Pass 1: Unconstrained Analysis
        analysis_prompt = (
            f"Instruction: {task.instruction}\n\n"
            f"Input Text: {task.input_text}\n\n"
            f"Strategic Reasoning Hints: {hints}\n\n"
            f"Few-Shot Reference Examples:\n{fs_str}\n\n"
            f"Analyze the text step-by-step in {self.reasoning_lang} to identify all relevant information before extraction."
        )
        
        pass1_prompt = self.apply_invariants(
            analysis_prompt,
            task.target_schema,
            use_ts=self.use_ts,
            use_null=self.use_null,
            use_dialect=self.use_dialect
        )
        
        response1 = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": f"You are a strategic analyst. Provide a detailed step-by-step reasoning in {self.reasoning_lang}."},
                {"role": "user", "content": pass1_prompt}
            ]
        )
        
        if hasattr(response1, "usage") and response1.usage:
            total_tokens += response1.usage.total_tokens
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
            use_null=self.use_null,
            use_dialect=self.use_dialect
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
            
            if hasattr(response2, "usage") and response2.usage:
                total_tokens += response2.usage.total_tokens
            
            result = json.loads(response2.choices[0].message.content)
            result["_tokens"] = total_tokens
            return result
        except Exception as e:
            logger.error(f"StableChampion Pass 2 failed: {e}")
            return {"error": f"Extraction failed: {str(e)}", "_tokens": total_tokens}

class GatedStableChampionAgent(GenSIEAgent, InvariantPromptMixin):
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
        self.use_null = True
        self.use_dialect = False
        
        self.rag_k = int(os.getenv("GENSIE_RAG_K", "3"))
        self.reasoning_lang = os.getenv("GENSIE_REASONING_LANG", "Spanish")
        self.hint_count = int(os.getenv("GENSIE_HINT_COUNT", "3"))

    def run(self, task: Task, model: str) -> Dict[str, Any]:
        """
        Executes the two-pass extraction logic with a dynamic RAG gate.
        
        If RAG is gated (no relevant examples), it injects a generalization directive.
        Otherwise, it uses the retrieved few-shot examples for pass 1 analysis.
        """
        total_tokens = 0
        
        # 1. Gated Augmentation
        few_shots, is_relevant = self.rag.get_gated_examples(task, k=self.rag_k, threshold=0.65)

        directive = ""
        if not is_relevant:
            fs_str = ""
            directive = "No relevant examples found. Perform zero-shot extraction relying strictly on the schema definitions and reasoning hints."
        else:
            fs_str = "\n".join([f"Example Input: {e['input_text']}\nExample Output: {json.dumps(e['output'])}" for e in few_shots])
        hints = self.architect.get_reasoning_hints(task, model, lang=self.reasoning_lang, count=self.hint_count)
        
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
            use_null=self.use_null,
            use_dialect=self.use_dialect
        )
        
        response1 = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": f"You are a strategic analyst. Provide a detailed step-by-step reasoning in {self.reasoning_lang}."},
                {"role": "user", "content": pass1_prompt}
            ]
        )
        
        if hasattr(response1, "usage") and response1.usage:
            total_tokens += response1.usage.total_tokens
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
            use_null=self.use_null,
            use_dialect=self.use_dialect
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
            
            if hasattr(response2, "usage") and response2.usage:
                total_tokens += response2.usage.total_tokens
            
            result = json.loads(response2.choices[0].message.content)
            result["_tokens"] = total_tokens
            return result
        except Exception as e:
            logger.error(f"GatedStableChampion Pass 2 failed: {e}")
            return {"error": f"Extraction failed: {str(e)}", "_tokens": total_tokens}

class SyntheticAnchorAgent(GenSIEAgent, InvariantPromptMixin):
    """
    Agent that uses a synthetic anchor when RAG fails to find relevant examples.
    """
    def __init__(self):
        """Initializes the agent with Gated RAG, Architect module and optimal invariants."""
        self.client = OpenAI(
            base_url=os.getenv("OPENAI_BASE_URL"),
            api_key=os.getenv("OPENAI_API_KEY", "sk-dummy"),
        )
        self.rag = GatedRAGModule()
        self.architect = ArchitectModule(self.client)
        # Invariants: use_ts=False, use_null=True, use_dialect=False
        self.use_ts = False
        self.use_null = True
        self.use_dialect = False
        
        self.rag_k = int(os.getenv("GENSIE_RAG_K", "3"))
        self.reasoning_lang = os.getenv("GENSIE_REASONING_LANG", "Spanish")
        self.hint_count = int(os.getenv("GENSIE_HINT_COUNT", "3"))

    def run(self, task: Task, model: str) -> Dict[str, Any]:
        """
        Executes the two-pass extraction logic with a dynamic RAG gate and synthetic fallback.
        """
        total_tokens = 0
        
        # 1. Gated Augmentation (threshold=0.55)
        few_shots, is_relevant = self.rag.get_gated_examples(task, k=self.rag_k, threshold=0.55)

        directive = ""
        fs_str = ""
        if not is_relevant:
            synthetic = self.architect.synthesize_example(task, model)
            if synthetic:
                fs_str = f"Example Input: {synthetic['text']}\nExample Output: {json.dumps(synthetic['json'])}"
                directive = "No historical examples found. Use this synthetic example to understand the target schema structure."
            else:
                directive = "No relevant examples found. Perform zero-shot extraction relying strictly on the schema definitions and reasoning hints."
        else:
            fs_str = "\n".join([f"Example Input: {e['input_text']}\nExample Output: {json.dumps(e['output'])}" for e in few_shots])
            
        hints = self.architect.get_reasoning_hints(task, model, lang=self.reasoning_lang, count=self.hint_count)
        
        # 2. Pass 1: Analysis
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
            use_null=self.use_null,
            use_dialect=self.use_dialect
        )
        
        response1 = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": f"You are a strategic analyst. Provide a detailed step-by-step reasoning in {self.reasoning_lang}."},
                {"role": "user", "content": pass1_prompt}
            ]
        )
        
        if hasattr(response1, "usage") and response1.usage:
            total_tokens += response1.usage.total_tokens
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
            use_null=self.use_null,
            use_dialect=self.use_dialect
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
            
            if hasattr(response2, "usage") and response2.usage:
                total_tokens += response2.usage.total_tokens
            
            result = json.loads(response2.choices[0].message.content)
            result["_tokens"] = total_tokens
            return result
        except Exception as e:
            logger.error(f"SyntheticAnchor Pass 2 failed: {e}")
            return {"error": f"Extraction failed: {str(e)}", "_tokens": total_tokens}

class OfficialParticipant(Participant):
    """
    Standard entry point for the competition.
    Participants can configure their available pipelines here.
    """

    def __init__(self):
        # Registering both base and hardened agents
        self.pipelines = {
            # Two-Pass Ablation
            "two-pass": TwoPassAgent(),
            "two-pass-ni": TwoPassAgent(use_ts=False, use_null=False, use_dialect=False),
            "two-pass-ts": TwoPassAgent(use_null=False, use_dialect=False),
            "two-pass-null": TwoPassAgent(use_ts=False, use_dialect=False),
            "two-pass-dialect": TwoPassAgent(use_ts=False, use_null=False),
            
            # Grounded Ablation
            "grounded": GroundedAgent(),
            "grounded-ni": GroundedAgentNI(),
            "grounded-ts": GroundedAgent(use_null=False, use_dialect=False),
            "grounded-null": GroundedAgent(use_ts=False, use_dialect=False),
            "grounded-dialect": GroundedAgent(use_ts=False, use_null=False),
            
            # Auditor Ablation
            "auditor": AuditorAgent(),
            "auditor-ni": AuditorAgentNI(),
            "auditor-ts": AuditorAgent(use_null=False, use_dialect=False),
            "auditor-null": AuditorAgent(use_ts=False, use_dialect=False),
            "auditor-dialect": AuditorAgent(use_ts=False, use_null=False),
            
            "basic": BasicAgent(),
            
            # End-Anchored Ablation
            "end-anchored": EndAnchoredAgent(),
            "end-anchored-ni": EndAnchoredAgentNI(),
            "end-anchored-ts": EndAnchoredAgent(use_null=False, use_dialect=False),
            "end-anchored-null": EndAnchoredAgent(use_ts=False, use_dialect=False),
            "end-anchored-dialect": EndAnchoredAgent(use_ts=False, use_null=False),

            "champion": ChampionAgent(),
            "slim-champion": SlimChampionAgent(),
            "stable-champion": StableChampionAgent(),
            "gated-stable-champion": GatedStableChampionAgent(),
            "synthetic-anchor": SyntheticAnchorAgent(),
        }

    def get_info(self) -> ParticipantInfo:
        return ParticipantInfo(
            team_name="MOLD Team",
            institution="University of Havana",
            pipelines=[
                PipelineInfo(
                    name="two-pass",
                    description="Strategy that decouples reasoning in Spanish from strict JSON extraction.",
                ),
                PipelineInfo(
                    name="grounded",
                    description="Evidence-based agent that mandates source quotes to authorize extraction.",
                ),
                PipelineInfo(
                    name="auditor",
                    description="Self-correction loop with an adversarial audit to strike hallucinations.",
                ),
                PipelineInfo(
                    name="baseline",
                    description="Reference implementation using OpenAI Structured Outputs.",
                ),
                PipelineInfo(
                    name="end-anchored",
                    description="Strategy that places a blank JSON template at the end of the prompt.",
                ),
                PipelineInfo(
                    name="champion",
                    description="High-accuracy modular pipeline with RAG, Two-Pass reasoning, and ReAct verification.",
                ),
                PipelineInfo(
                    name="slim-champion",
                    description="Streamlined high-accuracy pipeline with RAG and Two-Pass reasoning, optimized for SLMs.",
                ),
                PipelineInfo(
                    name="stable-champion",
                    description="Streamlined architecture using the optimal Two-Pass invariant configuration (Null-Rule only).",
                ),
                PipelineInfo(
                    name="synthetic-anchor",
                    description="Experimental pipeline that uses synthetic examples from ArchitectModule as few-shot anchors when RAG fails.",
                ),
            ],
        )

    def get_agent(self, pipeline_name: str) -> GenSIEAgent:
        if pipeline_name not in self.pipelines:
            # Fallback to grounded if pipeline not found
            return self.pipelines["grounded"]
        return self.pipelines[pipeline_name]
