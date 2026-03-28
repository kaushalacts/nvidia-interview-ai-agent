import unittest
from unittest.mock import patch, MagicMock
from agents.enhanced_evaluator_agent import EnhancedEvaluatorAgent


class TestEnhancedEvaluatorAgent(unittest.TestCase):
    """Test suite for EnhancedEvaluatorAgent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.agent = EnhancedEvaluatorAgent()
        self.sample_question = "Explain the difference between TCP and UDP protocols."
        self.sample_response = "TCP is connection-oriented and provides reliable delivery with error checking, while UDP is connectionless and faster but doesn't guarantee delivery."
        self.sample_expected = "TCP is connection-oriented with reliability guarantees through acknowledgments and retransmission. UDP is connectionless with no reliability guarantees but lower overhead."
        self.sample_context = {
            "session_id": "test-123",
            "user_id": "user-1",
            "current_stage": "TECHNICAL_DEEP_DIVE",
            "difficulty_level": 3,
            "weak_areas": ["error handling", "edge cases"],
            "strong_areas": ["OOP basics", "networking fundamentals"],
            "conversation_history": []
        }
    
    @patch('agents.enhanced_evaluator_agent.generate_answer')
    def test_evaluate_response_returns_correct_structure(self, mock_generate):
        """Test that evaluation returns dict with all required fields"""
        # Mock LLM response with structured JSON
        mock_generate.return_value = """
        {
            "technical_accuracy": 85,
            "depth_of_understanding": 70,
            "communication_clarity": 90,
            "problem_solving_approach": 75,
            "feedback": "Strong understanding of core concepts. Good communication clarity.",
            "identified_weak_areas": ["error handling details", "edge case consideration"],
            "identified_strong_areas": ["core protocol concepts", "clear explanation"]
        }
        """
        
        result = self.agent.evaluate_response(
            self.sample_question,
            self.sample_response,
            self.sample_expected,
            self.sample_context
        )
        
        # Verify all required fields are present
        self.assertIn("technical_accuracy", result)
        self.assertIn("depth_of_understanding", result)
        self.assertIn("communication_clarity", result)
        self.assertIn("problem_solving_approach", result)
        self.assertIn("overall_score", result)
        self.assertIn("feedback", result)
        self.assertIn("identified_weak_areas", result)
        self.assertIn("identified_strong_areas", result)
    
    @patch('agents.enhanced_evaluator_agent.generate_answer')
    def test_scores_are_in_valid_range(self, mock_generate):
        """Test that all scores are within 0-100 range"""
        mock_generate.return_value = """
        {
            "technical_accuracy": 85,
            "depth_of_understanding": 70,
            "communication_clarity": 90,
            "problem_solving_approach": 75,
            "feedback": "Good work",
            "identified_weak_areas": ["edge cases"],
            "identified_strong_areas": ["core concepts"]
        }
        """
        
        result = self.agent.evaluate_response(
            self.sample_question,
            self.sample_response,
            self.sample_expected,
            self.sample_context
        )
        
        # Check all scores are in valid range
        self.assertGreaterEqual(result["technical_accuracy"], 0)
        self.assertLessEqual(result["technical_accuracy"], 100)
        self.assertGreaterEqual(result["depth_of_understanding"], 0)
        self.assertLessEqual(result["depth_of_understanding"], 100)
        self.assertGreaterEqual(result["communication_clarity"], 0)
        self.assertLessEqual(result["communication_clarity"], 100)
        self.assertGreaterEqual(result["problem_solving_approach"], 0)
        self.assertLessEqual(result["problem_solving_approach"], 100)
        self.assertGreaterEqual(result["overall_score"], 0)
        self.assertLessEqual(result["overall_score"], 100)
    
    @patch('agents.enhanced_evaluator_agent.generate_answer')
    def test_overall_score_calculation(self, mock_generate):
        """Test that overall_score is calculated as weighted average"""
        mock_generate.return_value = """
        {
            "technical_accuracy": 80,
            "depth_of_understanding": 60,
            "communication_clarity": 90,
            "problem_solving_approach": 70,
            "feedback": "Good work",
            "identified_weak_areas": ["depth"],
            "identified_strong_areas": ["clarity"]
        }
        """
        
        result = self.agent.evaluate_response(
            self.sample_question,
            self.sample_response,
            self.sample_expected,
            self.sample_context
        )
        
        # Calculate expected weighted average: 
        # technical(40%) + depth(30%) + communication(15%) + problem_solving(15%)
        expected_overall = (80 * 0.40) + (60 * 0.30) + (90 * 0.15) + (70 * 0.15)
        # 32 + 18 + 13.5 + 10.5 = 74
        
        self.assertEqual(result["overall_score"], 74)
    
    @patch('agents.enhanced_evaluator_agent.generate_answer')
    def test_identifies_weak_areas(self, mock_generate):
        """Test that weak areas are identified and populated"""
        mock_generate.return_value = """
        {
            "technical_accuracy": 85,
            "depth_of_understanding": 70,
            "communication_clarity": 90,
            "problem_solving_approach": 75,
            "feedback": "Good work",
            "identified_weak_areas": ["error handling", "edge cases", "scalability"],
            "identified_strong_areas": ["core concepts"]
        }
        """
        
        result = self.agent.evaluate_response(
            self.sample_question,
            self.sample_response,
            self.sample_expected,
            self.sample_context
        )
        
        # Verify weak areas is a list and not empty
        self.assertIsInstance(result["identified_weak_areas"], list)
        self.assertGreater(len(result["identified_weak_areas"]), 0)
        self.assertIn("error handling", result["identified_weak_areas"])
    
    @patch('agents.enhanced_evaluator_agent.generate_answer')
    def test_identifies_strong_areas(self, mock_generate):
        """Test that strong areas are identified and populated"""
        mock_generate.return_value = """
        {
            "technical_accuracy": 85,
            "depth_of_understanding": 70,
            "communication_clarity": 90,
            "problem_solving_approach": 75,
            "feedback": "Good work",
            "identified_weak_areas": ["edge cases"],
            "identified_strong_areas": ["core concepts", "clear explanation", "structured thinking"]
        }
        """
        
        result = self.agent.evaluate_response(
            self.sample_question,
            self.sample_response,
            self.sample_expected,
            self.sample_context
        )
        
        # Verify strong areas is a list and not empty
        self.assertIsInstance(result["identified_strong_areas"], list)
        self.assertGreater(len(result["identified_strong_areas"]), 0)
        self.assertIn("core concepts", result["identified_strong_areas"])
    
    @patch('agents.enhanced_evaluator_agent.generate_answer')
    def test_handles_llm_failure_gracefully(self, mock_generate):
        """Test graceful fallback when LLM fails"""
        # Simulate LLM failure with warning message
        mock_generate.return_value = "⚠️ AI engine is warming up."
        
        result = self.agent.evaluate_response(
            self.sample_question,
            self.sample_response,
            self.sample_expected,
            self.sample_context
        )
        
        # Should return valid structure with default values
        self.assertIn("technical_accuracy", result)
        self.assertIn("overall_score", result)
        self.assertIn("feedback", result)
        # Check that it indicates an error occurred
        self.assertIn("temporarily unavailable", result["feedback"].lower())
    
    @patch('agents.enhanced_evaluator_agent.generate_answer')
    def test_context_aware_evaluation(self, mock_generate):
        """Test that session context is used in evaluation"""
        mock_generate.return_value = """
        {
            "technical_accuracy": 85,
            "depth_of_understanding": 70,
            "communication_clarity": 90,
            "problem_solving_approach": 75,
            "feedback": "Good understanding considering TECHNICAL_DEEP_DIVE stage",
            "identified_weak_areas": ["error handling"],
            "identified_strong_areas": ["networking fundamentals"]
        }
        """
        
        result = self.agent.evaluate_response(
            self.sample_question,
            self.sample_response,
            self.sample_expected,
            self.sample_context
        )
        
        # Verify that the mock was called (meaning context was passed to prompt)
        mock_generate.assert_called_once()
        call_args = mock_generate.call_args[0][0]
        
        # Check that context info is in the prompt
        self.assertIn("TECHNICAL_DEEP_DIVE", call_args)
        self.assertIn("difficulty level: 3", call_args.lower())


if __name__ == "__main__":
    unittest.main()
