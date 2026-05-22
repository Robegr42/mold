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
