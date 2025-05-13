
#5월 12일 수정 (캐싱 + Moderation 반영)
"""
recommend_api.py
FastAPI 서버
 - Moderation API로 유저 입력 사전 검열
 - (exam_info, body_part, symptom) 기준 캐싱
 - process_recommendation + generate_natural_answer
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import os
import pathlib

from myrag.recommend_pipeline import (
    process_recommendation,
    generate_natural_answer,
)
from myrag.moderation import moderate_text

# .env 로드
from dotenv import load_dotenv
BASE_DIR = pathlib.Path(__file__).resolve().parent
ENV_PATH = BASE_DIR.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

class RecommendRequest(BaseModel):
    exam_info: Optional[str] = None
    body_part: Optional[str] = None
    symptom:   Optional[str] = None

app = FastAPI()

# ★ 간단 캐시 (서버 프로세스 메모리)
RECOMMEND_CACHE = {}

@app.post("/recommend")
def recommend(req: RecommendRequest):
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        return {"error": "No OPENAI_API_KEY"}

    # --- Moderation 검사 ---
    user_text = req.symptom or ""
    if not moderate_text(user_text):
        return {"error": "입력하신 내용은 부적절하거나 허용되지 않습니다."}

    # --- 캐싱 키 ---
    cache_key = (req.exam_info, req.body_part, req.symptom)
    if cache_key in RECOMMEND_CACHE:
        return RECOMMEND_CACHE[cache_key]

    # --- RAG + 기능 매핑 ---
    data = process_recommendation(
        exam_info=req.exam_info,
        body_part=req.body_part,
        symptom=req.symptom,
        openai_api_key=api_key,
    )

    # --- LLM 생성 ---
    answer_md = generate_natural_answer(data, api_key, user_text)

    # --- 최종 결과 ---
    result = {"answer": answer_md, **data}
    RECOMMEND_CACHE[cache_key] = result
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("myrag.recommend_api:app", host="127.0.0.1", port=8000, reload=True)
