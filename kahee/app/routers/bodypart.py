from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.sql_utils import sql_utils

from app.rag.retriever import retrieve
from app.rag.generator import generate_answer
from app.sql_utils.matcher import get_most_similar_function
from app.sql_utils.sql_utils import load_body_function_options
from app.sql_utils.sql_utils import fetch_functions_by_body
from app.config.metadata_loader import metadata_supplement
from app.config.chromadb_loader import collection

router = APIRouter(prefix="/bodypart", tags=["Body-Part"])

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
    rows = load_body_function_options()
    opts: dict[str, list[str]] = {}
    for r in rows:
        funcs = [f.strip() for f in r["function"].split(",")]
        opts.setdefault(r["body"], []).extend(funcs)
    return {"options": opts}


# 2️. 사용자 입력 → 유사 기능 매칭 (파일 기반)
@router.post("/bodyfunction/match")
def match_function(data: BodyPartRequest):
    funcs = fetch_functions_by_body(data.body_part)
    if not funcs:
        raise HTTPException(404, "해당 부위에 기능이 없습니다.")
    best = get_most_similar_function(data.function, funcs)
    if not best:
        raise HTTPException(404, "유사 기능을 찾지 못했습니다.")
    return {"matched_function": best}

# 3️. 기능별 추천 (RAG)
@router.post("/recommend")
def recommend(data: BodyPartRequest):
    # 1️. 기능 → 성분 매핑
    with open('data/function_to_ingredient.json', encoding='utf-8') as f:
        function_to_ingredient = json.load(f)
    ingredients = function_to_ingredient.get(data.function)
    if not ingredients:
        raise HTTPException(404, f"'{data.function}'에 매핑된 성분 정보가 없습니다.")


    # 2️. 성분 기반 영양제 필터링 (예: metadata_ingredient에서 성분 포함된 영양제 찾기)
    matched_supplements = []
    for item in metadata_supplement:
        combined_ingredients = ' '.join([
            item.get('RAWMTRL_NM', ''),
            item.get('INDIV_RAWMTRL_NM', ''),
            item.get('ETC_RAWMTRL_NM', '')
        ])
    if any(ingredient in combined_ingredients for ingredient in ingredients):
        matched_supplements.append(item)

    if not matched_supplements:
        raise HTTPException(404, "해당 성분을 포함한 영양제를 찾지 못했습니다.")

    # 3️. 필터링된 영양제 ID 추출 (벡터 DB에 있는 id와 매칭)
    target_ids = [supp["PRDLST_REPORT_NO"] for supp in matched_supplements]
    if not target_ids:
        raise HTTPException(404, "매칭된 영양제 ID가 없습니다.")
    
    # 4️. retrieve()를 개선: 벡터 DB에서 특정 IDs만 검색 (ChromaDB 필터링 옵션 사용)
    query_params = {
        "query_texts": [data.function],
        "n_results": 5,
        "where": {"PRDLST_REPORT_NO": {"$in": target_ids}},  # ID 필터링
        "include": ["metadatas"]
    }

    out = collection.query(**query_params)

    if not out['metadatas'] or not out['metadatas'][0]:
        raise HTTPException(404, "추천할 수 있는 영양제 정보가 없습니다.")

    
    context_list = [meta['PRIMARY_FNCLTY'] for meta in out['metadatas'][0]]

    answer = generate_answer(context_list, data.function)
    return {"recommendation": answer, "context": context_list}

