from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import SessionLocal
from app import crud
from app.database import get_db
from app.models import BodyFunction
from app.rag_stub import get_most_similar_function 
from typing import Optional


router = APIRouter(prefix="/bodypart", tags=["Body‑Part Recommendation"])

# Pydantic Schemas
class BodyPartRequest(BaseModel):
    body_part: str  
    function: str  

class SupplementOut(BaseModel):
    product_name: str
    product_id: str
    primary_function: Optional[str] = None
    caution: Optional[str] = None

# 핵심 로직
# 1. 기능선택
@router.get("/options")
def get_options(db: Session = Depends(get_db)):
    print("=== /bodypart/options 라우터 진입 ===")
    rows = db.query(BodyFunction.body, BodyFunction.function).all()
    print("rows =", rows)  
    try:
        rows = db.query(BodyFunction.body, BodyFunction.function).all()
        
        options = {}
        for body, func_str in rows:
            functions = [f.strip() for f in func_str.split(",") if f.strip()]
            options.setdefault(body, []).extend(functions)
        return {"options": options}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    
 # 2. 사용자 입력 -> 가장 유사한 기능으로 매칭   
@router.post("/bodyfunction/match")
def match_function(data: BodyPartRequest, db: Session = Depends(get_db)):
    try:
        # 1) function 리스트 조회
        functions = db.query(BodyFunction.function).filter(
            BodyFunction.body == data.body_part
        ).all()
        if not functions:
            raise HTTPException(status_code=404, detail="해당 부위에 등록된 기능이 없습니다.")
        # 2) 튜플 → 리스트 변환
        func_list = [f[0] for f in functions]
        # 3) 유사도 기반 best match 반환
        best_match = get_most_similar_function(data.function, func_list)
        # 예외/오류처리
        if not best_match:
            raise HTTPException(status_code=404, detail="유사한 기능을 찾을 수 없습니다.")
        return {"matched_function": best_match}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 3. 기능별 유효성분 참고하여 영양제 추천
@router.post("/recommend", response_model=list[SupplementOut])
def recommend(req: BodyPartRequest, db: Session = Depends(get_db)):
    # 1) 기능 → 성분 조회
    ingredient_names = crud.fetch_ingredient_names_by_function(db, req.function)
    if not ingredient_names:
        # 성분이 없으면 그냥 빈 리스트 반환
        return []

    # 2) 성분 포함 제품 조회
    supplements = crud.search_supplements_by_raw(db, ingredient_names)
    if not supplements:
        # 제품이 없으면 그냥 빈 리스트 반환
        return []

    # 3) 정상 추천 결과 반환
    return [
        SupplementOut(
            product_name=s.PRDLST_NM,
            product_id= str(s.PRDLST_REPORT_NO), 
            primary_function=s.PRIMARY_FNCLTY,
            caution=s.IFTKN_ATNT_MATR_CN,
        ) for s in supplements
    ]