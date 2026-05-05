import os
import json
import re
from typing import Any, Dict
from openai import OpenAI
from gensie.agent import GenSIEAgent, Participant, ParticipantInfo, PipelineInfo
from gensie.task import Task
from gensie.utils.prompts import (
    format_end_anchored_prompt,
    format_thinking_prompt,
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
            return json.loads(content)
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
            return json.loads(content)
        except (json.JSONDecodeError, AttributeError, IndexError) as e:
            return {
                "error": f"Failed to parse model response: {str(e)}",
                "raw": content if "content" in locals() else None,
            }
        except Exception as e:
            logger.error(str(e))
            return {"error": str(e)}


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
                "raw_content": content,
            }


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
            content = response2.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            # Fallback to json_object
            try:
                response3 = self.client.chat.completions.create(
                    model=model,
                    messages=messages2,
                    response_format={"type": "json_object"},
                )
                content = response3.choices[0].message.content
                return json.loads(content)
            except Exception as fallback_err:
                logger.error(f"Fallback extraction failed: {str(fallback_err)}")
                return {"error": f"Failed fallback extraction: {str(fallback_err)}"}


class OfficialParticipant(Participant):
    """
    Standard entry point for the competition.
    Participants can configure up to 3 pipelines here.
    """

    def __init__(self):
        # Default pipeline using the reference BasicAgent
        self.pipelines = {
            "baseline": BasicAgent(),
            "end-anchored": EndAnchoredAgent(),
            "reasoning-guided": ThinkingAgent(),
        }

    def get_info(self) -> ParticipantInfo:
        return ParticipantInfo(
            team_name="MOLD Team",
            institution="University of Havana",
            pipelines=[
                PipelineInfo(
                    name="baseline",
                    description="Standard OpenAI agent using structured outputs.",
                ),
                PipelineInfo(
                    name="end-anchored",
                    description="Agent using end-anchored templates and visual delimiters to improve long-context extraction.",
                ),
                PipelineInfo(
                    name="reasoning-guided",
                    description="Strategy using <think> and <answer> tags to perform Chain-of-Thought before extraction.",
                ),
            ],
        )

    def get_agent(self, pipeline_name: str) -> GenSIEAgent:
        if pipeline_name not in self.pipelines:
            # Fallback to default if pipeline not found, or raise error
            return self.pipelines["baseline"]
        return self.pipelines[pipeline_name]
