#경로 문제로 인해 분리하여 정리
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from app.config.settings import settings

client = chromadb.Client(ChromaSettings(persist_directory=settings.CHROMA_DIR))
collection = client.get_or_create_collection(settings.COLLECTION_NAME)
embed_model = SentenceTransformer(settings.EMBED_MODEL_ID)
