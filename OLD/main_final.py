# 📁 healthcheck_parser.py — 범용 건강검진 결과 분석기 (PDF, 이미지 대응)

import os
import re
import json
import pdfplumber
import pytesseract
from PIL import Image
import cv2
from dotenv import load_dotenv

# ✅ 환경변수 로딩
load_dotenv()

# 📁 파일 경로 설정
base_dir = os.path.dirname(__file__)
input_file = os.path.join(base_dir, os.getenv("INPUT_FILE", "input.pdf"))
pattern_file = os.path.join(base_dir, os.getenv("PATTERN_FILE", "pattern_map.json"))
criteria_file = os.path.join(base_dir, os.getenv("CRITERIA_FILE", "criteria.json"))

# ✅ 텍스트 추출 (PDF, 이미지 대응)
def extract_text(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        with pdfplumber.open(path) as pdf:
            return "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    elif ext in [".png", ".jpg", ".jpeg"]:
        img = cv2.imread(path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return pytesseract.image_to_string(gray, lang='kor+eng')
    else:
        raise ValueError("지원하지 않는 파일 형식입니다.")

# ✅ 성별 자동 추정
def infer_gender(text):
    match = re.search(r"\d{6}[-–](\d)", text)
    if match:
        return "남성" if match.group(1) in ["1", "3", "5"] else "여성"
    return os.getenv("DEFAULT_GENDER", "여성")

# ✅ 정규표현식 기반 파싱
def parse_with_patterns(text, pattern_map):
    result = {}
    for key, pattern in pattern_map.items():
        match = re.search(pattern, text)
        if match:
            result[key] = match.group(1).strip()
    return result

# ✅ 기준 비교 및 판정
def evaluate(parsed, gender, criteria):
    results = {}
    for key, rule in criteria.items():
        if key not in parsed:
            continue
        val = parsed[key]
        try:
            val = float(val)
        except:
            pass

        applicable = rule.get(gender, rule.get("공통", {}))
        for grade, condition in applicable.items():
            try:
                if eval(condition.replace("x", repr(val))):
                    results[key] = grade
                    break
            except Exception as e:
                print(f"[조건 오류] {key}: {condition} -> {e}")
    return results

# ✅ 비정상 항목 요약
def extract_abnormal(results):
    mapping = {
        "혈색소": "빈혈 / 혈액", "BMI": "체중 / 대사", "요단백": "신장 / 요로계",
        "우울증 점수구간": "정신 건강", "감마GTP": "간 기능", "AST": "간 기능", "ALT": "간 기능"
    }
    return {
        k: {"판정": v, "관련 부위": mapping.get(k, "기타")}
        for k, v in results.items() if v != "정상A"
    }

# ✅ JSON 로딩 유틸
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# ✅ 외부에서 호출할 수 있도록 함수화
def run_healthcheck_pipeline(file_path):
    text = extract_text(file_path)
    gender = infer_gender(text)
    pattern_map = load_json(pattern_file)
    criteria = load_json(criteria_file)

    parsed = parse_with_patterns(text, pattern_map)
    for field in ["몸무게(kg)"]:
        if field in parsed:
            parsed[field] = "비공개"

    results = evaluate(parsed, gender, criteria)
    abnormal = extract_abnormal(results)

    return {
        "gender": gender,
        "parsed": parsed,
        "results": results,
        "abnormal": abnormal
    }

# ✅ 실행
if __name__ == "__main__":
    text = extract_text(input_file)
    gender = infer_gender(text)
    pattern_map = load_json(pattern_file)
    criteria = load_json(criteria_file)

    parsed = parse_with_patterns(text, pattern_map)
    for field in ["몸무게(kg)"]:
        if field in parsed:
            parsed[field] = "비공개"

    results = evaluate(parsed, gender, criteria)
    abnormal = extract_abnormal(results)

    print("\n📋 건강검진 추출 결과")
    for k, v in parsed.items():
        print(f"{k}: {v}")

    print("\n📊 기준 비교 판정 결과")
    for k, v in results.items():
        print(f"{k}: {v}")

    print("\n⚠️ 건강 개선이 필요한 항목")
    if abnormal:
        for k, v in abnormal.items():
            print(f"- {k} ({v['관련 부위']}): {v['판정']}")
    else:
        print("모든 항목이 정상A입니다. 👏")

    # 저장
    with open("parsed_results.json", "w", encoding="utf-8") as f:
        json.dump({"parsed": parsed, "results": results, "abnormal": abnormal}, f, ensure_ascii=False, indent=2)

    print("\n✅ 분석 결과 saved: parsed_results.json")
