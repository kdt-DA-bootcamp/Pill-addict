## vectorized_data.json  ➜  LangChain Chroma VectorStore 저장 스크립트 
 
# 라이브러리 모음
import json, sys, math, uuid
from pathlib import Path
from tqdm import tqdm
from langchain.schema import Document

# 설정 가져오기
from app.config.chromadb_loader import vectorstore
from app.config.settings import settings

BATCH = 1_000  # 메모리 절약용

if len(sys.argv) < 2:
    sys.exit("JSON 경로 설정 필요요")

# 파일 경로 설정
src = Path(sys.argv[1])
if not src.exists():
    sys.exit(f"파일 없음: {src}")

data = json.loads(src.read_text(encoding="utf-8"))
total = len(data)
print(f"{total:,} 개 로드, {settings.CHROMA_DIR}")

docs: list[Document] = []
for i, item in enumerate(tqdm(data, desc="build")):
    meta = item["metadata"]

    docs.append(
        Document(
            page_content=meta.get("PRIMARY_FNCLTY", ""),
            metadata=meta | {"_id": item["id"]},
            id=item["id"],
            embedding=item["embedding"],  # 이미 계산된 벡터데이터 활용
        )
    )

    if len(docs) >= BATCH:
        vectorstore.add_documents(docs)
        docs.clear()

# 마지막 잔량
if docs:
    vectorstore.add_documents(docs)

vectorstore.persist()
print("업서트 완료. 총 카운트:", vectorstore._collection.count())



