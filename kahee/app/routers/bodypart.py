from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sql_utils import sql_utils

from rag.retriever import retrieve
from rag.generator import generate_answer
# from app.rag_stub import get_most_similar_function  # 기존 유사도 함수 사용...해야 하는데 파일 충돌 ---> 수정 필요

router = APIRouter(prefix="/bodypart", tags=["Body‑Part Recommendation"])

# Pydantic Schemas
class BodyPartRequest(BaseModel):
    body_part: str  
    function: str  

class SupplementOut(BaseModel):
    product_name: str
    product_id: str
    primary_function: str | None = None
    caution: str | None = None

# 1️. 기능 목록 조회 (파일 기반)
@router.get("/options")
def get_options():
    try:
        options = sql_utils.load_body_function_options()
        return {"options": options}
    except Exception as e:
        print(f"SERVER ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 2️. 사용자 입력 → 유사 기능 매칭 (파일 기반)
@router.post("/bodyfunction/match")
def match_function(data: BodyPartRequest):
    try:
        func_list = sql_utils.fetch_functions_by_body(data.body_part)
        if not func_list:
            raise HTTPException(status_code=404, detail="해당 부위에 등록된 기능이 없습니다.")
        best_match = get_most_similar_function(data.function, func_list) #--> 기존 코드에서 가져와야 함. 우선 보류
        if not best_match:
            raise HTTPException(status_code=404, detail="유사한 기능을 찾을 수 없습니다.")
        return {"matched_function": best_match}
    except Exception as e:
        print(f"SERVER ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 3️. 기능별 추천 (RAG)
@router.post("/recommend")
def recommend(req: BodyPartRequest):
    try:
        # 1) 벡터 검색
        context_list = retrieve(req.function, top_k=5)
        if not context_list:
            return {"message": "관련된 추천 정보를 찾지 못했습니다."}

        # 2) LLM 호출
        answer = generate_answer(context_list, req.function)
        return {
            "recommendation": answer,
            "context": context_list
        }
    except Exception as e:
        print(f"SERVER ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
