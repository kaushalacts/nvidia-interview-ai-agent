# rag/retrieve.py
from typing import List
from rag.embed_store import get_embeddings
import logging

logger = logging.getLogger(__name__)

CHROMA_DIR = "rag/chroma_db"


def query_articles(query: str, k: int = 3) -> List[dict]:
    embeddings = get_embeddings()
    if not embeddings:
        return []

    try:
        from langchain_chroma import Chroma

        vectordb = Chroma(
            persist_directory=CHROMA_DIR,
            embedding_function=embeddings,
        )

        results = vectordb.similarity_search(query, k=k)

        return [
            {
                "content": doc.page_content[:500],
                "metadata": doc.metadata,
            }
            for doc in results
        ]

    except Exception as e:
        logger.warning(f"⚠️ RAG query failed: {e}")
        return []
