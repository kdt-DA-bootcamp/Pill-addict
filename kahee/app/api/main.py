##  핵심 로직 ##

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import HTTPException
import json
from fastapi.middleware.cors import CORSMiddleware
from langchain_openai import OpenAIEmbeddings

# 설정 가져오기
from app.config.metadata_loader import metadata_supplement
from app.config.settings import settings 
from app.config.chromadb_loader import vectorstore
from app.config.metadata_loader import supp_index
from app.config.chromadb_loader import collection
from app.rag import retriever, generator
from app.rag.retriever import retrieve
from app.rag.generator import generate_answer
from app.routers import bodypart
from chromadb.config import Settings as ChromaSettings

app = FastAPI(title=settings.API_TITLE)

# CORS 설정: 브라우저가 로컬 아닌 다른 곳에 요청을 보낼 때 차단 방지 위해 필요
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.ALLOWED_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(bodypart.router)


# 메타데이터(파일단위데이터) 로드 (파일 직접 가져오도록 설정)
with open(settings.abs_metadata_ingredient, encoding="utf-8") as f:
    metadata_ingredient = json.load(f)

with open(settings.abs_metadata_allergy, encoding="utf-8") as f:
    metadata_allergy = json.load(f)

with open(settings.abs_metadata_body, encoding="utf-8") as f:
    metadata_body = json.load(f)

with open(settings.abs_metadata_supplement, encoding="utf-8") as f:
    metadata_supplement = json.load(f)

with open(settings.abs_vectors_file, encoding="utf-8") as f:
    vector_meta = json.load(f)


class SearchReq(BaseModel):
    query: str
    top_k: int = 5

class SearchResItem(BaseModel):
    info: str
    distance: float

class RAGReq(SearchReq): pass


# 디버깅용 출력 메세지
print(f"벡터 DB에 등록된 총 데이터 수: {collection.count()}")
print(f"CHROMA_DIR={settings.CHROMA_DIR}")
print(f"COLLECTION_NAME={settings.COLLECTION_NAME}")


# 엔드포인트 설정(로직 전개)
@app.post("/search")
def search(req: SearchReq):
    hits = vectorstore.similarity_search(req.query, req.top_k)
    return [{"info": h.page_content, "distance": h.metadata.get("distance")} for h in hits]

@app.post("/rag_search")
def rag_search(req: RAGReq):
    ctx = retriever.retrieve(req.query, req.top_k)
    answer = generator.generate_answer(ctx, req.query)
    return {"context": [d.page_content for d in ctx], "answer": answer}
class MetaQueryReq(BaseModel):
    product_id: str

@app.post("/meta_lookup")
def meta_lookup(req: MetaQueryReq):
    meta = supp_index.get(str(req.product_id))
    if not meta:
        raise HTTPException(404, "해당 id의 영양제제가 없습니다.")
    return {"metadata": meta}