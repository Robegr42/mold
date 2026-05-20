import unittest
from unittest.mock import MagicMock, patch
import numpy as np
from gensie.baseline import GatedRAGModule
from gensie.task import Task

class TestGatedRAGModule(unittest.TestCase):
    def setUp(self):
        # Mock TextEmbedding to avoid loading the model
        with patch('gensie.baseline.TextEmbedding') as mock_te:
            self.mock_model = mock_te.return_value
            # .embed() returns a generator of numpy arrays
            self.mock_model.embed.side_effect = lambda x: (np.random.rand(384) for _ in range(len(x)))
            
            # Mock _initialize_index to avoid loading data
            with patch.object(GatedRAGModule, '_initialize_index'):
                self.rag = GatedRAGModule()
                self.rag.index = MagicMock()
                self.rag.examples = [{"id": 0}, {"id": 1}, {"id": 2}, {"id": 3}]
                self.rag.model = self.mock_model

    def test_gated_examples_above_threshold(self):
        # threshold = 0.55
        # similarity = 1 - D/2
        # similarity > 0.55 => 1 - D/2 > 0.55 => 0.45 > D/2 => D < 0.9
        
        # Mock search to return a distance of 0.8 (similarity = 0.6)
        D = np.array([[0.8, 1.0, 1.1]], dtype='float32')
        I = np.array([[0, 1, 2]], dtype='int64')
        self.rag.index.search.return_value = (D, I)
        
        task = Task(id="test_001", instruction="test", input_text="test", target_schema={})
        examples, ok = self.rag.get_gated_examples(task, k=3) # Uses default 0.55
        
        self.assertTrue(ok)
        self.assertEqual(len(examples), 3)
        self.assertEqual(examples[0]["id"], 0)

    def test_gated_examples_below_threshold(self):
        # threshold = 0.55
        # Mock search to return a distance of 1.0 (similarity = 1 - 0.5 = 0.5)
        D = np.array([[1.0, 1.1, 1.2]], dtype='float32')
        I = np.array([[0, 1, 2]], dtype='int64')
        self.rag.index.search.return_value = (D, I)
        
        task = Task(id="test_001", instruction="test", input_text="test", target_schema={})
        examples, ok = self.rag.get_gated_examples(task, k=3, threshold=0.55)
        
        self.assertFalse(ok)
        self.assertEqual(examples, [])

    def test_gated_examples_exactly_threshold(self):
        # threshold = 0.55
        # 1 - D/2 = 0.55 => D/2 = 0.45 => D = 0.9
        D = np.array([[0.9, 1.0, 1.1]], dtype='float32')
        I = np.array([[0, 1, 2]], dtype='int64')
        self.rag.index.search.return_value = (D, I)
        
        task = Task(id="test_001", instruction="test", input_text="test", target_schema={})
        examples, ok = self.rag.get_gated_examples(task, k=3, threshold=0.55)
        
        # Usually threshold is inclusive
        self.assertTrue(ok)
        self.assertEqual(len(examples), 3)

if __name__ == '__main__':
    unittest.main()
