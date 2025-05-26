## 영양제 추천 로직

# 라이브러리 모음
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json, re

# 설정 가져오기
from app.rag.retriever import retrieve
from app.rag.generator import generate_answer
from app.sql_utils.matcher import get_most_similar_function
from app.sql_utils.sql_utils import load_body_function_options, fetch_functions_by_body
from langchain.schema import Document
from app.rag.msd_rag import MsdRagSearch
from langchain.schema import Document
from app.config.settings import settings

# 디버깅용 출력문
print("bodypart 라우터 시작됨")
router = APIRouter(prefix="/bodypart", tags=["Body-Part"])


# 기본 스키마 설정
class BodyPartRequest(BaseModel):
    body_part: str
    function:  str

class SupplementOut(BaseModel):
    product_name:      str
    product_id:        str
    primary_function:  str | None = None
    caution:           str | None = None


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
    with open("app/data/vectorized_data.json", encoding="utf-8") as f:
        items = json.load(f)

    matched = []
    for item in items:
        meta = item["metadata"]
        combined = " ".join(
            str(meta.get(k, "")) for k in ("RAWMTRL_NM", "INDIV_RAWMTRL_NM", "ETC_RAWMTRL_NM")
        )
        if any(ing in norm(combined) for ing in ingredients):
            matched.append(item)

    print("After mapping filter, matched:", len(matched))  # 디버깅용 출력문

    # 3-3. 매핑된 성분이나 추천 성분에 해당하는 영양제 없을 경우 RAG 활용하여 추천하는 로직 추가
    if not matched:
        print("필터링된 제품이 없어 전체 데이터에서 RAG 수행")
        docs = retrieve(data.function, k=5)
    else:
        from langchain.schema import Document
        docs = [
            Document(page_content=item["text"], metadata=item["metadata"])
            for item in matched
        ]


    # 3-5. 추출된 ID 기반으로 최종 벡터DB 검색
    from langchain.schema import Document
    docs = retrieve(data.function, k=5)

    # 3-6. MSD 부작용 정보 검색
    rag = MsdRagSearch(openai_api_key=settings.OPENAI_API_KEY)
    msd_docs = []
    for ing in ingredients:
        for caution in rag.search_side_effects(ing, k=1):
            msd_docs.append(Document(page_content=f"[주의사항] {ing}: {caution}", metadata={}))

    # MSD 문서 추가된 전체 문서 context
    all_docs = docs + msd_docs

    # 3-7. generate_answer 가 기대하는 형식으로 변환 및 RAG 답변 생성
    answer = generate_answer(all_docs, data.function)
    context_list = [d.metadata.get("PRIMARY_FNCLTY", "") for d in docs]

    return {
    "recommendation": answer,
    "context": context_list,
    "msd_info": msd_docs,
    "matched_supplements": [
        {
            "product_id":  d.metadata["PRDLST_REPORT_NO"],
            "product_name": d.metadata.get("PRDLST_NM"),
            "primary_function": d.metadata.get("PRIMARY_FNCLTY"),
            "caution": d.metadata.get("IFTKN_ATNT_MATR_CN"),
        }
        for d in docs
    ],
}