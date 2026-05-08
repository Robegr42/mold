import pytest
from unittest.mock import MagicMock, patch
from gensie.baseline import GroundedAgent
from gensie.task import Task
import json

@pytest.fixture
def sample_task():
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "quote": {"type": "string"}
        },
        "required": ["name", "quote"]
    }
    return Task(
        id="test_task",
        instruction="Extract the person's name and a quote.",
        input_text="John said 'Hello world'.",
        target_schema=schema
    )

def test_grounded_agent_inherits_correctly():
    agent = GroundedAgent()
    from gensie.agent import GenSIEAgent
    from gensie.baseline import InvariantPromptMixin
    assert isinstance(agent, GenSIEAgent)
    assert isinstance(agent, InvariantPromptMixin)

@patch('gensie.baseline.OpenAI')
def test_grounded_agent_runs_single_pass_and_applies_invariants(mock_openai, sample_task):
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({"name": "John", "quote": "Hello world"})
    mock_client.chat.completions.create.return_value = mock_response

    agent = GroundedAgent()
    
    # Spy on apply_invariants
    with patch.object(agent, 'apply_invariants', wraps=agent.apply_invariants) as mock_apply_invariants:
        result = agent.run(sample_task, "test-model")
        
        # Verify result
        result.pop("_tokens", None)
        assert result == {"name": "John", "quote": "Hello world"}
        
        # Verify single pass (1 completion call)
        assert mock_client.chat.completions.create.call_count == 1
        
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        
        # Verify prompt format and "skeptical auditor" instructions
        messages = call_kwargs['messages']
        assert messages[0]['role'] == 'system'
        assert "skeptical auditor" in messages[0]['content'].lower() or "skeptical auditor" in messages[1]['content'].lower()
        assert "source quote" in messages[0]['content'].lower() or "source quote" in messages[1]['content'].lower()
        
        # Verify invariants applied
        assert mock_apply_invariants.call_count == 1
        
        # Verify json_schema response format
        assert call_kwargs['response_format']['type'] == 'json_schema'

@patch('gensie.baseline.OpenAI')
def test_grounded_agent_fallback_to_text(mock_openai, sample_task):
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    
    # Setup first call to fail, second to succeed
    mock_response_success = MagicMock()
    mock_response_success.choices = [MagicMock()]
    mock_response_success.choices[0].message.content = json.dumps({"name": "John", "quote": "Hello world"})
    
    mock_client.chat.completions.create.side_effect = [Exception("Schema parsing failed"), mock_response_success]

    agent = GroundedAgent()
    result = agent.run(sample_task, "test-model")
    
    result.pop("_tokens", None)
    assert result == {"name": "John", "quote": "Hello world"}
    assert mock_client.chat.completions.create.call_count == 2
    
    first_call_kwargs = mock_client.chat.completions.create.call_args_list[0][1]
    second_call_kwargs = mock_client.chat.completions.create.call_args_list[1][1]
    
    assert first_call_kwargs['response_format']['type'] == 'json_schema'
    assert second_call_kwargs['response_format']['type'] == 'text'
