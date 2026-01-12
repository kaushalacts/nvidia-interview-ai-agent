# rag/embed_store.py
from langchain_core.documents import Document
from typing import Optional
import logging

logger = logging.getLogger(__name__)

CHROMA_DIR = "rag/chroma_db"

_embeddings = None
_embeddings_error: Optional[str] = None


def get_embeddings():
    """
    Lazy + resilient embedding loader.
    """
    global _embeddings, _embeddings_error

    if _embeddings:
        return _embeddings

    if _embeddings_error:
        return None

    try:
        from langchain_huggingface import HuggingFaceEmbeddings

        _embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        logger.info("✅ Embeddings loaded")

        return _embeddings

    except Exception as e:
        _embeddings_error = str(e)
        logger.warning(f"⚠️ Embeddings disabled: {e}")
        return None


def store_article(title: str, content: str, metadata: dict):
    embeddings = get_embeddings()
    if not embeddings:
        return False

    try:
        from langchain_chroma import Chroma

        doc = Document(
            page_content=content,
            metadata={"title": title, **metadata},
        )

        vectordb = Chroma(
            persist_directory=CHROMA_DIR,
            embedding_function=embeddings,
        )

        vectordb.add_documents([doc])
        return True

    except Exception as e:
        logger.warning(f"⚠️ Failed to store article: {e}")
        return False
