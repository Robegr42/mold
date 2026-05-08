import pytest
from gensie.baseline import LexiconGroundedAgent

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
    from gensie.task import Task
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
