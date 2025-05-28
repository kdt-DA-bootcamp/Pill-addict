# 사용자 정보 입력에 따른 추천 로직

from fastapi import APIRouter
from .user_input import UserHealthInfo

router = APIRouter()

@router.post("/recommend")
async def recommend(info: UserHealthInfo):
    filters = []

    if info.is_pregnant:
        filters.append("NOT_FOR_PREGNANT")
    if info.is_baby:
        filters.append("NOT_FOR_CHILD")
    if info.smokes or info.drinks:
        filters.append("AVOID_LIVER_TOXIC")
    if info.allergies:
        for allergen in info.allergies:
            filters.append(f"NO_{allergen.upper()}")

    # 임시 추천 결과
    return {
        "filters_applied": filters,
        "recommended": ["비타민 D", "오메가3"]
    }
