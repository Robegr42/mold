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

load_dotenv()
logger = getLogger("gensie")


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
