# app/routers/bodypart.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.sql_utils.sql_utils import fetch_functions_by_body
from app.sql_utils.matcher import get_most_similar_function
from app.rag import retriever, generator

router = APIRouter()

class BodyPartRequest(BaseModel):
    body_part: str
    function: str

@router.get("/options")
def get_options():
    # 단순 예시
    data = fetch_functions_by_body("신경계")  # or load_body_function_options()
    return {"options": data}

@router.post("/bodyfunction/match")
def match_function(req: BodyPartRequest):
    funcs = fetch_functions_by_body(req.body_part)
    if not funcs:
        raise HTTPException(404, "해당 부위 기능 없음")
    best = get_most_similar_function(req.function, funcs)
    if not best:
        raise HTTPException(404, "유사 기능 없음")
    return {"matched_function":best}

@router.post("/recommend")
def recommend(req: BodyPartRequest):
    query = f"{req.body_part} {req.function}"
    docs = retriever.retrieve(query, k=5)
    answer = generator.generate_answer(docs, query)
    return {"query":query, "answer":answer}
