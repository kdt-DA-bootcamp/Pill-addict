import os
import re
import pdfplumber
import pytesseract
from PIL import Image
import cv2
import tempfile
from dotenv import load_dotenv

# ✅ 환경변수 로딩
load_dotenv()

# 📁 파일 경로 설정 (default 파일명)
base_dir = os.path.dirname(__file__)
pattern_map = {
    "이름": r"성명\s*([가-힣]+)",
    "생년월일": r"주민등록번호\s*([0-9]{6})",
    "검진일": r"검진일\s*([0-9]{4}\.\s*[0-9]{1,2}\.\s*[0-9]{1,2})",
    "키(cm)": r"키\s*\(cm\).+?([0-9.]+)\s*/",
    "몸무게(kg)": r"키\s*\(cm\).+?[0-9.]+\s*/\s*([0-9.]+)",
    "BMI": r"체질량지수.*?([0-9.]+)",
    "허리둘레(cm)": r"허리둘레.*?([0-9.]+)",
    "수축기혈압": r"\(?수축기[^\d]*(\d+)\s*/",
    "이완기혈압": r"\(?수축기[^\d]*\d+\s*/\s*(\d+)\s*mmHg",
    "혈색소": r"혈색소.*?(\d+\.?\d*)",
    "공복혈당": r"공복혈당.*?(\d+)",
    "AST": r"AST.*?(\d+)",
    "ALT": r"ALT.*?(\d+)",
    "감마GTP": r"(감마지티피|γ-?GTP).*?(\d+)",
    "요단백": r"요단백.*?(정상|경계|단백뇨 의심)",
    "eGFR": r"신사구체여과율.*?(\d+)",
    "우울증 점수구간": r"우울증상이 없음\((\s*\d+~\d+점)",
    "총콜레스테롤": r"총콜레스테롤.*?(비해당)",
    "중성지방": r"중성지방.*?(비해당)",
    "HDL 콜레스테롤": r"고밀도 콜레스테롤.*?(비해당)",
    "생활습관_절주": r"(절주 필요)",
    "생활습관_금연": r"(금연 필요)",
    "생활습관_운동": r"(운동 필요)"
}

criteria = {
    "혈색소": {
        "여성": {
            "정상A": "12.0 <= x <= 15.5",
            "정상B": "10.0 <= x < 12.0",
            "질환의심": "x < 10.0"
        },
        "남성": {
            "정상A": "13.0 <= x <= 16.5",
            "정상B": "12.0 <= x < 13.0",
            "질환의심": "x < 12.0"
        }
    },
    "공복혈당": {
        "공통": {
            "정상A": "x < 100",
            "정상B": "100 <= x <= 125",
            "질환의심": "x >= 126"
        }
    },
    "BMI": {
        "공통": {
            "정상A": "18.5 <= x <= 24.9",
            "정상B": "x < 18.5 or 25.0 <= x <= 29.9",
            "질환의심": "x >= 30"
        }
    },
    "수축기혈압": {
        "공통": {
            "정상A": "x < 120",
            "정상B": "120 <= x <= 139",
            "질환의심": "x >= 140"
        }
    },
    "이완기혈압": {
        "공통": {
            "정상A": "x < 80",
            "정상B": "80 <= x <= 89",
            "질환의심": "x >= 90"
        }
    },
    "AST": {
        "공통": {
            "정상A": "x <= 40",
            "정상B": "41 <= x <= 50",
            "질환의심": "x > 50"
        }
    },
    "ALT": {
        "공통": {
            "정상A": "x <= 35",
            "정상B": "36 <= x <= 45",
            "질환의심": "x > 45"
        }
    },
    "감마GTP": {
        "여성": {
            "정상A": "8 <= x <= 35",
            "정상B": "36 <= x <= 45",
            "질환의심": "x > 45"
        },
        "남성": {
            "정상A": "11 <= x <= 63",
            "정상B": "64 <= x <= 77",
            "질환의심": "x > 77"
        }
    },
    "요단백": {
        "공통": {
            "정상A": "x == '정상'",
            "정상B": "x == '경계'",
            "질환의심": "'의심' in x"
        }
    },
    "eGFR": {
        "공통": {
            "정상A": "x >= 60",
            "질환의심": "x < 60"
        }
    },
    "우울증 점수구간": {
        "공통": {
            "정상A": "'0~4점' in x",
            "정상B": "'5~9점' in x",
            "질환의심": "'10~19점' in x or '20~27점' in x"
        }
    }
}

# ✅ 텍스트 추출 (PDF, 이미지 대응)
def extract_text(path_or_obj):
    if isinstance(path_or_obj, str):
        ext = os.path.splitext(path_or_obj)[1].lower()
    else:
        ext = ".pdf"  # streamlit 업로드는 기본 PDF로 간주

    if ext == ".pdf":
        if isinstance(path_or_obj, str):
            with pdfplumber.open(path_or_obj) as pdf:
                return "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
        else:
            with pdfplumber.open(path_or_obj) as pdf:
                return "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    elif ext in [".png", ".jpg", ".jpeg"]:
        if isinstance(path_or_obj, str):
            img = cv2.imread(path_or_obj)
        else:
            img = cv2.imdecode(np.frombuffer(path_or_obj.read(), np.uint8), cv2.IMREAD_COLOR)
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


# ✅ 외부에서 호출할 수 있도록 함수화
def run_healthcheck_pipeline(file_path=None, file_obj=None):
    if file_obj:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(file_obj.read())
            tmp_path = tmp_file.name

        try:
            text = extract_text(tmp_path)
        finally:
            os.remove(tmp_path)

    elif file_path:
        text = extract_text(file_path)
    else:
        raise ValueError("file_path나 file_obj 둘 중 하나는 입력해야 합니다.")

    gender = infer_gender(text)

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
