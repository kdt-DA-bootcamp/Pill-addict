## 쿼리 기반 필터링된 메타데이터 호출

# 라이브러리 및 설정 가져오기기
from langchain_community.vectorstores import Chroma
from app.config.chromadb_loader import vectorstore


# 설정
def retrieve(query: str, k: int = 5):
    return vectorstore.similarity_search(query, k)

