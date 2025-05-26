## 벡터 유사도 검색해서 답변 구성

# 라이브러리 및 설정 가져오기
from langchain.schema import Document
from app.rag.vector_searcher import search_vector


# 설정
def retrieve(query: str, k: int = 5) -> list[Document]:
    from langchain_openai import OpenAIEmbeddings
    embedding_model = OpenAIEmbeddings()
    query_vec = embedding_model.embed_query(query)
    results, _ = search_vector(query_vec, top_k=k)
    return [Document(page_content=itm["text"], metadata=itm["metadata"]) for itm in results]

