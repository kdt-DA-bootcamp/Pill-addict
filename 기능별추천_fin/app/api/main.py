##  핵심 로직 ##

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json

# 설정 가져오기
from app.config.settings import settings 
from app.rag import retriever, generator
from app.routers import bodypart

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

# 엔드포인트 설정(로직 전개: 기타 엔드포인트는 모두 삭제 or retriever로 넘김)
class SearchReq(BaseModel):
    query: str
    top_k: int = 5


class RAGReq(SearchReq): pass

@app.post("/rag_search")
def rag_search(req: RAGReq):
    ctx = retriever.retrieve(req.query, req.top_k)
    answer = generator.generate_answer(ctx, req.query)
    return {"context": [d.page_content for d in ctx], "answer": answer}

# 이후 최종적으로 추천된 영양제에 대한 기타 정보들 metadata에서 호출
with open("app/data/vectorized_data.json", encoding="utf-8") as f:
    vec_items = json.load(f)

product_index = {
    str(item["metadata"]["PRDLST_REPORT_NO"]): item["metadata"]
    for item in vec_items
}

@app.get("/product/{product_id}")
def get_product(product_id: str):
    product = product_index.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="해당 제품이 없습니다.")
    return {"product": product}
