import pytest
from gensie.baseline import InvariantPromptMixin, MIRAAgent, ARCANEAgent, VIGILAgent

def test_invariant_prompt_mixin_date_rule():
    mixin = InvariantPromptMixin()
    base_prompt = "Extract data."
    target_schema = {"type": "object", "properties": {"date": {"type": "string"}}}
    
    # Test without use_dates (default)
    prompt_no_dates = mixin.apply_invariants(base_prompt, target_schema)
    assert "Date Formatting Rule" not in prompt_no_dates
    
    # Test with use_dates=True
    # This should fail initially because use_dates is not a parameter yet
    prompt_with_dates = mixin.apply_invariants(base_prompt, target_schema, use_dates=True)
    assert "4. Date Formatting Rule: Format all date and time fields according strictly to the schema's expected format (e.g., ISO 8601 YYYY-MM-DD or HH:MM:SS). Ensure lexical precision for these fields." in prompt_with_dates

def test_agents_have_use_dates_attribute():
    mira = MIRAAgent()
    arcane = ARCANEAgent()
    vigil = VIGILAgent()
    
    assert hasattr(mira, "use_dates")
    assert mira.use_dates is False
    
    assert hasattr(arcane, "use_dates")
    assert arcane.use_dates is False
    
    assert hasattr(vigil, "use_dates")
    assert vigil.use_dates is False
