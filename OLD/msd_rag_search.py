# msd_rag_search.py
"""파일 목적/역할
Chroma DB 로드: 이전 단계에서 생성된 msd_chroma_db 폴더(벡터 인덱스)를 불러와서 사용할 준비.

검색(similarity_search): 사용자가 쿼리(예: 성분명 “밀크시슬”)를 넣으면, 상위 K개의 유사한 텍스트 snippet을 반환.

결과 구조: snippet은 문서 본문 일부(최대 200자) + metadata(예: section, source)로 구성.

테스트: if __name__=="__main__": 블록에서 간단히 “밀크시슬”로 테스트해볼 수 있음.

동작 과정
초기화: MsdRagSearch(persist_dir="msd_chroma_db", openai_api_key=...)

검색: .similarity_search(ingredient, k=k) → 점수 순 상위 k개.

추가 처리: 실제 제품화 시에는 snippet에 “주의”, “효과”, “복용” 등 특정 키워드가 있는지 확인하거나, 바로 snippet만 리턴할 수도 있음."""

import os
from typing import List, Dict
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

class MsdRagSearch:
    def __init__(self, persist_dir="msd_chroma_db", openai_api_key=None):
        embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self.db = Chroma(
            persist_directory=persist_dir,
            embedding_function=embeddings
        )

    def search_msd(self, ingredient: str, k=2) -> List[Dict]:
        docs = self.db.similarity_search(ingredient, k=k)
        results = []
        for d in docs:
            snippet = d.page_content[:200]
            results.append({
                "content": snippet,
                "metadata": d.metadata
            })
        return results

if __name__=="__main__":
    openai_api_key = os.getenv("OPENAI_API_KEY","")
    if not openai_api_key:
        print("Need OPENAI_API_KEY.")
        exit()

    searcher = MsdRagSearch(persist_dir="msd_chroma_db", openai_api_key=openai_api_key)
    query = "밀크시슬"
    hits = searcher.search_msd(query, k=2)
    print(f"=== Searching for '{query}' ===")
    for i, h in enumerate(hits,1):
        print(f"[Result {i}] content: {h['content']}")
        print("           metadata:", h["metadata"])
        print("---")
