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
