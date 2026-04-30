import pytest
from unittest.mock import MagicMock, patch
from gensie.baseline import EndAnchoredAgent
from gensie.task import Task
from gensie.schemas.core import GenSIESchema
from pydantic import Field

class SimpleSchema(GenSIESchema):
    name: str = Field(..., description="A simple name")

@patch("gensie.baseline.OpenAI")
def test_end_anchored_agent_uses_json_schema(mock_openai):
    # Setup mock
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"name": "Gemini"}'
    mock_client.chat.completions.create.return_value = mock_response
    
    # Initialize agent
    agent = EndAnchoredAgent()
    
    # Create task
    task = Task.create(
        text="My name is Gemini.", 
        schema_class=SimpleSchema, 
        task_id="test_001"
    )
    
    # Run agent
    agent.run(task, model="gpt-4o")
    
    # Verify call to chat.completions.create
    args, kwargs = mock_client.chat.completions.create.call_args
    assert kwargs["response_format"]["type"] == "json_schema"
    assert kwargs["response_format"]["json_schema"]["schema"] == task.target_schema
    assert kwargs["response_format"]["json_schema"]["strict"] is True
