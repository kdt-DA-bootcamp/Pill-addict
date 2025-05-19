# (새) app/rag/retriever.py
"""
변경 사항
1. 임베딩 모델:

기존: OpenAIEmbeddings() → 새: OpenAIEmbeddings(model="text-embedding-3-small")

모델명을 "text-embedding-3-small"으로 명시

2. 캐싱 로직(_embed_query_cached) 추가

_embed_cache dict에 {query: embedding_vec} 형태로 저장

동일한 query가 다시 들어오면, API 호출 없이 _embed_cache[query]를 반환

3. 쓰레드 안전 처리를 위해 threading.Lock() 사용 (간단 예시)

FastAPI 멀티스레드 시 환경에서 캐시 동시 접근 문제 방지"""

import threading
from langchain.schema import Document
from app.rag.vector_searcher import search_vector
from langchain_openai import OpenAIEmbeddings

# 전역 임베딩 모델 (model="text-embedding-3-small")
#
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

# 간단 캐시: {query_str: embedding_vector}
_embed_cache = {}
_cache_lock = threading.Lock()

def retrieve(query: str, k: int = 5) -> list[Document]:
    # 1) query → 임베딩 (캐싱)
    query_vec = _embed_query_cached(query)

    # 2) vectorized_data.json + np array
    results, sims = search_vector(query_vec, top_k=k)

    # 3) 상위 K개 -> Document
    docs = []
    for item in results:
        content = item.get("text", "")
        meta = item.get("metadata", {})
        docs.append(Document(page_content=content, metadata=meta))
    return docs

def _embed_query_cached(query: str) -> list[float]:
    with _cache_lock:
        if query in _embed_cache:
            return _embed_cache[query]  # 캐시 HIT
        # 캐시 미스 → 실제 임베딩
        vec = embedding_model.embed_query(query)
        _embed_cache[query] = vec
        return vec
