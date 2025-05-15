# pipeline.py

import io
import re
import json
import pandas as pd
import pdfplumber
import pytesseract
from PIL import Image
import config
from openai import OpenAI 

# OpenAI 클라이언트 초기화
# API 키는 보통 환경 변수(OPENAI_API_KEY)에 설정해두면 자동으로 인식됩니다.
# 또는 config 파일에 API 키가 있다면 client = OpenAI(api_key=config.OPENAI_API_KEY) 와 같이 사용합니다.
# 이 예제에서는 함수 내에서 초기화하거나, pipeline.py 상단에 한 번만 초기화해도 됩니다.
# client = OpenAI() # 전역으로 한 번만 초기화하는 경우

def generate_openai_response(user_name: str, structured_data: dict) -> str:
    """
    OpenAI GPT를 사용하여 사용자 맞춤 응답을 생성합니다. (pipeline.py 내에 정의)
    """
    client = OpenAI() # 함수 호출 시마다 초기화하거나, 전역 client 사용
    # 만약 config.OPENAI_API_KEY 와 같이 API 키를 관리한다면:
    # client = OpenAI(api_key=config.OPENAI_API_KEY)

    # GPT에게 전달할 프롬프트를 구성합니다.
    # structured_data에서 필요한 정보를 추출하여 상세한 프롬프트를 만듭니다.
    exam_results_str = json.dumps(structured_data.get('exam_results', {}), ensure_ascii=False, indent=2)
    abnormal_findings_str = json.dumps(structured_data.get('abnormal_findings', {}), ensure_ascii=False, indent=2)
    
    ingredients_details = []
    for ing_info in structured_data.get('ingredient_info', []):
        details = f"- {ing_info.get('name', '이름 없음')}: 기능({ing_info.get('function', '정보 없음')}), 주의사항({ing_info.get('caution', '정보 없음')})"
        ingredients_details.append(details)
    ingredients_str = "\n".join(ingredients_details) if ingredients_details else "추천 성분 정보 없음"

    product_examples = []
    for prod in structured_data.get('recommended_products', [])[:2]: # 예시로 2개 제품만
        product_examples.append(f"- {prod.get('PRDLST_NM', '제품명 없음')} (제조사: {prod.get('BSSH_NM', '제조사 정보 없음')})")
    products_str = "\n".join(product_examples) if product_examples else "추천 제품 예시 없음"

    prompt = (
        f"{user_name}님의 건강 검진 결과 및 정보를 바탕으로 개인 맞춤형 건강 관리 조언 및 영양제 추천을 상세하고 친절하게 제공해주세요.\n\n"
        f"### 사용자 정보\n"
        f"- 이름: {user_name}\n\n"
        f"### 건강검진 주요 결과:\n{exam_results_str}\n\n"
        f"### 주의가 필요한 항목 (이상 소견 분석):\n{abnormal_findings_str}\n\n"
        f"### 추천 영양 성분 및 상세 정보:\n{ingredients_str}\n\n"
        f"### 추천 제품 예시 (참고용):\n{products_str}\n\n"
        f"### 요청사항:\n"
        f"1. 위의 모든 정보를 종합적으로 고려하여 {user_name}님만을 위한 맞춤형 건강 조언을 구체적으로 작성해주세요.\n"
        f"2. 각 추천 성분이 왜 필요한지, 어떤 도움을 줄 수 있는지, 그리고 섭취 시 특별히 주의해야 할 사항이 있다면 명확하게 설명해주세요.\n"
        f"3. 전반적인 건강 증진을 위한 생활 습관 개선 방안도 함께 제안해주시면 좋겠습니다.\n"
        f"4. 답변은 전문가적이면서도 이해하기 쉽고 친근한 어투로 작성해주세요."
    )

    messages_for_api = [
        {"role": "system", "content": "당신은 사용자의 건강검진 데이터와 개인 정보를 바탕으로 심층적인 건강 분석 및 맞춤형 영양제 추천, 생활 습관 조언을 제공하는 전문 AI 건강 컨설턴트입니다."},
        {"role": "user", "content": prompt}
    ]

    try:
        response = client.chat.completions.create(
            model=config.MODEL_NAME,  # config 파일에 정의된 모델 이름 사용
            messages=messages_for_api,
            max_tokens=2000,  # 응답 길이는 필요에 따라 조절
            temperature=0.7   # 창의성과 일관성 조절 (0.0 ~ 2.0)
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI API 호출 중 오류 발생: {e}")
        # 실제 서비스에서는 사용자에게 좀 더 친절한 오류 메시지를 반환하는 것이 좋습니다.
        return "죄송합니다. AI 응답을 생성하는 데 문제가 발생했습니다. 잠시 후 다시 시도해주세요."

# --- 기존 함수들은 그대로 사용 ---
def parse_health_exam(file_bytes: bytes, file_type: str) -> tuple[dict,str]:
    text = ""
    if file_type == "pdf":
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or "" # Ensure page_text is not None
                text += page_text + "\n"
    else: # 이미지 파일 처리
        img = Image.open(io.BytesIO(file_bytes))
        text = pytesseract.image_to_string(img, lang="kor+eng") # tesseract OCR 사용

    patterns = {
        "혈색소":    r"혈색소[^0-9]*?(\d+\.?\d*)", # 검사명과 숫자 사이 다른 문자 허용
        "공복혈당":  r"공복혈당[^0-9]*?(\d+\.?\d*)",
        "BMI":      r"(?:BMI|체질량지수)[^0-9]*?(\d+\.?\d*)",
        "허리둘레":  r"허리둘레[^0-9]*?(\d+\.?\d*)",
        "AST":      r"AST\(SGOT\)[^0-9]*?(\d+\.?\d*)|AST[^0-9]*?(\d+\.?\d*)", # AST(SGOT) 또는 AST
        "ALT":      r"ALT\(SGPT\)[^0-9]*?(\d+\.?\d*)|ALT[^0-9]*?(\d+\.?\d*)", # ALT(SGPT) 또는 ALT
        "감마GTP":  r"(?:감마지티피|감마GTP|\ ?-GTP)[^0-9]*?(\d+\.?\d*)", # 다양한 감마GTP 표현
        "요단백":    r"요단백[^■]*?■\s*([가-힣]+)" # 상태 값을 직접 추출 (예: 정상, 경계, 양성 등)
    }

    result = {}
    print("---- OCR 결과 ----") # OCR 결과 확인용 (디버깅 시)
    print(text)
    print("--------------------")

    for key, pat in patterns.items():
        # AST, ALT의 경우 두 가지 패턴을 시도
        if key == "AST" or key == "ALT":
            m = re.search(patterns[key], text) # 기본 패턴 먼저 시도 (예: AST(SGOT) 123)
                                               # 이 부분은 패턴을 더 정교하게 만들어야 합니다.
                                               # 현재는 첫번째 그룹 또는 두번째 그룹 중 하나를 사용하려고 시도해야 함
                                               # 간단하게는 이렇게 할 수 있습니다.
            match_obj = re.search(pat, text)
            if match_obj:
                # 첫 번째 그룹(예: AST(SGOT)의 값) 또는 두 번째 그룹(예: AST만의 값) 중 유효한 것을 찾습니다.
                val_str = match_obj.group(1) if match_obj.group(1) else match_obj.group(2)
            else:
                val_str = None
        else:
            m = re.search(pat, text)
            val_str = m.group(1) if m else None

        if val_str is None:
            # print(f"Warning: '{key}' not found or pattern mismatch in the document.")
            continue
        
        val_str = val_str.strip() # 공백 제거

        try:
            if key == "요단백": # 요단백은 문자열 그대로 저장 (예: "정상", "경계", "양성(+)")
                # "정상" 또는 "음성" 외의 값을 비정상으로 간주할 수 있도록 값 표준화 필요 시 여기에 로직 추가
                # 예: "양성(1+)" -> "양성"
                if "정상" in val_str or "음성" in val_str: # 다양한 정상 표현 처리
                    result[key] = "정상"
                elif "경계" in val_str:
                    result[key] = "경계"
                elif "양성" in val_str or "+" in val_str : # 다양한 양성 표현 처리
                     # 실제 값에 따라 더 세분화된 상태로 저장 가능 (예: "단백뇨 의심" 대신 실제 값 "양성(++)")
                    result[key] = "단백뇨 의심" # 또는 val_str 그대로 저장
                else:
                    result[key] = val_str # 인식된 값 그대로 저장
            else:
                result[key] = float(val_str)
        except ValueError:
            # print(f"Warning: Could not convert value for '{key}' ('{val_str}') to float.")
            result[key] = val_str # 변환 실패 시 문자열로 저장 또는 다른 처리
            
    return result, text

def load_reference() -> dict:
    # (사용자 코드와 동일하게 유지)
    data = {
        "혈색소": {
            "여성": {"min": 12.0, "max": 15.5, "unit": "g/dL"},
            "남성": {"min": 13.0, "max": 17.0, "unit": "g/dL"}
        },
        "공복혈당": {
            "공통": {"min": 70.0, "max": 100.0, "unit": "mg/dL"} # 100 미만 정상
        },
        "BMI": {
            "공통": { # 대한비만학회 기준 (2018)
                "저체중": {"min": 0, "max": 18.4, "unit": "kg/m²"}, 
                "정상": {"min": 18.5, "max": 22.9, "unit": "kg/m²"}, # 18.5 ~ 22.9 정상
                "과체중": {"min": 23.0, "max": 24.9, "unit": "kg/m²"}, # 23.0 ~ 24.9 과체중 (비만 전단계)
                "1단계 비만": {"min": 25.0, "max": 29.9, "unit": "kg/m²"}, # 25.0 ~ 29.9 1단계 비만
                "2단계 비만": {"min": 30.0, "max": 34.9, "unit": "kg/m²"}, # 30.0 ~ 34.9 2단계 비만
                "3단계 비만": {"min": 35.0, "max": float('inf'), "unit": "kg/m²"} # 35.0 이상 3단계 비만 (고도비만)
            }
        },
        "허리둘레": {
            "남성": {"복부비만_기준": 90.0, "unit": "cm"}, 
            "여성": {"복부비만_기준": 85.0, "unit": "cm"}
        },
        "AST": { # AST (SGOT)
            "공통": {"min": 0.0,  "max": 40.0,  "unit": "U/L"} # 일반적인 정상 범위
        },
        "ALT": { # ALT (SGPT)
            "공통": {"min": 0.0,  "max": 40.0,  "unit": "U/L"} # 일반적인 정상 범위 (기관에 따라 35 U/L까지 보기도 함)
        },
        "감마GTP": { # 감마-GTP (γ-GTP)
            "남성": {"min": 11.0, "max": 73.0, "unit": "U/L"}, 
            "여성": {"min": 8.0,  "max": 46.0, "unit": "U/L"}  
        },
        "요단백": {
            "공통": {"normal": "정상", "unit": None} # "음성"도 정상으로 처리
        }
    }
    return data

def find_abnormal(exam: dict, ref_data: dict, user_gender: str) -> dict:
    # (사용자 코드와 동일하게 유지하되, BMI와 요단백 기준 수정)
    abnormal = {}
    for item, value in exam.items():
        if item not in ref_data or value is None:
            continue

        item_ref_info = ref_data[item]
        specific_ref_data = item_ref_info.get(user_gender, item_ref_info.get("공통"))

        if not specific_ref_data:
            continue

        if item == "BMI":
            status_note = ""
            bmi_val = float(value) # Ensure value is float for comparison
            if bmi_val < specific_ref_data["정상"]["min"]:
                status_note = "저체중"
            elif bmi_val > specific_ref_data["정상"]["max"]: # 정상 범위를 벗어난 경우
                if bmi_val <= specific_ref_data["과체중"]["max"]:
                    status_note = "과체중"
                elif bmi_val <= specific_ref_data["1단계 비만"]["max"]:
                    status_note = "1단계 비만"
                elif bmi_val <= specific_ref_data["2단계 비만"]["max"]:
                    status_note = "2단계 비만"
                else: # 3단계 비만
                    status_note = "3단계 비만"
            
            if status_note: # 저체중, 과체중, 비만 단계에 해당할 경우
                abnormal[item] = {
                    "value": bmi_val,
                    "reference": f"정상: {specific_ref_data['정상']['min']}~{specific_ref_data['정상']['max']} {specific_ref_data['정상']['unit']}",
                    "note": status_note
                }
            continue

        elif item == "허리둘레":
            if isinstance(value, (int, float)) and "복부비만_기준" in specific_ref_data:
                threshold = specific_ref_data["복부비만_기준"]
                unit = specific_ref_data.get("unit", "cm")
                if value >= threshold:
                    abnormal[item] = {
                        "value": value,
                        "reference": f"정상(복부비만 해당없음): {threshold}{unit} 미만 ({user_gender} 기준)",
                        "note": "복부비만"
                    }
            continue
        
        # 요단백 처리: OCR 결과가 "정상"이 아니면 이상으로 간주
        elif item == "요단백":
            normal_val = specific_ref_data.get("normal", "정상") # "정상" 또는 "음성"
            # OCR 결과가 "정상" 또는 "음성" 문자열을 포함하지 않으면 비정상으로 처리
            if isinstance(value, str) and normal_val not in value:
                 abnormal[item] = {
                    "value": value, # 실제 OCR 값 (예: "경계", "단백뇨 의심", "양성(++)")
                    "reference": f"정상: {normal_val}",
                    "note": f"{value}" # 실제 검출된 값을 note로 사용
                }
            continue

        # 기타 수치 항목 (min/max 기준)
        if isinstance(value, (int, float)):
            current_range_ref = specific_ref_data
            if "정상" in specific_ref_data and isinstance(specific_ref_data["정상"], dict): # BMI 같은 계층적 구조 제외
                 current_range_ref = specific_ref_data["정상"]

            if "min" in current_range_ref and "max" in current_range_ref:
                val_float = float(value)
                min_val = float(current_range_ref["min"])
                max_val = float(current_range_ref["max"])
                note = ""
                if val_float < min_val:
                    note = "낮음"
                elif val_float > max_val:
                    note = "높음"
                
                if note:
                    gender_note = f" ({user_gender} 기준)" if user_gender in item_ref_info and user_gender != "공통" else ""
                    abnormal[item] = {
                        "value": val_float,
                        "reference": f"{min_val}~{max_val} {current_range_ref.get('unit', '')}{gender_note}",
                        "note": note
                    }
    return abnormal

ABNORMAL_TO_INGREDIENTS_TUPLE_KEY = {
    # (항목명, 상태) 튜플을 키로 사용
    ("혈색소", "낮음"): ["철", "엽산", "비타민C", "비타민B12"],
    ("요단백", "경계"): ["크랜베리", "비타민C", "아연", "프로바이오틱스"], # 요단백 '경계' 상태에 대한 추천
    ("요단백", "단백뇨 의심"): ["크랜베리", "비타민C", "아연", "오메가-3", "프로바이오틱스"], # '단백뇨 의심' 상태 (더 적극적 관리)
    # 실제 요단백 값 (예: "양성(++)")을 note로 사용할 경우, 그 값에 대한 매핑도 추가 가능
    ("공복혈당", "높음"): ["바나바잎추출물", "크롬", "여주추출물", "알파리포산", "마그네슘"], # 혈당 조절 기능성 원료 위주
    ("AST", "높음"): ["밀크씨슬(실리마린)", "비타민E", "UDCA(우르소데옥시콜산)"], # 간 기능 개선
    ("ALT", "높음"): ["밀크씨슬(실리마린)", "비타민E", "UDCA(우르소데옥시콜산)", "NAC(N-아세틸시스테인)"], # 간 기능 개선
    ("감마GTP", "높음"): ["밀크씨슬(실리마린)", "비타민B군", "글루타치온", "셀레늄"], # 간 해독 및 항산화
    ("BMI", "저체중"): ["종합비타민", "미네랄", "단백질보충제"], # 체중 증가 및 영양 균형
    ("BMI", "과체중"): ["녹차추출물(카테킨)", "가르시니아캄보지아추출물", "CLA(공액리놀레산)", "식이섬유"], # 체지방 감소 도움
    ("BMI", "1단계 비만"): ["녹차추출물(카테킨)", "가르시니아캄보지아추출물", "CLA(공액리놀레산)", "L-카르니틴", "식이섬유"],
    ("BMI", "2단계 비만"): ["녹차추출물(카테킨)", "가르시니아캄보지아추출물", "L-카르니틴", "오메가-3", "프로바이오틱스"], # 더 적극적 관리
    ("BMI", "3단계 비만"): ["녹차추출물(카테킨)", "L-카르니틴", "오메가-3", "프로바이오틱스", "식이섬유"], # 고도비만 관리
    ("허리둘레", "복부비만"): ["오메가-3", "식이섬유", "프로바이오틱스", "녹차추출물(카테킨)"] # 복부 지방 및 내장지방 관리
}

def get_ingredients_from_abnormal_tuple(abnormal: dict) -> list[str]:
    # (사용자 코드와 동일하게 유지, ABNORMAL_TO_INGREDIENTS_TUPLE_KEY의 'note' 값과 일치하도록 find_abnormal 수정 필요)
    rec = set()
    for item_name, details in abnormal.items():
        status = details.get("note") # 예: "낮음", "과체중", "복부비만", "경계", "단백뇨 의심"
        # find_abnormal에서 요단백의 note를 실제 값("경계", "단백뇨 의심")으로 설정했으므로 별도 처리 불필요

        lookup_key = (item_name, status)
        if lookup_key in ABNORMAL_TO_INGREDIENTS_TUPLE_KEY:
            rec.update(ABNORMAL_TO_INGREDIENTS_TUPLE_KEY[lookup_key])
        # else:
            # print(f"Debug: No ingredient mapping for key {lookup_key}") # 매핑되지 않는 키 확인용
    return list(rec)

def recommend_products(ingredients: list[str], supplement_data: list[dict], top_n: int = 3) -> list[dict]:
    # (사용자 코드와 동일하게 유지)
    recommended_products = []
    if not ingredients: # 추천 성분이 없으면 빈 리스트 반환
        return recommended_products
        
    for product in supplement_data:
        # 제품의 기능성 원료명(INDIV_RAWMTRL_NM) 또는 전체 원재료명(RAWMTRL_NM)에 추천 성분이 포함되어 있는지 확인
        # 하나라도 포함되면 추천 (any 사용)
        # 문자열로 변환하여 부분 일치 확인 (예: "비타민C"가 "비타민C분말"에 포함)
        
        # INDIV_RAWMTRL_NM 필드가 있고, 문자열이며, 비어있지 않은 경우에만 검사
        raw_materials_to_check = []
        if product.get("INDIV_RAWMTRL_NM") and isinstance(product["INDIV_RAWMTRL_NM"], str):
            raw_materials_to_check.append(str(product["INDIV_RAWMTRL_NM"]))
        # RAWMTRL_NM 필드도 추가로 확인 (선택 사항)
        # if product.get("RAWMTRL_NM") and isinstance(product["RAWMTRL_NM"], str):
        #     raw_materials_to_check.append(str(product["RAWMTRL_NM"]))

        found_ingredient = False
        for raw_material_field in raw_materials_to_check:
            if any(ing.lower() in raw_material_field.lower() for ing in ingredients): # 대소문자 구분 없이 비교
                found_ingredient = True
                break
        
        if found_ingredient:
            recommended_products.append(product)
            if len(recommended_products) >= top_n:
                break
    return recommended_products

def load_ingredient_info() -> pd.DataFrame:
    # (사용자 코드와 동일하게 유지, JSON 파일 경로 확인)
    # config.INGREDIENT_CSV_PATH 가 실제로는 JSON 파일 경로를 가리킨다고 가정합니다.
    # 파일 확장자가 .csv로 되어 있지만 실제 내용은 JSON인 경우가 있을 수 있습니다.
    try:
        df = pd.read_json(config.INGREDIENT_JSON_PATH, dtype=str) # 경로 수정 및 JSON 명시
    except ValueError as e:
        print(f"Error loading ingredient info from JSON: {e}")
        print(f"Attempting to load as CSV: {config.INGREDIENT_JSON_PATH}") # 경로명 변경 INGREDIENT_CSV_PATH -> INGREDIENT_JSON_PATH
        try:
            # CSV 파일로 로드 시도 (인코딩 문제 발생 가능성 있음)
            df = pd.read_csv(config.INGREDIENT_JSON_PATH, dtype=str) # 경로명 변경 INGREDIENT_CSV_PATH -> INGREDIENT_JSON_PATH
        except Exception as csv_e:
            print(f"Error loading ingredient info as CSV: {csv_e}")
            # 빈 DataFrame 반환 또는 예외 재발생 등의 오류 처리
            return pd.DataFrame()


    # APLC_RAWMTRL_NM (원료명)을 인덱스로 설정
    if "APLC_RAWMTRL_NM" in df.columns:
        df = df.set_index("APLC_RAWMTRL_NM")
    else:
        print("Warning: 'APLC_RAWMTRL_NM' column not found in ingredient data. Index not set.")
        # 인덱스 설정 실패 시 다른 컬럼을 사용하거나, 인덱스 없이 진행하도록 처리 필요

    # FNCLTY_CN 컬럼명을 'function'으로 변경
    if "FNCLTY_CN" in df.columns:
        df = df.rename(columns={"FNCLTY_CN": "function"})
    else:
        print("Warning: 'FNCLTY_CN' column not found. 'function' column will be missing.")
        df["function"] = "기능성 정보 없음" # 'function' 컬럼이 없을 경우 기본값으로 생성

    return df

def load_msd_manual() -> dict:
    # (사용자 코드와 동일하게 유지)
    try:
        with open(config.MSD_MANUAL_JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Warning: MSD manual file not found at {config.MSD_MANUAL_JSON_PATH}")
        return {}
    except json.JSONDecodeError:
        print(f"Warning: Error decoding MSD manual JSON from {config.MSD_MANUAL_JSON_PATH}")
        return {}

    msd_map = {}
    if isinstance(data, list): # 데이터가 리스트 형태일 경우 (각 항목이 딕셔너리)
        for entry in data:
            # JSON 파일의 실제 키 이름에 맞춰 "ingredient", "name" 등을 사용
            # "caution", "주의사항" 등도 마찬가지
            ingredient_key = entry.get("ingredient", entry.get("name")) 
            caution_key = entry.get("caution", entry.get("주의사항", "")) # 기본값으로 빈 문자열
            if ingredient_key: # 성분명이 있는 경우에만 맵에 추가
                msd_map[ingredient_key] = caution_key
    elif isinstance(data, dict): # 데이터가 이미 { "성분명": "주의사항" } 형태의 딕셔너리일 경우
        msd_map = data
    else:
        print("Warning: MSD manual data is not in expected list or dict format.")
    
    return msd_map


def build_structured_data(
    exam: dict,
    abnormal: dict,
    ingredients: list[str], # 추천된 성분 이름 리스트 (문자열)
    products: list[dict],
    ing_info_df: pd.DataFrame, # 성분 정보 DataFrame (인덱스: 성분명, 'function' 컬럼 포함)
    msd_info: dict, # MSD 매뉴얼 정보 (딕셔너리: { 성분명: 주의사항 })
    user_name: str
) -> dict:
    
    # DataFrame이 비어있거나 'function' 컬럼이 없는 경우에 대한 방어 코드
    if ing_info_df.empty or "function" not in ing_info_df.columns:
        func_map = {}
        # print("Warning: Ingredient info DataFrame is empty or 'function' column is missing. Using empty function map.")
    else:
        func_map = ing_info_df["function"].to_dict()

    detailed_ingredient_info = []
    for ingredient_name in ingredients: # 추천된 성분 이름(str) 리스트 순회
        function = func_map.get(ingredient_name, "해당 성분에 대한 기능성 정보가 없습니다.")
        caution = msd_info.get(ingredient_name, "해당 성분에 대한 주의사항 정보가 없습니다.")
        detailed_ingredient_info.append({
            "name": ingredient_name,
            "function": function,
            "caution": caution
        })

    structured_data = {
        "user_name": user_name,
        "exam_results": exam,
        "abnormal_findings": abnormal,
        # "recommended_ingredients"는 이제 상세 정보를 포함한 리스트로 대체되거나,
        # 또는 GPT 프롬프트에서 "ingredient_info"를 직접 활용합니다.
        # 여기서는 "ingredient_info"를 사용하고, "recommended_ingredients"는 이름 목록으로 유지할 수 있습니다.
        "recommended_ingredients": [{"name": ing_name} for ing_name in ingredients], # 단순 이름 목록
        "ingredient_info": detailed_ingredient_info, # 이름, 기능, 주의사항 포함된 상세 목록
        "recommended_products": products,
        "msd_manual_info": msd_info, # 전체 MSD 정보 (GPT가 참고할 수 있도록)
    }
    
    gpt_response_content = generate_openai_response(user_name, structured_data)

    return {"structured_data": structured_data, "gpt_response": gpt_response_content}