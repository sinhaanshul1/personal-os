import os
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv(override=True)

# Configuration
CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "assistant_memory"

# Initialize Embeddings
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

def get_vector_db():
    """Initialize or load the Chroma vector database."""
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_PATH
    )

async def add_memories(texts: list[str], metadatas: list[dict] = None):
    """Add a list of strings to the vector database."""
    db = get_vector_db()
    await db.aadd_texts(texts=texts, metadatas=metadatas)

async def query_memories(query: str, k: int = 5):
    """Query the vector database for relevant memories."""
    db = get_vector_db()
    docs = await db.asimilarity_search(query, k=k)
    return docs
