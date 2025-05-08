#경로 문제로 인해 분리하여 정리
import json
from app.config.settings import settings
import chromadb
from chromadb.config import Settings as ChromaSettings

# 메타데이터 로드
with open(settings.abs_metadata_supplement, encoding="utf-8") as f:
    metadata_supplement = json.load(f)

# 벡터 DB 연결
client = chromadb.Client(ChromaSettings(persist_directory=settings.CHROMA_DIR))
collection = client.get_or_create_collection(settings.COLLECTION_NAME)

