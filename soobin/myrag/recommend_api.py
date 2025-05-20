# # pill-addict/soobin/myrag/recommend_api.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import os
from soobin.myrag.moderation import moderate_text
from soobin.myrag.recommend_pipeline import process_recommendation

router = APIRouter()

class RecommendRequest(BaseModel):
    exam_info: Optional[str] = None
    body_part: Optional[str] = None
    symptom: str

@router.post("/recommend")
def recommend_api(req: RecommendRequest):
    if not moderate_text(req.symptom):
        return {"error":"부적절 표현 감지"}
    try:
        data = process_recommendation(
            exam_info=req.exam_info,
            body_part=req.body_part,
            symptom=req.symptom,
            openai_api_key=os.getenv("OPENAI_API_KEY","")
        )
        return {
            "recommendation":"(RAG결과 + LLM가능)",
            "pipeline_data": data
        }
    except Exception as e:
        import traceback
        print("추천API 내부 에러:", traceback.format_exc())
        return {"error": str(e)}
    
