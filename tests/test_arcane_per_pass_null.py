import os
import pytest
from unittest.mock import MagicMock, patch
from gensie.baseline import ARCANEAgent
from gensie.task import Task

@pytest.fixture
def sample_task():
    return Task(
        id="1",
        instruction="Extract the user's name.",
        input_text="Mi nombre es Juan.",
        target_schema={"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}
    )

def test_arcane_agent_initialization(monkeypatch):
    monkeypatch.setenv("GENSIE_ARCANE_USE_TS", "true")
    monkeypatch.setenv("GENSIE_ARCANE_USE_DIALECT", "true")
    monkeypatch.setenv("GENSIE_ARCANE_NULL_P1", "true")
    monkeypatch.setenv("GENSIE_ARCANE_NULL_P2", "false")
    monkeypatch.setenv("GENSIE_ARCANE_REASONING_LANG", "English")
    
    agent = ARCANEAgent()
    assert agent.use_ts is True
    assert agent.use_dialect is True
    assert agent.use_null_p1 is True
    assert agent.use_null_p2 is False
    assert agent.reasoning_lang == "English"
    assert not hasattr(agent, "use_null")

@patch("gensie.baseline.GatedRAGModule")
@patch("gensie.baseline.ArchitectModule")
def test_arcane_agent_run_per_pass_null(mock_architect_class, mock_rag_class, sample_task, monkeypatch):
    monkeypatch.setenv("GENSIE_ARCANE_NULL_P1", "true")
    monkeypatch.setenv("GENSIE_ARCANE_NULL_P2", "true")
    monkeypatch.setenv("GENSIE_ARCANE_REASONING_LANG", "Spanish")

    agent = ARCANEAgent()
    agent.client = MagicMock()
    
    # Mock RAG success
    mock_rag = mock_rag_class.return_value
    mock_rag.get_gated_examples.return_value = ([], True)
    
    # Mock responses
    mock_response_1 = MagicMock()
    mock_response_1.choices = [MagicMock(message=MagicMock(content="Analysis"))]
    mock_response_1.usage = MagicMock(total_tokens=10)
    
    mock_response_2 = MagicMock()
    mock_response_2.choices = [MagicMock(message=MagicMock(content='{"name": "Juan"}'))]
    mock_response_2.usage = MagicMock(total_tokens=20)
    
    agent.client.chat.completions.create.side_effect = [mock_response_1, mock_response_2]
    
    with patch.object(agent, 'apply_invariants', wraps=agent.apply_invariants) as mock_apply_invariants:
        agent.run(sample_task, model="test-model")
        
        # Check Pass 1 call to apply_invariants
        assert mock_apply_invariants.call_args_list[0].kwargs["use_null"] == True
        # Check Pass 2 call to apply_invariants
        assert mock_apply_invariants.call_args_list[1].kwargs["use_null"] == True

@patch("gensie.baseline.GatedRAGModule")
@patch("gensie.baseline.ArchitectModule")
def test_arcane_agent_reasoning_lang(mock_architect_class, mock_rag_class, sample_task, monkeypatch):
    monkeypatch.setenv("GENSIE_ARCANE_REASONING_LANG", "French")

    agent = ARCANEAgent()
    agent.client = MagicMock()
    
    mock_rag = mock_rag_class.return_value
    mock_rag.get_gated_examples.return_value = ([], True)
    
    mock_response_1 = MagicMock()
    mock_response_1.choices = [MagicMock(message=MagicMock(content="Analysis"))]
    mock_response_2 = MagicMock()
    mock_response_2.choices = [MagicMock(message=MagicMock(content='{}'))]
    agent.client.chat.completions.create.side_effect = [mock_response_1, mock_response_2]
    
    agent.run(sample_task, model="test-model")
    
    # Check Pass 1 system message and prompt
    call_args_1 = agent.client.chat.completions.create.call_args_list[0][1]
    assert "French" in call_args_1["messages"][0]["content"]
    assert "French" in call_args_1["messages"][1]["content"]

def test_arcane_agent_defaults():
    # Clear environment variables if they exist
    with patch.dict(os.environ, {}, clear=True):
        agent = ARCANEAgent()
        assert agent.use_null_p1 is False
        assert agent.use_null_p2 is True
        assert agent.use_dialect is False
