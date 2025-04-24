# 📁 main.py — PDF 건강검진 결과 유연한 판정 템플릿 (.json 기반, 오류 방지 포함)

import pdfplumber
import json
import os
import re
from dotenv import load_dotenv

# ✅ 환경 변수 로드
load_dotenv()

# 🔧 경로 설정
base_dir = os.path.dirname(__file__)
pdf_path = os.path.join(base_dir, os.getenv("PDF_FILE", "이루시아검진결과.pdf"))
pattern_file = os.path.join(base_dir, os.getenv("PATTERN_FILE", "pattern_map.json"))
criteria_file = os.path.join(base_dir, os.getenv("CRITERIA_FILE", "criteria.json"))
gender = os.getenv("DEFAULT_GENDER", "여성")

# PDF 텍스트 추출 함수
def extract_text_from_pdf(pdf_path):
    text_all = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_all += page_text + "\n"
    return text_all

# 정규표현식 기반 파서
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

# JSON 로딩 함수
def load_json_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

# 메인 실행 흐름
if __name__ == "__main__":
    text_all = extract_text_from_pdf(pdf_path)
    pattern_map = load_json_file(pattern_file)
    criteria = load_json_file(criteria_file)

    parsed = parse_with_pattern_map(text_all, pattern_map)

    # 비공개 처리 항목
    private_fields = ["몸무게(kg)"]
    for field in private_fields:
        if field in parsed:
            parsed[field] = "비공개"

    results = evaluate_against_criteria(parsed, gender, criteria)

    print("\n📋 PDF 기반 건강검진 추출 결과")
    for k, v in parsed.items():
        print(f"{k}: {v}")

    print("\n📊 기준 비교 판정 결과")
    for k, v in results.items():
        print(f"{k}: {v}")
        
output_data = {
    "parsed": parsed,
    "results": results
}
with open("parsed_results.json", "w", encoding="utf-8") as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)
