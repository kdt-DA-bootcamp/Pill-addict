from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import json

# 설정 가져오기
from app.routers import bodypart
from app.config import settings
from rag.retriever import retrieve
from rag.generator import generate_answer


app = FastAPI(title=settings.API_TITLE)
app.include_router(bodypart.router)

client      = chromadb.Client(Settings(persist_directory=settings.CHROMA_DIR))
collection  = client.get_collection(settings.COLLECTION_NAME)
embed_model = SentenceTransformer(settings.EMBED_MODEL_ID)

# 메타데이터 로드 (파일 직접 가져오도록 설정)
with open(settings.METADATA_FILE, encoding="utf-8") as f:
    metadata1 = json.load(f)

class SearchReq(BaseModel):
    query: str
    top_k: int = 5

class SearchResItem(BaseModel):
    info: str
    distance: float

class RAGReq(BaseModel):
    query: str
    top_k: int = 5

@app.post("/search", response_model=list[SearchResItem])
def search(req: SearchReq):
    q_emb = embed_model.encode(req.query).tolist()
    out   = collection.query(
        query_embeddings=[q_emb],
        n_results=req.top_k,
        include=["distances", "metadatas"]
    )
    metadatas = out["metadatas"][0]
    dists     = out["distances"][0]
    return [
        SearchResItem(text=metadatas[i]["info"], distance=dists[i])
        for i in range(len(metadatas))
    ]

@app.post("/rag_search")
def rag_search(req: RAGReq):
    # 1. 벡터 검색
    context_list = retrieve(req.query, req.top_k)
    # 2️. LLM 호출
    answer = generate_answer(context_list, req.query)
    # 3️.  반환
    return {
        "query": req.query,
        "context": context_list,
        "answer": answer
    }
class MetaQueryReq(BaseModel):
    product_id: str

@app.post("/meta_lookup")
def meta_lookup(req: MetaQueryReq):
    result = [row for row in metadata1 if row["product_id"] == req.product_id]
    return result

