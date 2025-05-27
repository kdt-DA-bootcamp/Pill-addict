# main_api.py
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
import pandas as pd

from pipeline import (
    parse_health_exam,
    load_reference,
    find_abnormal,
    get_ingredients_from_abnormal,
    recommend_products,
    load_ingredient_info,
    load_msd_manual,
    build_structured_data
)
from gpt_service import generate_response
import config

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# 미리 로드
ref_df      = load_reference()
supp_df     = pd.read_excel(config.SUPPLEMENT_DB_PATH)
ing_info_df = load_ingredient_info()
msd_info    = load_msd_manual()

@app.post("/analyze")
async def analyze(file: UploadFile = File(...), user_name: str = "이루시아"):
    content = await file.read()
    file_type = "pdf" if file.content_type == "application/pdf" else "image"

    exam, raw_text = parse_health_exam(content, file_type)
    abnormal      = find_abnormal(exam, ref_df)
    ingredients   = get_ingredients_from_abnormal(abnormal)
    products      = recommend_products(ingredients, supp_df)
    structured    = build_structured_data(
        exam, abnormal, ingredients, products, ing_info_df, msd_info
    )
    chat_md       = generate_response(user_name, structured)
    return JSONResponse({"markdown": chat_md})
