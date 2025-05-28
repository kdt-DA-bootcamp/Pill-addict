## 기존 chroma_loader.py를 대신해 벡터데이터 읽어오는 코드
## faiss_index 읽어오도록 수정

#라이브러리 및 설정 가져오기
# app/rag/vector_searcher.py
import faiss, pickle, numpy as np
from pathlib import Path
from typing import Any

# ── 경로 설정
BASE = Path(__file__).resolve().parent.parent
IDX_DIR = BASE / "data" / "faiss_index_supplement"


# ── 인덱스 & 메타 한 번만 메모리에 로드
_index = faiss.read_index(str(IDX_DIR / "index.faiss"))
with open(IDX_DIR / "index.pkl", "rb") as f:
    _metas: list[dict[str,Any]] = pickle.load(f)
_vecs = None  

# ── 검색 함수
def search_vector(query_embedding: list[float], top_k: int = 5):
    # 1) numpy 배열로 변환 & (1, dim) 모양으로 reshape
    q = np.array(query_embedding, dtype=np.float32).reshape(1, -1)

    # 2) FAISS 인덱스에 검색 요청 (L2 거리 기준)
    distances, indices = _index.search(q, top_k)

    results, scores = [], []
    # distances: shape (1, top_k), indices: (1, top_k)
    for idx, dist in zip(indices[0], distances[0]):
        # 메타데이터에서 같은 순서의 dict 가져오기
        meta = _metas[idx]

        results.append({
            # • text: RAG에서 컨텍스트로 사용할 본문
            "text": meta.get("text", ""),
            # • metadata: Document.metadata 에 그대로 들어갈 dict
            "metadata": meta,
            # • score: FAISS가 계산한 거리값 (작을수록 비슷)
            "score": float(dist),
        })
        scores.append(float(dist))

    return results, scores
