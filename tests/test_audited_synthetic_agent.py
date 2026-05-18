import pytest
import os
import json
import numpy as np
from unittest.mock import MagicMock, patch
from gensie.baseline import AuditedSyntheticAgent
from gensie.task import Task
from jsonschema import ValidationError

@pytest.fixture
def sample_task():
    return Task(
        id="1", 
        instruction="Extract the user's name.", 
        input_text="Mi nombre es Juan.", 
        target_schema={"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}
    )

@patch("gensie.baseline.GatedRAGModule")
@patch("gensie.baseline.ArchitectModule")
def test_audited_synthetic_agent_audit_pass(mock_architect_class, mock_rag_class, sample_task):
    mock_rag = mock_rag_class.return_value
    mock_architect = mock_architect_class.return_value
    
    agent = AuditedSyntheticAgent()
    agent.client = MagicMock()
    
    # RAG fails (threshold not met)
    mock_rag.get_gated_examples.return_value = ([], False)
    
    # Synthesis succeeds
    synthetic_example = {
        "text": "Mi nombre es Pedro.",
        "json": {"name": "Pedro"}
    }
    mock_architect.synthesize_example.return_value = synthetic_example
    
    # Mock embeddings for semantic check (similarity >= 0.70)
    # Cosine similarity of [1, 0] and [1, 0] is 1.0
    mock_rag.model.encode.side_effect = [np.array([1.0, 0.0]), np.array([1.0, 0.0])]
    
    # Mock Two-Pass logic
    mock_response_1 = MagicMock()
    mock_response_1.choices = [MagicMock(message=MagicMock(content="Analysis: Juan."))]
    mock_response_1.usage = MagicMock(total_tokens=10)
    
    mock_response_2 = MagicMock()
    mock_response_2.choices = [MagicMock(message=MagicMock(content='{"name": "Juan"}'))]
    mock_response_2.usage = MagicMock(total_tokens=20)
    
    agent.client.chat.completions.create.side_effect = [mock_response_1, mock_response_2]
    
    result = agent.run(sample_task, model="test-model")
    
    assert result["name"] == "Juan"
    
    # Check that architect was called
    mock_architect.synthesize_example.assert_called_once()
    
    # Check that rag.model.encode was called for both input and synthetic text
    assert mock_rag.model.encode.call_count == 2

    # Verify synthetic example was used in fs_str in Pass 1
    call_args_1 = agent.client.chat.completions.create.call_args_list[0][1]
    pass1_content = call_args_1["messages"][1]["content"]
    assert "Example Input: Mi nombre es Pedro." in pass1_content
    assert '"name": "Pedro"' in pass1_content
    assert "This is a zero-shot extraction" not in pass1_content

@patch("gensie.baseline.GatedRAGModule")
@patch("gensie.baseline.ArchitectModule")
def test_audited_synthetic_agent_audit_fail_structural(mock_architect_class, mock_rag_class, sample_task):
    mock_rag = mock_rag_class.return_value
    mock_architect = mock_architect_class.return_value
    
    agent = AuditedSyntheticAgent()
    agent.client = MagicMock()
    
    # RAG fails
    mock_rag.get_gated_examples.return_value = ([], False)
    
    # Synthesis returns invalid JSON
    synthetic_example = {
        "text": "Mi nombre es Pedro.",
        "json": {"wrong_field": "Pedro"} # Missing "name"
    }
    mock_architect.synthesize_example.return_value = synthetic_example
    
    # Mock Two-Pass logic
    mock_response_1 = MagicMock()
    mock_response_1.choices = [MagicMock(message=MagicMock(content="Analysis: Juan."))]
    mock_response_1.usage = MagicMock(total_tokens=10)
    
    mock_response_2 = MagicMock()
    mock_response_2.choices = [MagicMock(message=MagicMock(content='{"name": "Juan"}'))]
    mock_response_2.usage = MagicMock(total_tokens=20)
    
    agent.client.chat.completions.create.side_effect = [mock_response_1, mock_response_2]
    
    result = agent.run(sample_task, model="test-model")
    
    assert result["name"] == "Juan"
    
    # Verify it pivoted to Zero-Shot
    call_args_1 = agent.client.chat.completions.create.call_args_list[0][1]
    pass1_content = call_args_1["messages"][1]["content"]
    assert "This is a zero-shot extraction" in pass1_content
    assert "Example Input: Mi nombre es Pedro." not in pass1_content

@patch("gensie.baseline.GatedRAGModule")
@patch("gensie.baseline.ArchitectModule")
def test_audited_synthetic_agent_audit_fail_semantic(mock_architect_class, mock_rag_class, sample_task):
    mock_rag = mock_rag_class.return_value
    mock_architect = mock_architect_class.return_value
    
    agent = AuditedSyntheticAgent()
    agent.client = MagicMock()
    
    # RAG fails
    mock_rag.get_gated_examples.return_value = ([], False)
    
    # Synthesis returns unrelated text
    synthetic_example = {
        "text": "El clima está soleado.",
        "json": {"name": "Clima"}
    }
    mock_architect.synthesize_example.return_value = synthetic_example
    
    # Mock embeddings for semantic check (similarity < 0.70)
    # Orthogonal vectors have similarity 0
    mock_rag.model.encode.side_effect = [np.array([1.0, 0.0]), np.array([0.0, 1.0])]
    
    # Mock Two-Pass logic
    mock_response_1 = MagicMock()
    mock_response_1.choices = [MagicMock(message=MagicMock(content="Analysis: Juan."))]
    mock_response_2 = MagicMock()
    mock_response_2.choices = [MagicMock(message=MagicMock(content='{"name": "Juan"}'))]
    agent.client.chat.completions.create.side_effect = [mock_response_1, mock_response_2]
    
    result = agent.run(sample_task, model="test-model")
    
    assert result["name"] == "Juan"

    # Verify it pivoted to Zero-Shot
    call_args_1 = agent.client.chat.completions.create.call_args_list[0][1]
    pass1_content = call_args_1["messages"][1]["content"]
    assert "This is a zero-shot extraction" in pass1_content
    assert "El clima está soleado." not in pass1_content
