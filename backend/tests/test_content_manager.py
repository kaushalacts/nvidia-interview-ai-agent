import unittest
from unittest.mock import patch, MagicMock, Mock
import uuid
import json
import sys
from datetime import datetime

# Mock langchain modules before importing
sys.modules['langchain_core'] = MagicMock()
sys.modules['langchain_core.documents'] = MagicMock()
sys.modules['langchain_chroma'] = MagicMock()
sys.modules['langchain_huggingface'] = MagicMock()

from core.content_manager import ContentManager
from api.models import QuestionBank


class TestContentManager(unittest.TestCase):
    """Test suite for ContentManager"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.manager = ContentManager()
        
        self.valid_question = {
            "question": "What is the difference between TCP and UDP?",
            "expected_answer": "TCP is connection-oriented and reliable, while UDP is connectionless and faster but less reliable.",
            "topic_tags": ["networking", "protocols"],
            "difficulty_level": 3,
            "stage_suitable": "technical_deep_dive",
            "source_url": "https://example.com/networking",
            "metadata": {"source": "manual_entry", "author": "admin"}
        }
    
    def test_validate_question_valid(self):
        """Test that valid question passes validation"""
        is_valid, error = self.manager.validate_question(self.valid_question)
        
        self.assertTrue(is_valid)
        self.assertEqual(error, "")
    
    def test_validate_question_empty_question(self):
        """Test that empty question field fails validation"""
        invalid_question = self.valid_question.copy()
        invalid_question["question"] = ""
        
        is_valid, error = self.manager.validate_question(invalid_question)
        
        self.assertFalse(is_valid)
        self.assertIn("question", error.lower())
    
    def test_validate_question_empty_answer(self):
        """Test that empty expected_answer fails validation"""
        invalid_question = self.valid_question.copy()
        invalid_question["expected_answer"] = ""
        
        is_valid, error = self.manager.validate_question(invalid_question)
        
        self.assertFalse(is_valid)
        self.assertIn("expected_answer", error.lower())
    
    def test_validate_question_invalid_difficulty_low(self):
        """Test that difficulty < 1 fails validation"""
        invalid_question = self.valid_question.copy()
        invalid_question["difficulty_level"] = 0
        
        is_valid, error = self.manager.validate_question(invalid_question)
        
        self.assertFalse(is_valid)
        self.assertIn("difficulty", error.lower())
    
    def test_validate_question_invalid_difficulty_high(self):
        """Test that difficulty > 5 fails validation"""
        invalid_question = self.valid_question.copy()
        invalid_question["difficulty_level"] = 6
        
        is_valid, error = self.manager.validate_question(invalid_question)
        
        self.assertFalse(is_valid)
        self.assertIn("difficulty", error.lower())
    
    def test_validate_question_invalid_stage(self):
        """Test that invalid stage name fails validation"""
        invalid_question = self.valid_question.copy()
        invalid_question["stage_suitable"] = "invalid_stage"
        
        is_valid, error = self.manager.validate_question(invalid_question)
        
        self.assertFalse(is_valid)
        self.assertIn("stage", error.lower())
    
    def test_validate_question_empty_topic_tags(self):
        """Test that empty topic_tags fails validation"""
        invalid_question = self.valid_question.copy()
        invalid_question["topic_tags"] = []
        
        is_valid, error = self.manager.validate_question(invalid_question)
        
        self.assertFalse(is_valid)
        self.assertIn("topic_tags", error.lower())
    
    def test_validate_question_invalid_url_format(self):
        """Test that invalid URL format fails validation"""
        invalid_question = self.valid_question.copy()
        invalid_question["source_url"] = "not-a-url"
        
        is_valid, error = self.manager.validate_question(invalid_question)
        
        self.assertFalse(is_valid)
        self.assertIn("url", error.lower())
    
    @patch('core.content_manager.ContentManager.check_duplicate')
    @patch('core.content_manager.ContentManager.store_question')
    def test_ingest_question_success(self, mock_store, mock_check_dup):
        """Test successful single question ingestion"""
        # Mock no duplicate found
        mock_check_dup.return_value = (False, None)
        
        # Mock successful storage
        test_id = str(uuid.uuid4())
        mock_store.return_value = test_id
        
        result = self.manager.ingest_question(self.valid_question)
        
        self.assertEqual(result["status"], "accepted")
        self.assertEqual(result["content_id"], test_id)
        self.assertTrue(result["embedding_stored"])
        self.assertNotIn("reason", result)
    
    @patch('core.content_manager.ContentManager.check_duplicate')
    def test_ingest_question_duplicate(self, mock_check_dup):
        """Test that duplicate question is rejected"""
        # Mock duplicate found
        existing_id = str(uuid.uuid4())
        mock_check_dup.return_value = (True, existing_id)
        
        result = self.manager.ingest_question(self.valid_question)
        
        self.assertEqual(result["status"], "rejected")
        self.assertIn("reason", result)
        self.assertIn("duplicate", result["reason"].lower())
        self.assertFalse(result["embedding_stored"])
    
    def test_ingest_question_validation_failure(self):
        """Test that invalid question is rejected"""
        invalid_question = self.valid_question.copy()
        invalid_question["difficulty_level"] = 10
        
        result = self.manager.ingest_question(invalid_question)
        
        self.assertEqual(result["status"], "rejected")
        self.assertIn("reason", result)
        self.assertFalse(result["embedding_stored"])
    
    @patch('core.content_manager.ContentManager.ingest_question')
    def test_batch_ingest_questions(self, mock_ingest):
        """Test batch ingestion processes multiple questions"""
        # Mock responses for batch
        mock_ingest.side_effect = [
            {"status": "accepted", "content_id": "id-1", "embedding_stored": True},
            {"status": "rejected", "reason": "Duplicate question", "embedding_stored": False},
            {"status": "accepted", "content_id": "id-2", "embedding_stored": True},
        ]
        
        questions = [self.valid_question, self.valid_question, self.valid_question]
        
        result = self.manager.batch_ingest_questions(questions)
        
        self.assertIn("job_id", result)
        self.assertEqual(result["accepted_count"], 2)
        self.assertEqual(result["rejected_count"], 1)
        self.assertEqual(len(result["rejected_reasons"]), 1)
    
    @patch('core.content_manager.SessionLocal')
    @patch('core.content_manager.get_embeddings')
    @patch('langchain_chroma.Chroma')
    def test_store_question_creates_embedding(self, mock_chroma, mock_embeddings, mock_session_local):
        """Test that storing question creates database record and embedding"""
        # Mock database session
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        # Mock embeddings
        mock_embeddings.return_value = MagicMock()
        
        # Mock ChromaDB
        mock_vectordb = MagicMock()
        mock_chroma.return_value = mock_vectordb
        
        content_id = self.manager.store_question(self.valid_question)
        
        # Verify database add was called
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        
        # Verify ChromaDB add was called
        mock_vectordb.add_documents.assert_called_once()
        
        # Verify UUID was returned
        self.assertIsNotNone(content_id)
        uuid.UUID(content_id)  # Should not raise exception
    
    @patch('core.content_manager.get_embeddings')
    @patch('langchain_chroma.Chroma')
    def test_check_duplicate_finds_similar_question(self, mock_chroma, mock_embeddings):
        """Test that duplicate checking finds similar questions"""
        # Mock embeddings
        mock_embeddings.return_value = MagicMock()
        
        # Mock ChromaDB with similar result
        mock_vectordb = MagicMock()
        mock_doc = MagicMock()
        mock_doc.metadata = {"question_id": "existing-id"}
        
        # Mock similarity search with high similarity
        mock_vectordb.similarity_search_with_score.return_value = [
            (mock_doc, 0.05)  # Low distance = high similarity
        ]
        mock_chroma.return_value = mock_vectordb
        
        is_duplicate, existing_id = self.manager.check_duplicate(
            "What is the difference between TCP and UDP?"
        )
        
        self.assertTrue(is_duplicate)
        self.assertEqual(existing_id, "existing-id")
    
    @patch('core.content_manager.get_embeddings')
    @patch('langchain_chroma.Chroma')
    def test_check_duplicate_no_similar_question(self, mock_chroma, mock_embeddings):
        """Test that duplicate checking returns False for unique questions"""
        # Mock embeddings
        mock_embeddings.return_value = MagicMock()
        
        # Mock ChromaDB with no similar results
        mock_vectordb = MagicMock()
        mock_vectordb.similarity_search_with_score.return_value = []
        mock_chroma.return_value = mock_vectordb
        
        is_duplicate, existing_id = self.manager.check_duplicate(
            "What is quantum computing?"
        )
        
        self.assertFalse(is_duplicate)
        self.assertIsNone(existing_id)
    
    @patch('core.content_manager.get_embeddings')
    def test_check_duplicate_embeddings_unavailable(self, mock_embeddings):
        """Test duplicate checking when embeddings are unavailable"""
        # Mock embeddings unavailable
        mock_embeddings.return_value = None
        
        is_duplicate, existing_id = self.manager.check_duplicate(
            "What is machine learning?"
        )
        
        # Should return not duplicate if embeddings unavailable
        self.assertFalse(is_duplicate)
        self.assertIsNone(existing_id)


if __name__ == '__main__':
    unittest.main()
