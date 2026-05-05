import pytest
from unittest.mock import MagicMock
from gensie.baseline import InvariantPromptMixin
from gensie.agent import GenSIEAgent
from gensie.task import Task
import json

try:
    from gensie.baseline import AuditorAgent
except ImportError:
    AuditorAgent = None

@pytest.fixture
def agent():
    if AuditorAgent is None:
        pytest.skip("AuditorAgent not implemented")
    return AuditorAgent()

@pytest.fixture
def sample_task():
    return Task(
        id="1", 
        instruction="Extract the user's name and age.", 
        input_text="My name is John.", 
        target_schema={
            "type": "object", 
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            }
        }
    )

def test_auditor_agent_inheritance():
    if AuditorAgent is None:
        pytest.fail("AuditorAgent is not implemented")
    agent = AuditorAgent()
    assert isinstance(agent, GenSIEAgent)
    assert isinstance(agent, InvariantPromptMixin)

def test_auditor_agent_success(agent, sample_task):
    mock_response_1 = MagicMock()
    # Draft includes a hallucinated age
    mock_response_1.choices[0].message.content = '{"name": "John", "age": 30}'
    
    mock_response_2 = MagicMock()
    # Audit replaces unverified claim with null
    mock_response_2.choices[0].message.content = '{"name": "John", "age": null}'
    
    agent.client.chat.completions.create = MagicMock(side_effect=[mock_response_1, mock_response_2])
    
    result = agent.run(sample_task, model="test-model")
    
    assert result == {"name": "John", "age": None}
    assert agent.client.chat.completions.create.call_count == 2
    
    # First pass: Draft
    call_args_1 = agent.client.chat.completions.create.call_args_list[0][1]
    assert call_args_1["response_format"]["type"] in ("json_object", "json_schema")
    
    # Second pass: Invariants applied, json_schema, adversarial inspector
    call_args_2 = agent.client.chat.completions.create.call_args_list[1][1]
    system_prompt_2 = call_args_2["messages"][0]["content"].lower()
    assert "adversarial inspector" in system_prompt_2 or "audit" in system_prompt_2
    
    user_prompt_2 = call_args_2["messages"][1]["content"]
    assert "EXTRACTION INVARIANTS" in user_prompt_2
    assert "Draft" in user_prompt_2
    assert call_args_2["response_format"]["type"] == "json_schema"

def test_auditor_agent_fallback_on_api_error(agent, sample_task):
    mock_response_1 = MagicMock()
    mock_response_1.choices[0].message.content = '{"name": "John", "age": 30}'
    
    mock_response_3 = MagicMock()
    mock_response_3.choices[0].message.content = '{"name": "John", "age": null}'
    
    # Simulate API error on 2nd pass (e.g. structured outputs not supported)
    agent.client.chat.completions.create = MagicMock(side_effect=[
        mock_response_1, 
        Exception("json_schema not supported"), 
        mock_response_3
    ])
    
    result = agent.run(sample_task, model="test-model")
    
    assert result == {"name": "John", "age": None}
    assert agent.client.chat.completions.create.call_count == 3
    
    call_args_3 = agent.client.chat.completions.create.call_args_list[2][1]
    assert call_args_3["response_format"]["type"] == "json_object"
