import pytest
import os
import json
from unittest.mock import MagicMock, patch
from gensie.baseline import SlimChampionAgent, StableChampionAgent
from gensie.task import Task

@pytest.fixture
def sample_task():
    return Task(
        id="1", 
        instruction="Extract the user's name.", 
        input_text="Mi nombre es Juan.", 
        target_schema={"type": "object", "properties": {"name": {"type": "string"}}}
    )

@patch("gensie.baseline.RAGModule")
@patch("gensie.baseline.ArchitectModule")
def test_stable_champion_env_config(mock_architect, mock_rag, sample_task):
    with patch.dict(os.environ, {"GENSIE_RAG_K": "1", "GENSIE_REASONING_LANG": "English", "GENSIE_HINT_COUNT": "5"}):
        agent = StableChampionAgent()

        assert agent.rag_k == 1
        assert agent.reasoning_lang == "English"
        assert agent.hint_count == 5

        mock_response_1 = MagicMock()
        mock_response_1.choices = [MagicMock(message=MagicMock(content="Analysis: Juan."))]
        mock_response_1.usage = MagicMock(total_tokens=10)

        mock_response_2 = MagicMock()
        mock_response_2.choices = [MagicMock(message=MagicMock(content='{"name": "Juan"}'))]
        mock_response_2.usage = MagicMock(total_tokens=20)

        agent.client.chat.completions.create = MagicMock(side_effect=[mock_response_1, mock_response_2])

        # Mock RAG and Architect responses
        agent.rag.get_few_shot_examples.return_value = []
        agent.architect.get_reasoning_hints.return_value = "Hint 1, Hint 2"

        result = agent.run(sample_task, model="test-model")

        assert result["name"] == "Juan"
        assert result["_tokens"] == 30

        # Verify RAG k
        agent.rag.get_few_shot_examples.assert_called_with(sample_task, k=1)

        # Verify Architect hints
        agent.architect.get_reasoning_hints.assert_called_with(sample_task, "test-model", lang="English", count=5)

        # Verify Pass 1 system prompt
        call_args_1 = agent.client.chat.completions.create.call_args_list[0][1]
        assert "English" in call_args_1["messages"][0]["content"]

@patch("gensie.baseline.RAGModule")
@patch("gensie.baseline.ArchitectModule")
def test_slim_champion_env_config(mock_architect, mock_rag, sample_task):
    with patch.dict(os.environ, {"GENSIE_RAG_K": "2", "GENSIE_REASONING_LANG": "Spanish", "GENSIE_HINT_COUNT": "2"}):
        agent = SlimChampionAgent()

        assert agent.rag_k == 2
        assert agent.reasoning_lang == "Spanish"
        assert agent.hint_count == 2

        mock_response_1 = MagicMock()
        mock_response_1.choices = [MagicMock(message=MagicMock(content="Análisis: Juan."))]
        mock_response_1.usage = MagicMock(total_tokens=15)

        mock_response_2 = MagicMock()
        mock_response_2.choices = [MagicMock(message=MagicMock(content='{"name": "Juan"}'))]
        mock_response_2.usage = MagicMock(total_tokens=25)

        agent.client.chat.completions.create = MagicMock(side_effect=[mock_response_1, mock_response_2])

        # Mock RAG and Architect responses
        agent.rag.get_few_shot_examples.return_value = []
        agent.architect.get_reasoning_hints.return_value = "Pista 1"

        result = agent.run(sample_task, model="test-model")

        assert result["name"] == "Juan"
        assert result["_tokens"] == 40

        # Verify RAG k
        agent.rag.get_few_shot_examples.assert_called_with(sample_task, k=2)

        # Verify Architect hints
        agent.architect.get_reasoning_hints.assert_called_with(sample_task, "test-model", lang="Spanish", count=2)

        # Verify Pass 1 system prompt
        call_args_1 = agent.client.chat.completions.create.call_args_list[0][1]
        assert "Spanish" in call_args_1["messages"][0]["content"]
