import pytest
import json
from unittest.mock import MagicMock, patch
from gensie.baseline import LexiconGroundedAgent
from gensie.task import Task

def test_lexicon_grounded_agent_instantiation():
    """
    Verifies that LexiconGroundedAgent can be instantiated.
    """
    agent = LexiconGroundedAgent()
    assert agent is not None
    assert isinstance(agent, LexiconGroundedAgent)

def test_lexicon_grounded_agent_run_placeholder():
    """
    Verifies that LexiconGroundedAgent has a run method.
    """
    agent = LexiconGroundedAgent()
    assert hasattr(agent, "run")

def test_lexicon_grounded_agent_augment_schema():
    """
    Verifies that _augment_schema correctly adds dialectal hints to the schema.
    """
    agent = LexiconGroundedAgent()
    schema = {
        "type": "object",
        "properties": {
            "employment_status": {
                "type": "string",
                "enum": ["employed", "unemployed"],
                "description": "The current employment status of the person."
            },
            "is_homeowner": {
                "type": "boolean",
                "description": "Whether the person owns their home."
            },
            "age": {
                "type": "integer",
                "description": "Age of the person."
            }
        }
    }
    
    augmented_schema = agent._augment_schema(schema)
    
    # Check enum hints
    emp_desc = augmented_schema["properties"]["employment_status"]["description"]
    assert "(Dialectal Hints: ['employed', 'unemployed'])" in emp_desc
    
    # Check boolean hints
    home_desc = augmented_schema["properties"]["is_homeowner"]["description"]
    assert "(Hints: 'sí/propietario' -> true, 'no/inquilino' -> false)" in home_desc
    
    # Check property without special hints remains mostly same (or doesn't get boolean/enum hints)
    age_desc = augmented_schema["properties"]["age"]["description"]
    assert "Dialectal Hints" not in age_desc
    assert "Hints: 'sí/propietario'" not in age_desc

def test_lexicon_grounded_agent_transform_to_quote_first_schema():
    """
    Verifies that _transform_to_quote_first_schema correctly transforms leaf properties.
    """
    agent = LexiconGroundedAgent()
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "metadata": {
                "type": "object",
                "properties": {
                    "is_active": {"type": "boolean"}
                },
                "required": ["is_active"]
            }
        },
        "required": ["name", "age", "metadata"]
    }

    transformed = agent._transform_to_quote_first_schema(schema)

    # Check name transformation
    assert transformed["properties"]["name"]["type"] == "object"
    assert "verbatim_quote" in transformed["properties"]["name"]["properties"]
    assert transformed["properties"]["name"]["properties"]["verbatim_quote"]["type"] == "string"
    assert transformed["properties"]["name"]["properties"]["value"]["type"] == "string"
    assert "verbatim_quote" in transformed["properties"]["name"]["required"]
    assert "value" in transformed["properties"]["name"]["required"]

    # Check age transformation
    assert transformed["properties"]["age"]["properties"]["value"]["type"] == "integer"

    # Check nested property transformation
    is_active_schema = transformed["properties"]["metadata"]["properties"]["is_active"]
    assert is_active_schema["type"] == "object"
    assert is_active_schema["properties"]["value"]["type"] == "boolean"

def test_lexicon_grounded_agent_generate_prompt():
    """
    Verifies that _generate_prompt includes the necessary rules and follows the expected structure.
    """
    agent = LexiconGroundedAgent()
    task = Task(
        id="test_001",
        instruction="Extract information",
        input_text="Sample text",
        target_schema={
            "type": "object",
            "properties": {"name": {"type": "string"}}
        }
    )
    
    messages = agent._generate_prompt(task, "gpt-4o")
    
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    
    system_content = messages[0]["content"]
    user_content = messages[1]["content"]
    
    assert "QUOTE-FIRST RULE" in system_content
    assert "verbatim_quote" in system_content
    assert "BEFORE" in system_content or "first key" in system_content
    assert "ZERO TOLERANCE" in system_content
    assert "Sample text" in user_content
    assert "Extract information" in user_content
    
    # Check that invariants were applied (e.g., TS schema present)
    assert "Interface" in system_content
    assert "verbatim_quote: string" in system_content

def test_lexicon_grounded_agent_parse_result():
    """
    Verifies that _parse_result correctly strips verbatim_quote wrappers.
    """
    agent = LexiconGroundedAgent()
    
    # Nested structure with verbatim_quote
    raw_result = {
        "person": {
            "name": {"verbatim_quote": "John Doe", "value": "John Doe"},
            "age": {"verbatim_quote": "30 years old", "value": 30}
        },
        "tags": [
            {"verbatim_quote": "developer", "value": "developer"},
            {"verbatim_quote": "hacker", "value": "hacker"}
        ],
        "_tokens": {"prompt_tokens": 100, "completion_tokens": 50}
    }
    
    expected = {
        "person": {
            "name": "John Doe",
            "age": 30
        },
        "tags": ["developer", "hacker"],
        "_tokens": {"prompt_tokens": 100, "completion_tokens": 50}
    }
    
    parsed = agent._parse_result(raw_result)
    assert parsed == expected

@patch('gensie.baseline.OpenAI')
def test_lexicon_grounded_agent_run(mock_openai):
    """
    Verifies that run executes correctly, handles tokens, and parses results.
    """
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "name": {"verbatim_quote": "John", "value": "John"}
    })
    mock_response.usage = MagicMock()
    mock_response.usage.prompt_tokens = 10
    mock_response.usage.completion_tokens = 5
    mock_client.chat.completions.create.return_value = mock_response

    task = Task(
        id="test_001",
        instruction="Extract name",
        input_text="John is here",
        target_schema={
            "type": "object",
            "properties": {"name": {"type": "string"}}
        }
    )
    
    agent = LexiconGroundedAgent()
    result = agent.run(task, "gpt-4o")
    
    assert result["name"] == "John"
    assert "_tokens" in result
    assert result["_tokens"]["prompt_tokens"] == 10
    assert result["_tokens"]["completion_tokens"] == 5
