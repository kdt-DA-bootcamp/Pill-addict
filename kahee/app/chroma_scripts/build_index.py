import sys
import os
# config 경로 문제 지속으로 임시로 상대경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

import sys, json, uuid, math
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.config.settings import settings

BATCH_SIZE = 5000

if __name__ == "__main__":

    # 1️. ChromaDB 연결
    ## 디버깅용1
    print("CHROMA_DIR:", settings.CHROMA_DIR)
    print("COLLECTION_NAME:", settings.COLLECTION_NAME)
    client = chromadb.Client(ChromaSettings(persist_directory=settings.CHROMA_DIR))
    collection = client.get_or_create_collection(settings.COLLECTION_NAME)
    # 디버깅용2
    print(f"현재 DB 등록된 총 문서 수: {collection.count()}")

    # 2️. 입력 파일 로드
    SRC_JSON = sys.argv[1]

    with open(SRC_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 3️. 데이터 구성
    total_len = len(data)
    ids = [str(i + 1) for i in range(total_len)]
    embeddings_all = [item["embedding"] for item in data]
    metadatas_all = [item["metadata"] for item in data]

    # 4️. 배치 업로드
    num_batches = math.ceil(total_len / BATCH_SIZE)
    for i in range(num_batches):
        start = i * BATCH_SIZE
        end = min(start + BATCH_SIZE, total_len)

        batch_ids = ids[start:end]
        batch_embeddings = embeddings_all[start:end]
        batch_metadatas = metadatas_all[start:end]

        collection.upsert(
            ids=batch_ids,
            embeddings=batch_embeddings,
            metadatas=batch_metadatas
        )
        print(f"[{i+1}/{num_batches}] {len(batch_ids):,}개 업서트 완료 ")

    # 5️. 최종 확인(단순확인용)
    print(f"\n최종 등록된 벡터 수: {collection.count()}개")
    
    #6. 디스크에 저장
    client.persist()
    print("디스크에 저장 완료 (client.persist() 호출)")