import pytest
import json
import hashlib
from unittest.mock import MagicMock, patch
from gensie.baseline import ArchitectModule
from gensie.task import Task

class MockMessage:
    def __init__(self, content):
        self.content = content

class MockChoice:
    def __init__(self, content):
        self.message = MockMessage(content)

class MockResponse:
    def __init__(self, content):
        self.choices = [MockChoice(content)]

def test_synthesize_example_caching():
    client = MagicMock()
    architect = ArchitectModule(client)
    
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"}
        },
        "required": ["name", "age"]
    }
    task = Task(
        id="test_001",
        instruction="Extract person info",
        input_text="Juan tiene 25 años",
        target_schema=schema
    )
    
    # Mocking first call - Successful synthesis in a code block
    valid_response = {
        "text": "Juan tiene 25 años y vive en Madrid.",
        "json": {"name": "Juan", "age": 25}
    }
    client.chat.completions.create.return_value = MockResponse(f"Aquí tienes:\n```json\n{json.dumps(valid_response)}\n```")
    
    # First call
    result1 = architect.synthesize_example(task, "gpt-4o")
    assert result1 == valid_response
    assert client.chat.completions.create.call_count == 1
    
    # Verify the call used text format
    args, kwargs = client.chat.completions.create.call_args
    assert kwargs["response_format"]["type"] == "text"
    
    # Second call should be cached
    result2 = architect.synthesize_example(task, "gpt-4o")
    assert result2 == valid_response
    assert client.chat.completions.create.call_count == 1

def test_synthesize_example_self_correction():
    client = MagicMock()
    architect = ArchitectModule(client)
    
    schema = {
        "type": "object",
        "properties": {"city": {"type": "string"}}
    }
    task = Task(id="test_002", instruction="Extract city", input_text="", target_schema=schema)
    
    # First call fails (missing 'json' key)
    invalid_response = {"text": "Barcelona es una gran ciudad."}
    # Second call succeeds (no code block, just raw JSON)
    valid_response = {
        "text": "Barcelona es una gran ciudad.",
        "json": {"city": "Barcelona"}
    }
    
    client.chat.completions.create.side_effect = [
        MockResponse(json.dumps(invalid_response)),
        MockResponse(json.dumps(valid_response))
    ]
    
    result = architect.synthesize_example(task, "gpt-4o")
    assert result == valid_response
    # 2 calls: 1 initial + 1 retry
    assert client.chat.completions.create.call_count == 2

def test_synthesize_example_robust_parsing():
    client = MagicMock()
    architect = ArchitectModule(client)
    
    schema = {"type": "object", "properties": {"foo": {"type": "string"}}}
    task = Task(id="test_004", instruction="foo", input_text="", target_schema=schema)
    
    # Simulate response with conversational noise and code block
    noisy_response = """
    Claro, aquí tienes el ejemplo solicitado:
    
    ```json
    {
        "text": "Este es un párrafo de ejemplo.",
        "json": {"foo": "bar"}
    }
    ```
    
    Espero que te sirva.
    """
    client.chat.completions.create.return_value = MockResponse(noisy_response)
    
    result = architect.synthesize_example(task, "gpt-4o")
    assert result["json"]["foo"] == "bar"
    assert result["text"] == "Este es un párrafo de ejemplo."

def test_synthesize_example_brace_fallback():
    client = MagicMock()
    architect = ArchitectModule(client)
    
    schema = {"type": "object", "properties": {"foo": {"type": "string"}}}
    task = Task(id="test_005", instruction="foo", input_text="", target_schema=schema)
    
    # Simulate response with ONLY braces, no code block
    brace_response = 'El resultado es {"text": "Párrafo", "json": {"foo": "baz"}} de nada.'
    client.chat.completions.create.return_value = MockResponse(brace_response)
    
    result = architect.synthesize_example(task, "gpt-4o")
    assert result["json"]["foo"] == "baz"
