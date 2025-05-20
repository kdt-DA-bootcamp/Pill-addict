
# pill-addict/kahee/app/rag/vector_searcher.py
## 기존 chroma_loader.py를 대신해 벡터데이터 읽어오는 코드

#라이브러리 및 설정 가져오기
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path
from kahee.app.config.settings import BASE_DIR   # ✅ BASE_DIR 불러오기

#미리 만들어둔 벡터파일 불러오기

VEC_PATH = BASE_DIR / "data" / "sample_vectorized_data.json"   # 'app' 빼고!
with VEC_PATH.open(encoding="utf-8") as f:
    data = json.load(f)
print("VEC_PATH:", VEC_PATH) 

vectors = np.array([item["embedding"] for item in data], dtype=np.float32)

#함수 선언
def search_vector(query_embedding: list[float], top_k: int = 5):
    query = np.array(query_embedding, dtype=np.float32).reshape(1, -1)
    sims = cosine_similarity(query, vectors)[0]
    top_indices = sims.argsort()[-top_k:][::-1]
    return [data[i] for i in top_indices], [sims[i] for i in top_indices]

if __name__ == "__main__":
    print("VEC_PATH:", VEC_PATH)
