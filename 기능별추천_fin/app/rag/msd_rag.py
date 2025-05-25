# 수빈님 코드 중 필요한 부분만 가져왔습니다.

from pathlib import Path
from typing import List
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

class MsdRagSearch:
    def __init__(self, openai_api_key: str, index_dir: str = "app/data/faiss_index_msd"):
        embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self.db = FAISS.load_local(
            folder_path=index_dir,
            embeddings=embeddings,
            allow_dangerous_deserialization=True
        )

    def search_side_effects(self, ingredient: str, k: int = 1) -> List[str]:
        docs = self.db.similarity_search(ingredient, k=k)
        return [d.page_content[:300].strip() + "…" for d in docs] if docs else ["추가 정보 없음"]
