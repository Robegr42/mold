import unittest
from unittest.mock import MagicMock, patch
import json
from gensie.baseline import SyntheticAnchorAgent
from gensie.task import Task

class TestSyntheticAnchorAgent(unittest.TestCase):
    def setUp(self):
        self.task = Task(
            id="test_001",
            instruction="Extract names",
            input_text="Juan Perez vive en Madrid.",
            target_schema={
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"]
            }
        )
        
        # Patch dependencies
        self.patch_openai = patch("gensie.baseline.OpenAI")
        self.patch_rag = patch("gensie.baseline.GatedRAGModule")
        self.patch_arch = patch("gensie.baseline.ArchitectModule")
        
        self.mock_openai = self.patch_openai.start()
        self.mock_rag_class = self.patch_rag.start()
        self.mock_arch_class = self.patch_arch.start()
        
        # Configure instance mocks
        self.mock_rag = self.mock_rag_class.return_value
        self.mock_arch = self.mock_arch_class.return_value
        
        self.agent = SyntheticAnchorAgent()

    def tearDown(self):
        self.patch_openai.stop()
        self.patch_rag.stop()
        self.patch_arch.stop()

    def test_run_with_relevant_rag(self):
        # Case 1: RAG is relevant
        self.mock_rag.get_gated_examples.return_value = ([{"input_text": "Ex input", "output": {"name": "Juan"}}], True)
        self.mock_arch.get_reasoning_hints.return_value = "Hint 1"
        
        mock_response1 = MagicMock()
        mock_response1.choices = [MagicMock(message=MagicMock(content="Pass 1 analysis"))]
        mock_response1.usage = MagicMock(total_tokens=10)
        
        mock_response2 = MagicMock()
        mock_response2.choices = [MagicMock(message=MagicMock(content='{"name": "Juan Perez"}'))]
        mock_response2.usage = MagicMock(total_tokens=20)
        
        self.agent.client.chat.completions.create.side_effect = [mock_response1, mock_response2]
        
        result = self.agent.run(self.task, "gpt-4o")
        
        self.assertEqual(result["name"], "Juan Perez")
        self.assertEqual(result["_tokens"], 30)
        self.mock_rag.get_gated_examples.assert_called_once_with(self.task, k=3, threshold=0.55)

    def test_run_with_synthetic_fallback(self):
        # Case 2: RAG not relevant, synthesis succeeds
        self.mock_rag.get_gated_examples.return_value = ([], False)
        self.mock_arch.synthesize_example.return_value = {"text": "Synthetic text", "json": {"name": "Synthetic Name"}}
        self.mock_arch.get_reasoning_hints.return_value = "Hint 1"
        
        mock_response1 = MagicMock()
        mock_response1.choices = [MagicMock(message=MagicMock(content="Pass 1 analysis"))]
        mock_response1.usage = MagicMock(total_tokens=15)
        
        mock_response2 = MagicMock()
        mock_response2.choices = [MagicMock(message=MagicMock(content='{"name": "Juan Perez"}'))]
        mock_response2.usage = MagicMock(total_tokens=25)
        
        self.agent.client.chat.completions.create.side_effect = [mock_response1, mock_response2]
        
        result = self.agent.run(self.task, "gpt-4o")
        
        self.assertEqual(result["name"], "Juan Perez")
        self.assertEqual(result["_tokens"], 40)
        self.mock_arch.synthesize_example.assert_called_once_with(self.task, "gpt-4o")
        
        # Verify Pass 1 prompt contains the synthetic directive
        args, kwargs = self.agent.client.chat.completions.create.call_args_list[0]
        pass1_messages = kwargs['messages']
        pass1_content = pass1_messages[1]['content']
        self.assertIn("No historical examples found. Use this synthetic example to understand the target schema structure.", pass1_content)
        self.assertIn("Synthetic text", pass1_content)
        self.assertIn('"name": "Synthetic Name"', pass1_content)

if __name__ == "__main__":
    unittest.main()
