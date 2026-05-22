import pytest
from unittest.mock import MagicMock, patch
from gensie.baseline import EAGLEAgent
from gensie.task import Task

@pytest.fixture
def mock_openai():
    with patch("gensie.baseline.OpenAI") as mock:
        yield mock

def test_eagle_agent_instantiation(mock_openai):
    agent = EAGLEAgent()
    assert agent.use_null is True
    assert agent.use_ts is False
    assert agent.use_dialect is False
    assert agent.use_dates is True

def test_eagle_agent_run(mock_openai):
    agent = EAGLEAgent()
    task = Task(
        id="test_001",
        instruction="Extract information",
        input_text="The price is 100 dollars.",
        target_schema={
            "type": "object",
            "properties": {
                "price": {"type": "number"}
            },
            "required": ["price"]
        }
    )
    
    # Mock OpenAI response
    mock_completion = MagicMock()
    mock_completion.choices = [
        MagicMock(message=MagicMock(content='{"price": 100}'))
    ]
    mock_completion.usage.prompt_tokens = 30
    mock_completion.usage.completion_tokens = 20
    agent.client.chat.completions.create.return_value = mock_completion
    
    result = agent.run(task, model="gpt-4o-mini")
    
    assert result == {"price": 100, "_tokens": 50}
    
    # Verify the prompt structure (schema should be at the end)
    args, kwargs = agent.client.chat.completions.create.call_args
    messages = kwargs['messages']
    user_content = messages[1]['content']
    
    # InvariantPromptMixin adds invariants, and EAGLEAgent should add schema at the end.
    # The requirement says: "The agent must append the target schema (JSON format, as use_ts=False) at the very end of the prompt"
    expected_end = 'Output strictly following this JSON schema:\n```json\n{\n  "type": "object",\n  "properties": {\n    "price": {\n      "type": "number"\n    }\n  },\n  "required": [\n    "price"\n  ]\n}\n```'
    assert user_content.strip().endswith(expected_end)

def test_sage_agent_instantiation(mock_openai):
    from gensie.baseline import SAGEAgent
    agent = SAGEAgent()
    assert agent.use_null is True
    assert agent.use_ts is True
    assert agent.use_dialect is False
    assert agent.use_dates is True

def test_sage_agent_run(mock_openai):
    from gensie.baseline import SAGEAgent
    agent = SAGEAgent()
    task = Task(
        id="test_002",
        instruction="Extract information",
        input_text="The patient was seen on 2023-10-01.",
        target_schema={
            "type": "object",
            "properties": {
                "date": {"type": "string", "format": "date"}
            },
            "required": ["date"]
        }
    )
    
    # Mock OpenAI response
    mock_completion = MagicMock()
    mock_completion.choices = [
        MagicMock(message=MagicMock(content='{"date": "2023-10-01"}'))
    ]
    mock_completion.usage.prompt_tokens = 50
    mock_completion.usage.completion_tokens = 15
    agent.client.chat.completions.create.return_value = mock_completion
    
    result = agent.run(task, model="gpt-4o-mini")
    
    assert result == {"date": "2023-10-01", "_tokens": 65}
    
    # Verify the system prompt contains grounding instructions
    args, kwargs = agent.client.chat.completions.create.call_args
    messages = kwargs['messages']
    system_content = messages[0]['content']
    
    assert "explicitly quote or cite the source text" in system_content.lower()

def test_aura_agent_instantiation(mock_openai):
    from gensie.baseline import AURAAgent
    agent = AURAAgent()
    assert agent.use_null_p1 is False
    assert agent.use_null_p2 is False
    assert agent.use_dialect is True
    assert agent.use_ts is True
    assert agent.use_dates is True

def test_aura_agent_run(mock_openai):
    from gensie.baseline import AURAAgent
    agent = AURAAgent()
    task = Task(
        id="test_003",
        instruction="Extract products",
        input_text="We have a blue chair and a red table.",
        target_schema={
            "type": "object",
            "properties": {
                "products": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "color": {"type": "string"}
                        }
                    }
                }
            }
        }
    )
    
    # Pass 1: Draft
    mock_completion_1 = MagicMock()
    mock_completion_1.choices = [
        MagicMock(message=MagicMock(content='{"products": [{"name": "chair", "color": "blue"}, {"name": "table", "color": "red"}]}'))
    ]
    mock_completion_1.usage.prompt_tokens = 40
    mock_completion_1.usage.completion_tokens = 30
    mock_completion_1.usage.total_tokens = 70
    
    # Pass 2: Audit
    mock_completion_2 = MagicMock()
    mock_completion_2.choices = [
        MagicMock(message=MagicMock(content='{"products": [{"name": "chair", "color": "blue"}]}'))
    ]
    mock_completion_2.usage.prompt_tokens = 100
    mock_completion_2.usage.completion_tokens = 25
    mock_completion_2.usage.total_tokens = 125
    
    agent.client.chat.completions.create.side_effect = [mock_completion_1, mock_completion_2]
    
    result = agent.run(task, model="gpt-4o-mini")
    
    # Pass 1 tokens (70) + Pass 2 tokens (125) = 195
    assert result == {"products": [{"name": "chair", "color": "blue"}], "_tokens": 195}
    assert agent.client.chat.completions.create.call_count == 2
    
    # Check Pass 2 prompt for Auditor persona
    args, kwargs = agent.client.chat.completions.create.call_args
    messages = kwargs['messages']
    system_content = messages[0]['content']
    assert "Skeptical Auditor" in system_content
