# app/api/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json

from app.config.settings import settings
from app.routers.bodypart import router as bodypart_router

# === 수빈님 라우터 ===
from soobin.myrag.recommend_api import router as soobin_router

# === Faiss ===
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings

app = FastAPI(title=settings.API_TITLE)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.ALLOWED_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

faiss_db = None

@app.on_event("startup")
def load_faiss():
    global faiss_db
    embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
    # soobin/myrag/faiss_index_msd/ <-- 수빈님 faiss_build_index.py 결과
    faiss_db = FAISS.load_local(
        "soobin/myrag/faiss_index_msd",
        embeddings=embeddings,
        allow_dangerous_deserialization=True
    )
    print("FAISS index loaded successfully")

# === 가희님 라우터 등록 ===
app.include_router(bodypart_router, prefix="/bodypart", tags=["BodyPart"])

# === 수빈님 라우터 등록 ===
app.include_router(soobin_router, prefix="/soobin", tags=["Soobin"])

# === 가희님 RAG 예시 ===
class SearchReq(BaseModel):
    query: str
    top_k: int = 5

@app.post("/rag_search")
def rag_search(req: SearchReq):
    from app.rag import retriever, generator
    docs = retriever.retrieve(req.query, req.top_k)
    answer = generator.generate_answer(docs, req.query)
    return {"context":[d.page_content for d in docs], "answer":answer}

# === 예시 product/ID (가희님) ===
with open("app/data/vectorized_data.json", encoding="utf-8") as f:
    vec_items = json.load(f)

product_index = {
    str(it["metadata"]["PRDLST_REPORT_NO"]): it["metadata"]
    for it in vec_items
}

@app.get("/product/{product_id}")
def get_product(product_id: str):
    if product_id not in product_index:
        raise HTTPException(404, "해당 제품 없음")
    return {"product":product_index[product_id]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.api.main:app", host="0.0.0.0", port=settings.APP_PORT, reload=True)
