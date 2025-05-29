#사용자 정보 입력 코드
# app/routers/user_input.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import date

router = APIRouter(prefix="/user", tags=["User"])


class HealthSurvey(BaseModel):
    name: Optional[str]
    gender: Optional[Literal["남성", "여성"]]
    birth_date: Optional[date]
    family_history: Optional[List[Literal["고혈압", "당뇨병", "심장병", "암", "기타"]]] = []
    past_medical_history: Optional[List[Literal["간염", "천식", "고지혈증", "우울증", "기타"]]] = []
    allergies: Optional[List[Literal["계란", "우유", "갑각류", "약물", "기타"]]] = []
    current_medications: Optional[str] = None
    smoking_status: Optional[Literal["비흡연", "과거 흡연", "현재 흡연"]]
    drinking_status: Optional[Literal["전혀 안 함", "가끔", "자주"]]
    average_sleep_hours: Optional[int] = Field(ge=0, le=24)


@router.post("/survey")
def submit_survey(data: HealthSurvey):
    """
    사용자가 작성한 건강 문진표(HealthSurvey)를 수신합니다.
    이후 추천 로직에서 data.* 로 접근 가능해집니다.
    """
    # 예시: 입력값 로그
    print("Received survey:", data.json(ensure_ascii=False))
    # TODO: 세션에 저장하거나 DB에 기록
    return {"status": "ok", "received": data.dict()}

