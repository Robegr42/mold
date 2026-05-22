import pytest
import os
from unittest.mock import MagicMock, patch
from gensie.baseline import MIRAAgent
from gensie.task import Task

@pytest.fixture
def sample_task():
    return Task(
        id="1", 
        instruction="Extract the user's name.", 
        input_text="Mi nombre es Juan.", 
        target_schema={"type": "object", "properties": {"name": {"type": "string"}}}
    )

def test_mira_init_params():
    # Test initialization with explicit parameters
    agent = MIRAAgent(use_null_p1=True, use_null_p2=False)
    assert agent.use_null_p1 is True
    assert agent.use_null_p2 is False

    agent = MIRAAgent(use_null_p1=False, use_null_p2=True)
    assert agent.use_null_p1 is False
    assert agent.use_null_p2 is True

@patch.dict(os.environ, {"GENSIE_MIRA_NULL_P1": "true", "GENSIE_MIRA_NULL_P2": "false"})
def test_mira_init_env_vars():
    # Test initialization with environment variables
    agent = MIRAAgent()
    assert agent.use_null_p1 is True
    assert agent.use_null_p2 is False

def test_mira_init_fallback():
    # Test fallback to use_null
    agent = MIRAAgent(use_null=True)
    assert agent.use_null_p1 is True
    assert agent.use_null_p2 is True

    agent = MIRAAgent(use_null=False)
    assert agent.use_null_p1 is False
    assert agent.use_null_p2 is False

def test_mira_run_uses_per_pass_null(sample_task):
    agent = MIRAAgent(use_null_p1=True, use_null_p2=True)
    
    mock_response_1 = MagicMock()
    mock_response_1.choices[0].message.content = "Analysis..."
    mock_response_1.usage = None
    
    mock_response_2 = MagicMock()
    mock_response_2.choices[0].message.content = '{"name": "Juan"}'
    mock_response_2.usage = None
    
    agent.client.chat.completions.create = MagicMock(side_effect=[mock_response_1, mock_response_2])
    
    agent.run(sample_task, model="test-model")
    
    # Check Pass 1 call
    call_args_1 = agent.client.chat.completions.create.call_args_list[0][1]
    user_prompt_1 = call_args_1["messages"][1]["content"]
    assert "Extract-or-Null Rule" in user_prompt_1
    
    # Check Pass 2 call
    call_args_2 = agent.client.chat.completions.create.call_args_list[1][1]
    user_prompt_2 = call_args_2["messages"][1]["content"]
    assert "Extract-or-Null Rule" in user_prompt_2
    assert "EXTRACTION INVARIANTS" in user_prompt_2
