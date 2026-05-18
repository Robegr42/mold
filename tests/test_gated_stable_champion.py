import pytest
import os
import json
from unittest.mock import MagicMock, patch
from gensie.baseline import GatedStableChampionAgent
from gensie.task import Task

@pytest.fixture
def sample_task():
    return Task(
        id="1", 
        instruction="Extract the user's name.", 
        input_text="Mi nombre es Juan.", 
        target_schema={"type": "object", "properties": {"name": {"type": "string"}}}
    )

@patch("gensie.baseline.GatedRAGModule")
@patch("gensie.baseline.ArchitectModule")
def test_gated_stable_champion_gated(mock_architect, mock_rag, sample_task):
    agent = GatedStableChampionAgent()
    
    mock_response_1 = MagicMock()
    mock_response_1.choices[0].message.content = "Analysis: Juan."
    mock_response_1.usage.total_tokens = 10
    
    mock_response_2 = MagicMock()
    mock_response_2.choices[0].message.content = '{"name": "Juan"}'
    mock_response_2.usage.total_tokens = 20
    
    agent.client.chat.completions.create = MagicMock(side_effect=[mock_response_1, mock_response_2])
    
    # Mock Gated RAG: Gated (False)
    agent.rag.get_gated_examples.return_value = ([], False)
    agent.architect.get_reasoning_hints.return_value = "Hint 1"
    
    result = agent.run(sample_task, model="test-model")
    
    assert result["name"] == "Juan"
    
    # Verify RAG call with correct threshold
    agent.rag.get_gated_examples.assert_called_with(sample_task, k=3, threshold=0.55)
    
    # Verify Generalization Directive in Pass 1 prompt
    call_args_1 = agent.client.chat.completions.create.call_args_list[0][1]
    analysis_prompt = call_args_1["messages"][1]["content"]
    assert "No relevant examples found. Perform zero-shot extraction relying strictly on the schema definitions and reasoning hints." in analysis_prompt
    assert "Few-Shot Reference Examples:" in analysis_prompt
    # Since fs_str is empty, we expect the label to be there but empty content after it if it follows the same template
    # Actually, the template in StableChampionAgent was:
    # f"Few-Shot Reference Examples:\n{fs_str}\n\n"
    # If fs_str is empty, it will just be "Few-Shot Reference Examples:\n\n\n" or similar.

@patch("gensie.baseline.GatedRAGModule")
@patch("gensie.baseline.ArchitectModule")
def test_gated_stable_champion_not_gated(mock_architect, mock_rag, sample_task):
    agent = GatedStableChampionAgent()
    
    mock_response_1 = MagicMock()
    mock_response_1.choices[0].message.content = "Analysis: Juan."
    mock_response_1.usage.total_tokens = 10
    
    mock_response_2 = MagicMock()
    mock_response_2.choices[0].message.content = '{"name": "Juan"}'
    mock_response_2.usage.total_tokens = 20
    
    agent.client.chat.completions.create = MagicMock(side_effect=[mock_response_1, mock_response_2])
    
    # Mock Gated RAG: Not Gated (True)
    example = {"input_text": "Soy Maria", "output": {"name": "Maria"}}
    agent.rag.get_gated_examples.return_value = ([example], True)
    agent.architect.get_reasoning_hints.return_value = "Hint 1"
    
    result = agent.run(sample_task, model="test-model")
    
    assert result["name"] == "Juan"
    
    # Verify NO Generalization Directive and presence of examples
    call_args_1 = agent.client.chat.completions.create.call_args_list[0][1]
    analysis_prompt = call_args_1["messages"][1]["content"]
    assert "No relevant examples found" not in analysis_prompt
    assert "Soy Maria" in analysis_prompt
