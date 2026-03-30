import json
from agents.llm import generate_answer
from typing import Any, List


class EnhancedEvaluatorAgent:
    """
    Enhanced evaluator agent that provides multi-dimensional scoring 
    of interview responses with context-aware evaluation.
    """
    
    def evaluate_response(
        self,
        question: str,
        user_response: str,
        expected_answer: str,
        session_context: dict
    ) -> dict:
        """
        Evaluate a candidate's response with multi-dimensional scoring.
        
        Args:
            question: The interview question asked
            user_response: The candidate's response
            expected_answer: The expected/ideal answer
            session_context: Current session context including stage, difficulty, weak/strong areas
            
        Returns:
            Dict with evaluation scores, feedback, and identified strengths/weaknesses
        """
        # Extract context information
        current_stage = session_context.get("current_stage", "TECHNICAL_DEEP_DIVE")
        difficulty_level = session_context.get("difficulty_level", 3)
        weak_areas = session_context.get("weak_areas", [])
        strong_areas = session_context.get("strong_areas", [])
        
        # Build context-aware evaluation prompt
        prompt = self._build_evaluation_prompt(
            question=question,
            user_response=user_response,
            expected_answer=expected_answer,
            current_stage=current_stage,
            difficulty_level=difficulty_level,
            weak_areas=weak_areas,
            strong_areas=strong_areas
        )
        
        # Get LLM evaluation
        llm_response = generate_answer(prompt)
        
        # Parse and structure the response
        evaluation = self._parse_llm_response(llm_response)
        
        # Calculate overall score as weighted average
        evaluation["overall_score"] = self._calculate_overall_score(evaluation)
        
        return evaluation
    
    def _build_evaluation_prompt(
        self,
        question: str,
        user_response: str,
        expected_answer: str,
        current_stage: str,
        difficulty_level: int,
        weak_areas: list,
        strong_areas: list
    ) -> str:
        """Build a context-aware evaluation prompt for the LLM"""
        
        prompt = f"""You are a senior technical interviewer evaluating a candidate's response.

EVALUATION CONTEXT:
- Interview Stage: {current_stage}
- Difficulty Level: {difficulty_level}/5
- Known Weak Areas: {', '.join(weak_areas) if weak_areas else 'None identified yet'}
- Known Strong Areas: {', '.join(strong_areas) if strong_areas else 'None identified yet'}

QUESTION ASKED:
{question}

EXPECTED/IDEAL ANSWER:
{expected_answer}

CANDIDATE'S RESPONSE:
{user_response}

EVALUATION TASK:
Evaluate the candidate's response across four dimensions. Provide scores from 0-100 for each:

1. TECHNICAL_ACCURACY (0-100): How technically correct is the response?
   - Consider factual accuracy, correct terminology, proper concepts

2. DEPTH_OF_UNDERSTANDING (0-100): How deep is their understanding?
   - Do they grasp underlying principles or just surface-level facts?
   - Can they explain the "why" not just the "what"?

3. COMMUNICATION_CLARITY (0-100): How clearly do they communicate?
   - Is the explanation well-structured and easy to follow?
   - Do they use appropriate examples or analogies?

4. PROBLEM_SOLVING_APPROACH (0-100): Do they demonstrate good problem-solving skills?
   - Do they consider edge cases, trade-offs, or alternative approaches?
   - Do they show systematic thinking?

ALSO IDENTIFY:
- IDENTIFIED_WEAK_AREAS: List 2-4 specific areas where the candidate showed weakness or gaps
- IDENTIFIED_STRONG_AREAS: List 2-4 specific areas where the candidate demonstrated strength
- FEEDBACK: Provide constructive feedback (2-3 sentences)

Adjust your expectations based on the difficulty level and current stage. For {current_stage} at difficulty {difficulty_level}, 
a score of 70+ indicates good performance for this stage.

CRITICAL: Respond ONLY with valid JSON in this exact format:
{{
    "technical_accuracy": <number 0-100>,
    "depth_of_understanding": <number 0-100>,
    "communication_clarity": <number 0-100>,
    "problem_solving_approach": <number 0-100>,
    "feedback": "<constructive feedback string>",
    "identified_weak_areas": ["<area1>", "<area2>"],
    "identified_strong_areas": ["<area1>", "<area2>"]
}}

JSON Response:"""
        
        return prompt
    
    def _parse_llm_response(self, llm_response: str) -> dict:
        """Parse the LLM response and extract structured evaluation"""
        
        # Check if LLM is unavailable (warming up)
        if "⚠️" in llm_response or "warming up" in llm_response.lower():
            return self._get_fallback_evaluation()
        
        try:
            # Try to extract JSON from the response
            # Sometimes LLM adds extra text before/after JSON
            start_idx = llm_response.find('{')
            end_idx = llm_response.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = llm_response[start_idx:end_idx]
                parsed = json.loads(json_str)
                
                # Validate and sanitize scores
                evaluation = {
                    "technical_accuracy": self._clamp_score(parsed.get("technical_accuracy", 50)),
                    "depth_of_understanding": self._clamp_score(parsed.get("depth_of_understanding", 50)),
                    "communication_clarity": self._clamp_score(parsed.get("communication_clarity", 50)),
                    "problem_solving_approach": self._clamp_score(parsed.get("problem_solving_approach", 50)),
                    "feedback": parsed.get("feedback", "Evaluation completed."),
                    "identified_weak_areas": parsed.get("identified_weak_areas", []),
                    "identified_strong_areas": parsed.get("identified_strong_areas", [])
                }
                
                # Ensure lists are actually lists
                if not isinstance(evaluation["identified_weak_areas"], list):
                    evaluation["identified_weak_areas"] = []
                if not isinstance(evaluation["identified_strong_areas"], list):
                    evaluation["identified_strong_areas"] = []
                
                return evaluation
            else:
                return self._get_fallback_evaluation()
                
        except (json.JSONDecodeError, ValueError, KeyError):
            # If JSON parsing fails, return fallback evaluation
            return self._get_fallback_evaluation()
    
    def _clamp_score(self, score: Any) -> int:
        """Ensure score is an integer between 0 and 100"""
        try:
            score_int = int(float(score))
            return max(0, min(100, score_int))
        except (ValueError, TypeError):
            return 50  # Default middle score
    
    def _calculate_overall_score(self, evaluation: dict) -> int:
        """
        Calculate overall score as weighted average:
        - Technical Accuracy: 40%
        - Depth of Understanding: 30%
        - Communication Clarity: 15%
        - Problem Solving Approach: 15%
        """
        overall = (
            evaluation["technical_accuracy"] * 0.40 +
            evaluation["depth_of_understanding"] * 0.30 +
            evaluation["communication_clarity"] * 0.15 +
            evaluation["problem_solving_approach"] * 0.15
        )
        
        return int(overall)
    
    def _get_fallback_evaluation(self) -> dict:
        """Return fallback evaluation when LLM is unavailable"""
        return {
            "technical_accuracy": 50,
            "depth_of_understanding": 50,
            "communication_clarity": 50,
            "problem_solving_approach": 50,
            "feedback": "Evaluation temporarily unavailable. Please try again in a moment.",
            "identified_weak_areas": [],
            "identified_strong_areas": []
        }
