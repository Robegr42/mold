import pytest
from gensie.baseline import InvariantPromptMixin

class DummyAgent(InvariantPromptMixin):
    pass

def test_apply_invariants():
    agent = DummyAgent()
    base_prompt = "Extract the data from the text."
    target_schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"}
        }
    }
    
    modified_prompt = agent.apply_invariants(base_prompt, target_schema)
    
    assert base_prompt in modified_prompt
    # Check for extract-or-null rule
    assert "Extract values that are explicitly stated or strongly implied" in modified_prompt
    # Check for dialect rule
    assert "Iberian" in modified_prompt
    assert "Latin American" in modified_prompt
    # Check for typescript compressed schema
    # (Just verifying it appears, since compress_schema_to_ts handles the actual compression)
    assert "name: string" in modified_prompt or "name?: string" in modified_prompt

