from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import time
import pandas as pd

# 너의 로컬 분석 함수들 import
from pipeline import (
    parse_health_exam, load_reference, find_abnormal,
    get_ingredients_from_abnormal_tuple, load_ingredient_info,
    load_msd_manual, recommend_products, build_structured_data
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 시에는 "*"로 OK, 운영 시 특정 도메인만
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze_exam")
async def analyze_exam(
    file: UploadFile = File(...),
    user_name: str = Form(...),
    gender: str = Form(...),
    file_type: str = Form(...)
):
    try:
        contents = await file.read()

        # 1. OCR + 검사값 추출
        exam_dict, ocr_text = parse_health_exam(contents, file_type)

        # 2. 기준표 기반 이상치 탐지
        reference = load_reference()
        abnormal = find_abnormal(exam_dict, reference, gender)

        # 3. 성분 추천
        ingredients = get_ingredients_from_abnormal_tuple(abnormal)

        # 4. 제품 추천
        try:
            supplements_df = pd.read_json("data/supplements.json")
        except FileNotFoundError:
            supplements_df = pd.DataFrame()
        products = recommend_products(ingredients, supplements_df.to_dict("records"))

        # 5. GPT 응답 구성
        ing_info_df = load_ingredient_info()
        msd_manual = load_msd_manual()
        output = build_structured_data(
            exam_dict, abnormal, ingredients, products,
            ing_info_df, msd_manual, user_name
        )

        # 6. JSON 응답 반환
        return {
            "gpt_response": output["gpt_response"],
            "structured_data": output["structured_data"],
            "ocr_text": ocr_text
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
