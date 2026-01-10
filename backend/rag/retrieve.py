from langchain_community.embeddings import OllamaEmbeddings
from langchain_chroma import Chroma

CHROMA_DIR = "/app/rag/chroma_db"

embeddings = OllamaEmbeddings(
    base_url="http://ollama:11434",
    model="nomic-embed-text"
)

def query_articles(query: str, k: int = 3):
    vectordb = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings
    )

    results = vectordb.similarity_search(query, k=k)

    return [
        {
            "content": doc.page_content[:500],
            "metadata": doc.metadata
        }
        for doc in results
    ]
