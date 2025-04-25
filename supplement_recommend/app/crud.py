from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app import models

# Ingredient 조회: 기능명 키워드로 주요 원료 추출

def fetch_ingredient_names_by_function(db: Session, function_name: str) -> list[str]:
    rows = db.query(models.FunctionIngredient).filter(
        models.FunctionIngredient.function == function_name
    ).all()

    ingredient_names = []
    for row in rows:
        ingredient_names.extend(
            [i.strip() for i in row.ingredient.split(",") if i.strip()]
        )
    return ingredient_names



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
