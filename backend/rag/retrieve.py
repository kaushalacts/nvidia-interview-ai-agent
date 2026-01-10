from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

CHROMA_DIR = "rag/chroma_db"

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

def query_articles(query: str, k: int = 3):
    vectordb = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings
    )

    results = vectordb.similarity_search(query, k=k)

    return [
        {
            "content": doc.page_content[:500],  # preview
            "metadata": doc.metadata
        }
        for doc in results
    ]

