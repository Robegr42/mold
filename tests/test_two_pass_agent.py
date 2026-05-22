import pytest
from unittest.mock import MagicMock
from gensie.baseline import InvariantPromptMixin
from gensie.agent import GenSIEAgent
from gensie.task import Task
import json
import openai

try:
    from gensie.baseline import MIRAAgent
except ImportError:
    MIRAAgent = None

@pytest.fixture
def agent():
    if MIRAAgent is None:
        pytest.skip("MIRAAgent not implemented")
    return MIRAAgent()

@pytest.fixture
def sample_task():
    return Task(
        id="1", 
        instruction="Extract the user's name.", 
        input_text="Mi nombre es Juan.", 
        target_schema={"type": "object", "properties": {"name": {"type": "string"}}}
    )

def test_mira_agent_inheritance():
    if MIRAAgent is None:
        pytest.fail("MIRAAgent is not implemented")
    agent = MIRAAgent()
    assert isinstance(agent, GenSIEAgent)
    assert isinstance(agent, InvariantPromptMixin)

def test_mira_agent_success(agent, sample_task):
    mock_response_1 = MagicMock()
    mock_response_1.choices[0].message.content = "Analysis: The text is in Spanish and says the name is Juan."
    
    mock_response_2 = MagicMock()
    mock_response_2.choices[0].message.content = '{"name": "Juan"}'
    
    agent.client.chat.completions.create = MagicMock(side_effect=[mock_response_1, mock_response_2])
    
    result = agent.run(sample_task, model="test-model")
    
    result.pop("_tokens", None)
    assert result == {"name": "Juan"}
    assert agent.client.chat.completions.create.call_count == 2
    
    # First pass: Unconstrained, step-by-step Spanish, with TypeScript schema and dialect awareness
    call_args_1 = agent.client.chat.completions.create.call_args_list[0][1]
    system_prompt_1 = call_args_1["messages"][0]["content"].lower()
    assert "spanish" in system_prompt_1 or "español" in system_prompt_1
    
    user_prompt_1 = call_args_1["messages"][1]["content"]
    assert "TypeScript" in user_prompt_1
    assert "Dialect Rule" in user_prompt_1
    assert "response_format" not in call_args_1
    
    # Second pass: Pure extraction, now includes EXTRACTION INVARIANTS block
    call_args_2 = agent.client.chat.completions.create.call_args_list[1][1]
    assert call_args_2["response_format"]["type"] == "json_schema"
    user_prompt_2 = call_args_2["messages"][1]["content"]
    assert "EXTRACTION INVARIANTS" in user_prompt_2
    assert "Analysis: The text is in Spanish" in user_prompt_2

def test_mira_agent_fallback_on_api_error(agent, sample_task):
    mock_response_1 = MagicMock()
    mock_response_1.choices[0].message.content = "Analysis..."
    
    mock_response_3 = MagicMock()
    mock_response_3.choices[0].message.content = '{"name": "Juan"}'
    
    # Simulate API error on 2nd pass (e.g. structured outputs not supported)
    agent.client.chat.completions.create = MagicMock(side_effect=[
        mock_response_1, 
        Exception("json_schema not supported"), 
        mock_response_3
    ])
    
    result = agent.run(sample_task, model="test-model")
    
    result.pop("_tokens", None)
    assert result == {"name": "Juan"}
    assert agent.client.chat.completions.create.call_count == 3
    
    call_args_3 = agent.client.chat.completions.create.call_args_list[2][1]
    assert call_args_3["response_format"]["type"] == "text"

def test_mira_agent_fallback_on_json_error(agent, sample_task):
    mock_response_1 = MagicMock()
    mock_response_1.choices[0].message.content = "Analysis..."
    
    mock_response_2 = MagicMock()
    mock_response_2.choices[0].message.content = 'invalid json'

    mock_response_3 = MagicMock()
    mock_response_3.choices[0].message.content = '{"name": "Juan"}'
    
    # Simulate JSON decoding error on 2nd pass
    agent.client.chat.completions.create = MagicMock(side_effect=[
        mock_response_1, 
        mock_response_2, 
        mock_response_3
    ])
    
    result = agent.run(sample_task, model="test-model")
    
    result.pop("_tokens", None)
    assert result == {"name": "Juan"}
    assert agent.client.chat.completions.create.call_count == 3
    
    call_args_3 = agent.client.chat.completions.create.call_args_list[2][1]
    assert call_args_3["response_format"]["type"] == "text"
