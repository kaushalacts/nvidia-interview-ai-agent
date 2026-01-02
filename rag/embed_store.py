from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

CHROMA_DIR = "rag/chroma_db"

def store_article(title: str, content: str, metadata: dict):
    doc = Document(
        page_content=content,
        metadata={
            "title": title,
            **metadata
        }
    )

    vectordb = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings
    )

    vectordb.add_documents([doc])

