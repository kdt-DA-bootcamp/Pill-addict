from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app import models



def fetch_ingredient_names_by_function(db: Session, function_name: str) -> list[str]:
    """
    기능 이름(function_name)에 해당하는 주요 성분(ingredient)을 모두 가져옴.
    단일 행에 여러 성분이 콤마(,)로 묶여 있으면 분리해서 리스트로 반환.

    Parameters
    ----------
    db : Session
        SQLAlchemy 세션 객체
    function_name : str
        예: "인지기능/기억력", "피로"

    Returns
    -------
    list[str]
        ["홍삼", "은행잎추출물", "포스파티딜세린", ...]
    """
    rows = (
        db.query(models.FunctionIngredient)
        .filter(models.FunctionIngredient.function == function_name)
        .all()
    )

    ingredient_names = []
    for row in rows:
        ingredients_split = [i.strip() for i in row.ingredient.split(",") if i.strip()]
        ingredient_names.extend(ingredients_split)

    return ingredient_names


def search_supplements_by_raw(db: Session, ingredient_names: list[str]):
    """
    주어진 원재료 이름(ingredient_names) 리스트를 포함하는 건강기능식품(Supplement) 검색
    - 주원료, 기타원료, 개별원료, 캡슐원료 컬럼 모두 검색
    """
    if not ingredient_names:
        return []

    filters = []
    for name in ingredient_names:
        filters.append(models.Supplement.RAWMTRL_NM.ilike(f"%{name}%"))
        filters.append(models.Supplement.ETC_RAWMTRL_NM.ilike(f"%{name}%"))
        filters.append(models.Supplement.INDIV_RAWMTRL_NM.ilike(f"%{name}%"))
        filters.append(models.Supplement.CAP_RAWMTRL_NM.ilike(f"%{name}%"))

    query = db.query(models.Supplement).filter(or_(*filters))

    results = query.all()
    return results