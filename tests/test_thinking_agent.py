import json
from gensie.baseline import ThinkingAgent

def test_thinking_agent_parse_response_with_tags():
    agent = ThinkingAgent()
    content = """
<think>
The user wants to extract person names.
Found "Alice" and "Bob".
</think>
<answer>
{
  "names": ["Alice", "Bob"]
}
</answer>
"""
    result = agent._parse_response(content)
    assert result == {"names": ["Alice", "Bob"]}

def test_thinking_agent_parse_response_with_markdown():
    agent = ThinkingAgent()
    content = """
<think>
Analyzing...
</think>
<answer>
```json
{
  "names": ["Alice"]
}
```
</answer>
"""
    result = agent._parse_response(content)
    assert result == {"names": ["Alice"]}

def test_thinking_agent_parse_response_fallback():
    agent = ThinkingAgent()
    content = '{"names": ["Charlie"]}'
    result = agent._parse_response(content)
    assert result == {"names": ["Charlie"]}

def test_thinking_agent_parse_response_error():
    agent = ThinkingAgent()
    content = "<answer>Not JSON</answer>"
    result = agent._parse_response(content)
    assert "error" in result
    assert result["raw_content"] == content
