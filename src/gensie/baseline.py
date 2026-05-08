import os
import json
import re
import copy
from typing import Any, Dict, List
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
    def apply_invariants(self, base_prompt: str, target_schema: dict) -> str:
        ts_schema = compress_schema_to_ts(target_schema)
        
        invariants = (
            f"\n\n--- EXTRACTION INVARIANTS ---\n"
            f"1. Target Schema (TypeScript Interface):\n```typescript\n{ts_schema}\n```\n"
            f"2. Strict Extract-or-Null Rule: Do not infer or guess. If information is absent, return `null`.\n"
            f"3. Dialect Rule: Respect Iberian/Latin American synonyms when extracting terms."
        )
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


class EndAnchoredAgent(GenSIEAgent):
    """
    Agent implementing the End-Anchored Template & Delimiter Separation strategy.
    """

    def __init__(self):
        self.client = OpenAI(
            base_url=os.getenv("OPENAI_BASE_URL"),
            api_key=os.getenv("OPENAI_API_KEY", "sk-dummy"),
        )

    def run(self, task: Task, model: str) -> Dict[str, Any]:
        """
        Executes the extraction using a specifically formatted prompt
        that places a blank JSON template at the end.
        """
        prompt = format_end_anchored_prompt(
            instruction=task.instruction,
            schema=task.target_schema,
            input_text=task.input_text,
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

    def __init__(self):
        self.client = OpenAI(
            base_url=os.getenv("OPENAI_BASE_URL"),
            api_key=os.getenv("OPENAI_API_KEY", "sk-dummy"),
        )

    def run(self, task: Task, model: str) -> Dict[str, Any]:
        total_tokens = 0
        # Pass 1: Analysis in Spanish
        pass1_prompt = (
            f"Instruction: {task.instruction}\n\n"
            f"Input Text: {task.input_text}\n\n"
            f"Analyze the text step-by-step to fulfill the instruction."
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
        base_pass2_prompt = (
            f"Instruction: {task.instruction}\n\n"
            f"Input Text: {task.input_text}\n\n"
            f"Analysis: {analysis}\n\n"
            f"Extract the requested information."
        )
        
        # Apply invariants
        final_prompt = self.apply_invariants(base_pass2_prompt, task.target_schema)
        
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

    def __init__(self):
        self.client = OpenAI(
            base_url=os.getenv("OPENAI_BASE_URL"),
            api_key=os.getenv("OPENAI_API_KEY", "sk-dummy"),
        )

    def run(self, task: Task, model: str) -> Dict[str, Any]:
        total_tokens = 0
        base_prompt = (
            f"You are a skeptical auditor. You must rely ONLY on the provided text.\n"
            f"A source quote MUST exist to authorize any extraction.\n\n"
            f"Instruction: {task.instruction}\n\n"
            f"Input Text: {task.input_text}\n\n"
            f"Extract the requested information."
        )
        
        final_prompt = self.apply_invariants(base_prompt, task.target_schema)
        
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

    def __init__(self):
        self.client = OpenAI(
            base_url=os.getenv("OPENAI_BASE_URL"),
            api_key=os.getenv("OPENAI_API_KEY", "sk-dummy"),
        )

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
        final_prompt = self.apply_invariants(audit_prompt, task.target_schema)

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


class OfficialParticipant(Participant):
    """
    Standard entry point for the competition.
    Participants can configure their available pipelines here.
    """

    def __init__(self):
        # Registering both base and hardened agents
        self.pipelines = {
            "two-pass": TwoPassAgent(),
            "grounded": GroundedAgent(),
            "auditor": AuditorAgent(),
            "basic": BasicAgent(),
            "end-anchored": EndAnchoredAgent(),
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
            ],
        )

    def get_agent(self, pipeline_name: str) -> GenSIEAgent:
        if pipeline_name not in self.pipelines:
            # Fallback to grounded if pipeline not found
            return self.pipelines["grounded"]
        return self.pipelines[pipeline_name]
