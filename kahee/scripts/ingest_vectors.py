## CHROMA DB에 벡터 데이터 업로드 및 활용하기 쉽도록 설정
# 크로마 버전 오류 지속으로 그냥 langchain 활용하는 것으로 변경 -> 이후 최적화 필요?
# 최초 한 번만 실행

"""
실행 코드:
   python -m scripts.ingest_vectors --drop
   python -m scripts/ingest_vectors
"""

# 라이브러리 및 설정 가져오기
from __future__ import annotations
import argparse
from typing import List
from tqdm import tqdm
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from app.config.chromadb_loader import vectorstore
from app.config.metadata_loader import vector_rows

# 1. CLI 옵션
parser = argparse.ArgumentParser(description="Re-ingest with OpenAIEmbeddings")
parser.add_argument(
    "--drop", action="store_true",
    help="Delete entire collection (including metadata) before ingest"
)
parser.add_argument(
    "--batch", type=int, default=128,
    help="Batch size for add_documents()"
)
args = parser.parse_args()


# 2. 컬렉션 초기화 후 재생성(벡터 차원 안맞아서 수정)
client   = vectorstore._client
col_name = vectorstore._collection.name
col      = vectorstore._collection

if args.drop:
    print(f"Deleting collection '{col_name}' definition and data…")  #디버깅용 출력문
    client.delete_collection(col_name)
    # 컬렉션 메타·차원까지 통째로 삭제 후후 재생성
    new_col = client.get_or_create_collection(col_name)
    # wrapper 내부 컬렉션 객체도 교체
    vectorstore._collection = new_col
    col = new_col
    print("collection recreated with new dimension")   #디버깅용 출력문

print("Existing vectors: 0 (collection freshly recreated)")   #디버깅용 출력문


# 3. 데이터 로드 (메타로부터 문장+메타 가져오기)
#    라이브러리 모음에 올려뒀음


# 4. OpenAIEmbeddings 준비
embeddings = OpenAIEmbeddings()


# 5. Document 리스트로 변환 (제대로 실행되지 않을 경우 출력 데이터 0개 찍힘)
docs: List[Document] = []
for row in vector_rows:
    meta = row["metadata"]
    meta["PRDLST_REPORT_NO"] = str(meta["PRDLST_REPORT_NO"])
    # 검색용 텍스트: 메타 필드에서 주요 정보만 추출·결합
    text = " ".join([
        meta.get("PRIMARY_FNCLTY", ""),
        meta.get("RAWMTRL_NM", ""),
        meta.get("INDIV_RAWMTRL_NM", ""),
        meta.get("ETC_RAWMTRL_NM", ""),
    ]).strip()
    docs.append(Document(page_content=text, metadata=meta))

print(f"Prepared Documents: {len(docs)}")  #디버깅용 출력물: 40880 정상


# 6. 삽입 (배치 처리, 기존 embedding값과 차원 다를 시 오류 발생 가능성 있어 OpenAIEmbeddings 로 임베딩 재계산)
batch = args.batch
bar = tqdm(total=len(docs), desc="Ingesting with OpenAIEmbeddings", unit="doc")

for i in range(0, len(docs), batch):
    slice_docs = docs[i : i + batch]
    vectorstore.add_documents(slice_docs, embeddings=embeddings)
    bar.update(len(slice_docs))

bar.close()
print("Done. Total vectors now:", col.count())  #디버깅용 출력물: 40880 정상
