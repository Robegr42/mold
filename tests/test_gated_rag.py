import unittest
from unittest.mock import MagicMock, patch
import numpy as np
from gensie.baseline import GatedRAGModule
from gensie.task import Task

class TestGatedRAGModule(unittest.TestCase):
    def setUp(self):
        # Mock SentenceTransformer to avoid loading the model
        with patch('gensie.baseline.SentenceTransformer') as mock_st:
            self.mock_model = mock_st.return_value
            self.mock_model.encode.side_effect = lambda x: np.random.rand(len(x), 384)
            
            # Mock os.path.exists to return True for the model path
            with patch('os.path.exists', return_value=True):
                # Mock _initialize_index to avoid loading data
                with patch.object(GatedRAGModule, '_initialize_index'):
                    self.rag = GatedRAGModule()
                    self.rag.index = MagicMock()
                    self.rag.examples = [{"id": 0}, {"id": 1}, {"id": 2}, {"id": 3}]
                    self.rag.model = self.mock_model

    def test_gated_examples_above_threshold(self):
        # threshold = 0.65
        # similarity = 1 - D/2
        # similarity > 0.65 => 1 - D/2 > 0.65 => 0.35 > D/2 => D < 0.7
        
        # Mock search to return a distance of 0.6 (similarity = 0.7)
        D = np.array([[0.6, 0.8, 0.9]], dtype='float32')
        I = np.array([[0, 1, 2]], dtype='int64')
        self.rag.index.search.return_value = (D, I)
        
        task = Task(id="test_001", instruction="test", input_text="test", target_schema={})
        examples, ok = self.rag.get_gated_examples(task, k=3, threshold=0.65)
        
        self.assertTrue(ok)
        self.assertEqual(len(examples), 3)
        self.assertEqual(examples[0]["id"], 0)

    def test_gated_examples_below_threshold(self):
        # threshold = 0.65
        # Mock search to return a distance of 0.8 (similarity = 1 - 0.4 = 0.6)
        D = np.array([[0.8, 0.9, 1.0]], dtype='float32')
        I = np.array([[0, 1, 2]], dtype='int64')
        self.rag.index.search.return_value = (D, I)
        
        task = Task(id="test_001", instruction="test", input_text="test", target_schema={})
        examples, ok = self.rag.get_gated_examples(task, k=3, threshold=0.65)
        
        self.assertFalse(ok)
        self.assertEqual(examples, [])

    def test_gated_examples_exactly_threshold(self):
        # threshold = 0.65
        # 1 - D/2 = 0.65 => D/2 = 0.35 => D = 0.7
        D = np.array([[0.7, 0.8, 0.9]], dtype='float32')
        I = np.array([[0, 1, 2]], dtype='int64')
        self.rag.index.search.return_value = (D, I)
        
        task = Task(id="test_001", instruction="test", input_text="test", target_schema={})
        examples, ok = self.rag.get_gated_examples(task, k=3, threshold=0.65)
        
        # Usually threshold is inclusive
        self.assertTrue(ok)
        self.assertEqual(len(examples), 3)

if __name__ == '__main__':
    unittest.main()
