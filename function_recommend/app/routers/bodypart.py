## 영양제 추천 로직

# 라이브러리 모음
import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json, re
from typing import List, Optional

# 설정 가져오기
from app.rag.retriever import retrieve
from app.rag.generator import generate_answer
from app.sql_utils.matcher import get_most_similar_function
from app.sql_utils.sql_utils import load_body_function_options, fetch_functions_by_body
from app.routers.user_input import HealthSurvey
from langchain.schema import Document
from app.rag.msd_rag import MsdRagSearch
from langchain.schema import Document
from app.config.settings import settings
from app.rag.vector_searcher import _metas  

# 디버깅용 출력문
print("bodypart 라우터 시작됨")
router = APIRouter(prefix="/bodypart", tags=["Body-Part"])


# 기본 스키마 설정
class BodyPartRequest(BaseModel):
    body_part: str
    function:  str
    survey: Optional[HealthSurvey] = None
    

# class SupplementOut(BaseModel):
#     product_name:      str
#     product_id:        str
#     primary_function:  str | None = None
#     caution:           str | None = None


# 1. 기능 목록 조회
@router.get("/options")
def get_options():
    rows = load_body_function_options()
    opts: dict[str, list[str]] = {}
    for r in rows:
        funcs = [f.strip() for f in r["function"].split(",")]
        opts.setdefault(r["body"], []).extend(funcs)
    return {"options": opts}


# 2. 유사 기능 매칭
@router.post("/bodyfunction/match")
def match_function(data: BodyPartRequest):
    funcs = fetch_functions_by_body(data.body_part)
    if not funcs:
        raise HTTPException(404, "해당 부위에 기능이 없습니다.")
    best = get_most_similar_function(data.function, funcs)
    if not best:
        raise HTTPException(404, "유사 기능을 찾지 못했습니다.")
    return {"matched_function": best}

RATE_LIMIT_DELAY = 2.0 
# 3. 기능별 추천
@router.post("/recommend")
def recommend(data: BodyPartRequest):
    print("Enter recommend():", data.dict())  # 디버깅용 출력문
    with open("app/data/function_ingredient.json", encoding="utf-8") as f:
        fn_ing_map = json.load(f)

    # 3-1. 기능 기반 성분 매핑
    raw_ing = next(
        (itm["ingredient"] for itm in fn_ing_map if itm["function"] == data.function),
        ""
    )
    print("Mapped ingredients:", raw_ing)  # 디버깅용 출력문

    # 정규화 함수(이후 영양제 검색 성능 향상 위해 기능별로 매핑된 성분명 전처리)
    norm = lambda t: re.sub(r"[^가-힣a-z0-9]+", "", t.lower())

    ingredients = [
        norm(ing)
        for part in raw_ing.split(",")
        for ing in part.split("/")
        if ing.strip()
    ]
    print("Parsed ingredients list:", ingredients)  # 디버깅용 출력문

    if not ingredients:
        raise HTTPException(404, f"'{data.function}'에 매핑된 성분 정보가 없습니다.")

    # 3-2. 매핑 필터링
    matched = []
    for m in _metas:
        # 기존 RAWMTRL_NM 등 대신, 미리 묶어둔 'ingredient' 필드만 사용
        ingr_field: str = m.get("ingredient", "").lower()
        if any(ing in norm(ingr_field) for ing in ingredients):
            matched.append(m)
    print("After mapping filter, matched:", len(matched))

    # 3-3. 사용자가 입력한 알러지 정보로 추가 필터링
    if data.survey and data.survey.allergies:
        user_allergies = {a.lower() for a in data.survey.allergies}
        filtered = []
        for m in matched:
            # 메타데이터에 알러지 주의 문구가 들어있다면(예: IFTKN_ATNT_MATR_CN)
            warn: str = m.get("caution", "").lower()
            if not any(allg in warn for allg in user_allergies):
                filtered.append(m)
        matched = filtered
        print("After allergy filter, matched:", len(matched))

    # 3-4. 매핑된 성분이나 추천 성분에 해당하는 영양제 없을 경우 RAG 활용하여 추천하는 로직 추가
    if not matched:
        print("매핑된 제품 없음 → RAG 수행")
        docs = retrieve(data.function, k=3)
    else:
        docs = [
            Document(page_content=m["text"], metadata=m)
            for m in matched
        ]

    # 3-6. MSD 부작용 정보 검색
    rag = MsdRagSearch(openai_api_key=settings.OPENAI_API_KEY)
    msd_docs = []
    for ing in ingredients[:2]:
        time.sleep(RATE_LIMIT_DELAY)
        snippet = rag.search_side_effects(ing, k=1)[0][:200] + "…"
        msd_docs.append(
            Document(page_content=f"[주의사항] {ing}: {snippet}", metadata={})
        )

    # MSD 문서 추가된 전체 문서 context
    all_docs = docs + msd_docs

    # 3-7. generate_answer 가 기대하는 형식으로 변환 및 RAG 답변 생성
    time.sleep(RATE_LIMIT_DELAY)
    answer = generate_answer(all_docs, data.function)
    context_list = [d.metadata.get("PRIMARY_FNCLTY", "") for d in docs]

    return {
    "recommendation": answer,
    "context": context_list,
    "msd_info": msd_docs,
    "matched_supplements": [
        {
            "product_id":  d.metadata["id"],
            "product_name": d.metadata.get("name"),
            "primary_function": d.metadata.get("function"),
            "caution": d.metadata.get("text"),
        }
        for d in docs
    ],
}