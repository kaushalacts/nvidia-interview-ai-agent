from langchain_community.embeddings import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

embeddings = OllamaEmbeddings(
    base_url="http://ollama:11434",
    model="nomic-embed-text"
)

CHROMA_DIR = "/app/rag/chroma_db"

def store_article(title: str, content: str, metadata: dict):
    doc = Document(
        page_content=content,
        metadata={"title": title, **metadata}
    )

    vectordb = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings
    )

    vectordb.add_documents([doc])
