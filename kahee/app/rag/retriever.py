from app.config import settings
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# 초기화
client = chromadb.Client(Settings(persist_directory=settings.CHROMA_DIR))
collection = client.get_or_create_collection(settings.COLLECTION_NAME)
embed_model = SentenceTransformer(settings.EMBED_MODEL_ID)

def retrieve(query, top_k=5):
    q_emb = embed_model.encode(query).tolist()
    out = collection.query(
        query_embeddings=[q_emb],
        n_results=top_k,
        include=["metadatas"]
    )
    texts = [m["text"] for m in out["metadatas"][0]]
    return texts
