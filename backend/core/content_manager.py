"""
Content Manager for n8n webhook integration.

Provides API endpoints for n8n to ingest interview questions,
with validation, deduplication, and ChromaDB embedding storage.
"""

import uuid
import json
import logging
from typing import List, Optional, Tuple
from datetime import datetime

from api.models import QuestionBank
from api.database import SessionLocal
from rag.embed_store import get_embeddings
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

# ChromaDB collection for question bank
QUESTION_BANK_COLLECTION = "question_bank"
CHROMA_DIR = "rag/chroma_db"

# Valid stage names
VALID_STAGES = [
    "warmup",
    "technical_deep_dive",
    "problem_solving",
    "behavioral",
    "wrap_up"
]


class ContentManager:
    """
    Manages ingestion of interview questions from n8n webhooks.
    
    Provides validation, deduplication, and storage functionality
    for automated content pipeline.
    """
    
    def __init__(self):
        """Initialize the ContentManager"""
        pass
    
    def ingest_question(self, question_data: dict) -> dict:
        """
        Ingests a single question from n8n.
        
        Args:
            question_data: {
                "question": str,
                "expected_answer": str,
                "topic_tags": List[str],
                "difficulty_level": int (1-5),
                "stage_suitable": str,  # "warmup", "technical", etc.
                "source_url": str,
                "metadata": dict
            }
        
        Returns:
            {
                "content_id": str (uuid),
                "status": "accepted" | "rejected",
                "reason": str (if rejected),
                "embedding_stored": bool
            }
        """
        # Validate question
        is_valid, error_message = self.validate_question(question_data)
        if not is_valid:
            return {
                "status": "rejected",
                "reason": f"Validation failed: {error_message}",
                "embedding_stored": False
            }
        
        # Check for duplicates
        is_duplicate, existing_id = self.check_duplicate(question_data["question"])
        if is_duplicate:
            return {
                "status": "rejected",
                "reason": f"Duplicate question (existing ID: {existing_id})",
                "embedding_stored": False
            }
        
        # Store question
        try:
            content_id = self.store_question(question_data)
            return {
                "content_id": content_id,
                "status": "accepted",
                "embedding_stored": True
            }
        except Exception as e:
            logger.error(f"Failed to store question: {e}")
            return {
                "status": "rejected",
                "reason": f"Storage failed: {str(e)}",
                "embedding_stored": False
            }
    
    def batch_ingest_questions(self, questions: List[dict]) -> dict:
        """
        Ingests multiple questions from n8n (up to 50).
        
        Args:
            questions: List of question data dictionaries
        
        Returns:
            {
                "job_id": str (uuid),
                "accepted_count": int,
                "rejected_count": int,
                "rejected_reasons": List[dict]
            }
        """
        job_id = str(uuid.uuid4())
        accepted_count = 0
        rejected_count = 0
        rejected_reasons = []
        
        for i, question_data in enumerate(questions):
            result = self.ingest_question(question_data)
            
            if result["status"] == "accepted":
                accepted_count += 1
            else:
                rejected_count += 1
                rejected_reasons.append({
                    "index": i,
                    "question": question_data.get("question", "")[:100],
                    "reason": result.get("reason", "Unknown error")
                })
        
        return {
            "job_id": job_id,
            "accepted_count": accepted_count,
            "rejected_count": rejected_count,
            "rejected_reasons": rejected_reasons
        }
    
    def validate_question(self, question_data: dict) -> Tuple[bool, str]:
        """
        Validates question data.
        
        Returns: (is_valid, error_message)
        
        Checks:
        - Non-empty question and expected_answer
        - Valid difficulty_level (1-5)
        - Valid stage_suitable (warmup, technical_deep_dive, problem_solving, behavioral, wrap_up)
        - topic_tags is non-empty list
        - source_url is valid URL format
        """
        # Check required fields exist
        required_fields = ["question", "expected_answer", "topic_tags", 
                          "difficulty_level", "stage_suitable", "source_url"]
        for field in required_fields:
            if field not in question_data:
                return False, f"Missing required field: {field}"
        
        # Check non-empty question
        if not question_data["question"] or not isinstance(question_data["question"], str) or len(question_data["question"].strip()) == 0:
            return False, "Question cannot be empty"
        
        # Check non-empty expected_answer
        if not question_data["expected_answer"] or not isinstance(question_data["expected_answer"], str) or len(question_data["expected_answer"].strip()) == 0:
            return False, "Expected_answer cannot be empty"
        
        # Check difficulty_level (1-5)
        try:
            difficulty = int(question_data["difficulty_level"])
            if difficulty < 1 or difficulty > 5:
                return False, "Difficulty_level must be between 1 and 5"
        except (ValueError, TypeError):
            return False, "Difficulty_level must be an integer"
        
        # Check valid stage
        stage = question_data["stage_suitable"]
        if stage not in VALID_STAGES:
            return False, f"Stage_suitable must be one of: {', '.join(VALID_STAGES)}"
        
        # Check topic_tags is non-empty list
        topic_tags = question_data["topic_tags"]
        if not isinstance(topic_tags, list) or len(topic_tags) == 0:
            return False, "Topic_tags must be a non-empty list"
        
        # Check URL format
        source_url = question_data["source_url"]
        if not isinstance(source_url, str) or not (source_url.startswith("http://") or source_url.startswith("https://")):
            return False, "Source_url must be a valid URL (starting with http:// or https://)"
        
        return True, ""
    
    def check_duplicate(self, question_text: str) -> Tuple[bool, Optional[str]]:
        """
        Checks if question is duplicate using ChromaDB similarity.
        
        Returns: (is_duplicate, existing_question_id)
        
        Uses ChromaDB to:
        - Embed the question
        - Search for similar questions (cosine similarity > 0.9)
        - Return True if duplicate found
        """
        embeddings = get_embeddings()
        if not embeddings:
            logger.warning("Embeddings unavailable, skipping duplicate check")
            return False, None
        
        try:
            from langchain_chroma import Chroma
            
            vectordb = Chroma(
                persist_directory=CHROMA_DIR,
                embedding_function=embeddings,
                collection_name=QUESTION_BANK_COLLECTION
            )
            
            # Search for similar questions
            results = vectordb.similarity_search_with_score(question_text, k=3)
            
            # Check if any result has high similarity (> 0.9)
            # Note: Chroma returns distance, not similarity
            # Lower distance = higher similarity
            # For cosine distance: similarity = 1 - distance
            for doc, distance in results:
                similarity = 1 - distance
                if similarity > 0.9:
                    existing_id = doc.metadata.get("question_id")
                    logger.info(f"Duplicate found: {existing_id} (similarity: {similarity:.3f})")
                    return True, existing_id
            
            return False, None
            
        except Exception as e:
            logger.warning(f"Duplicate check failed: {e}")
            # If duplicate check fails, assume not duplicate to allow ingestion
            return False, None
    
    def store_question(self, question_data: dict) -> str:
        """
        Stores question in database and ChromaDB.
        
        Returns: content_id (uuid)
        
        Steps:
        1. Create QuestionBank record in database
        2. Generate embedding for question
        3. Store embedding in ChromaDB with metadata
        4. Return generated UUID
        """
        content_id = str(uuid.uuid4())
        db = SessionLocal()
        
        try:
            # Create database record
            question_record = QuestionBank(
                question_id=content_id,
                question_text=question_data["question"],
                expected_answer=question_data["expected_answer"],
                topic_tags=json.dumps(question_data["topic_tags"]),
                difficulty_level=question_data["difficulty_level"],
                stage_suitable=question_data["stage_suitable"],
                source_url=question_data["source_url"],
                created_date=datetime.utcnow(),
                usage_count=0,
                avg_user_score=None,
                is_active=True
            )
            
            db.add(question_record)
            db.commit()
            
            # Store embedding in ChromaDB
            embeddings = get_embeddings()
            if embeddings:
                try:
                    from langchain_chroma import Chroma
                    
                    vectordb = Chroma(
                        persist_directory=CHROMA_DIR,
                        embedding_function=embeddings,
                        collection_name=QUESTION_BANK_COLLECTION
                    )
                    
                    # Create document with metadata
                    doc = Document(
                        page_content=question_data["question"],
                        metadata={
                            "question_id": content_id,
                            "difficulty_level": question_data["difficulty_level"],
                            "stage": question_data["stage_suitable"],
                            "topic_tags": json.dumps(question_data["topic_tags"]),
                            "source_url": question_data["source_url"]
                        }
                    )
                    
                    vectordb.add_documents([doc])
                    logger.info(f"Question {content_id} stored in ChromaDB")
                    
                except Exception as e:
                    logger.warning(f"Failed to store embedding: {e}")
                    # Continue even if embedding fails
            
            return content_id
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
