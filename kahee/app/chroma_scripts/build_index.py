import sys, json, uuid, math
import chromadb
from chromadb.config import Settings
from config import settings

BATCH_SIZE = 5000

client = chromadb.Client(Settings(persist_directory=settings.CHROMA_DIR))
collection = client.get_or_create_collection(settings.COLLECTION_NAME)

SRC_JSON = sys.argv[1]

with open(SRC_JSON, "r", encoding="utf-8") as f:
    data = json.load(f)

total_len  = len(data)
ids_all        = [str(uuid.uuid4()) for _ in data]
embeddings_all = [item["embedding"] for item in data]
metadatas_all = [{
    "info": item["sentence"]
} for item in data]


num_batches = math.ceil(total_len / BATCH_SIZE)
for i in range(num_batches):
    start = i * BATCH_SIZE
    end   = min(start + BATCH_SIZE, total_len)

    batch_ids        = ids_all[start:end]
    batch_embeddings = embeddings_all[start:end]
    batch_metadatas  = metadatas_all[start:end]

    collection.upsert(
        ids=batch_ids,
        embeddings=batch_embeddings,
        metadatas=batch_metadatas
    )
    print(f"[{i+1}/{num_batches}] {len(batch_ids):,}개 업서트 완료")