# 📁 main.py — 유연한 건강검진 분석 시스템 (PDF/이미지 입력, 기준 비교, 비정상 추출)

import pdfplumber
import pytesseract
from PIL import Image
import cv2
import json
import os
import re
from dotenv import load_dotenv

# ✅ 환경 변수 로드
load_dotenv()

# 🔧 경로 설정
base_dir = os.path.dirname(__file__)
input_path = os.path.join(base_dir, os.getenv("INPUT_FILE", "이루시아검진결과.pdf"))
pattern_file = os.path.join(base_dir, os.getenv("PATTERN_FILE", "pattern_map.json"))
criteria_file = os.path.join(base_dir, os.getenv("CRITERIA_FILE", "criteria.json"))
gender = os.getenv("DEFAULT_GENDER", "여성")

# ✅ PDF/이미지에서 텍스트 추출

def extract_text(input_path):
    ext = os.path.splitext(input_path)[1].lower()
    text_all = ""
    if ext == ".pdf":
        with pdfplumber.open(input_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_all += page_text + "\n"
    elif ext in [".png", ".jpg", ".jpeg"]:
        img = cv2.imread(input_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        text_all = pytesseract.image_to_string(gray, lang='kor+eng')
    else:
        raise ValueError(f"Unsupported file type: {ext}")
    return text_all

# ✅ 정규표현식 기반 텍스트 파싱

def parse_with_pattern_map(text, pattern_dict):
    data = {}
    for key, pattern in pattern_dict.items():
        match = re.search(pattern, text)
        if match:
            if key == "감마GTP" and match.lastindex and match.lastindex >= 2:
                data[key] = match.group(2).strip()
            else:
                data[key] = match.group(1).strip()
    return data

# ✅ 기준 비교 함수 (eval 예외 방지 포함)

def evaluate_against_criteria(parsed, gender, criteria):
    results = {}
    for item, rules in criteria.items():
        if item not in parsed:
            continue
        try:
            val = float(parsed[item])
        except:
            val = parsed[item]

        applicable = rules.get(gender, rules.get("공통"))
        for grade, condition in applicable.items():
            try:
                if eval(condition.replace("x", repr(val))):
                    results[item] = grade
                    break
            except Exception as e:
                print(f"❌ [조건 에러] 항목: {item}, 조건: {condition}, 값: {val}, 에러: {e}")
    return results

# ✅ 비정상 항목 필터링 함수

def extract_abnormal(results):
    body_map = {
        "혈색소": "빈혈 / 혈액",
        "BMI": "체중 / 대사",
        "요단백": "신장 / 요로계",
        "우울증 점수구간": "정신 건강",
        "감마GTP": "간 기능",
        "AST": "간 기능",
        "ALT": "간 기능"
    }
    return {
        k: {
            "판정": v,
            "관련 부위": body_map.get(k, "기타")
        }
        for k, v in results.items() if v != "정상A"
    }

# ✅ JSON 로딩 함수

def load_json_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

# ✅ 실행 흐름

if __name__ == "__main__":
    text_all = extract_text(input_path)
    pattern_map = load_json_file(pattern_file)
    criteria = load_json_file(criteria_file)

    parsed = parse_with_pattern_map(text_all, pattern_map)

    private_fields = ["몸무게(kg)"]
    for field in private_fields:
        if field in parsed:
            parsed[field] = "비공개"

    results = evaluate_against_criteria(parsed, gender, criteria)
    abnormal = extract_abnormal(results)

    print("\n📋 건강검진 추출 결과")
    for k, v in parsed.items():
        print(f"{k}: {v}")

    print("\n📊 기준 비교 판정 결과")
    for k, v in results.items():
        print(f"{k}: {v}")

    print("\n⚠️ 건강 개선이 필요한 항목 요약")
    if abnormal:
        for k, info in abnormal.items():
            print(f"- {k} ({info['관련 부위']}): {info['판정']}")
    else:
        print("모든 항목이 정상A입니다. 👏")

    output_data = {
        "parsed": parsed,
        "results": results,
        "abnormal": abnormal
    }
    with open("parsed_results.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print("\n✅ 분석 결과 saved: parsed_results.json")
