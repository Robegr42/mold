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
