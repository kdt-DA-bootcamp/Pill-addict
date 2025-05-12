# soobin/myrag/recommend_api.py

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
import os
import pathlib

# ────────── (변경 1) 임포트 경로에서 'soobin.' 제거 ──────────
from myrag.recommend_pipeline import (
    process_recommendation,
    generate_natural_answer,
)

# ────────── .env 로드 ──────────
BASE_DIR = pathlib.Path(__file__).resolve().parent  # => .../soobin/myrag
ENV_PATH = BASE_DIR.parent / ".env"                 # => .../soobin/.env
load_dotenv(dotenv_path=ENV_PATH)

# ────────── 모델 ──────────
class RecommendRequest(BaseModel):
    exam_info: Optional[str] = None
    body_part: Optional[str] = None
    symptom:   Optional[str] = None

app = FastAPI()

@app.post("/recommend")
def recommend(req: RecommendRequest):
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        return {"error": "No OPENAI_API_KEY"}

    # 1) RAG 파이프라인
    data = process_recommendation(
        exam_info=req.exam_info,
        body_part=req.body_part,
        symptom=req.symptom,
        openai_api_key=api_key,
    )
    # 2) LLM 자연어 답변
    answer_md = generate_natural_answer(data, api_key)
    return {"answer": answer_md, **data}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("myrag.recommend_api:app", host="0.0.0.0", port=8000, reload=True)
    # uvicorn.run("myrag.recommend_api:app", host="