import streamlit as st
import json, time, random, pathlib
import pandas as pd
from streamlit_lottie import st_lottie
import requests
from requests.exceptions import RequestException

# ────── 📦 PILL-ADDICT PIPELINE ──────────────────────────────
# 같은 프로젝트 폴더 안에 있는 pipeline.py 를 그대로 import
# from pipeline import (
#     parse_health_exam, load_reference, find_abnormal,
#     get_ingredients_from_abnormal_tuple, load_ingredient_info,
#     load_msd_manual, recommend_products, build_structured_data
# )
# ▸ pipeline.py 가 다른 디렉터리에 있으면 PYTHONPATH 추가 or sys.path 수정 필요
# ─────────────────────────────────────────────────────────────

st.set_page_config(layout="centered", page_title="건강 챗봇 UI")

# ────── Lottie JSON 로드 ────────────────────────────────────
#try:
#    with open("health_loading.json", "r", encoding="utf-8") as f:
#        lottie_health = json.load(f)
#except Exception:
#    lottie_health = None
# ─── 경로 상수 & Lottie 로더 ───────────────────────────────
BASE_DIR = pathlib.Path(__file__).parent          # 현재 스크립트 위치
ASSETS_DIR = BASE_DIR               

def load_lottie_json(path: str | pathlib.Path):
    """로컬 Lottie JSON을 안전하게 불러온다."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.warning(f"Lottie 로딩 실패: {e}")      # 사용자에게 알림
        return None

lottie_health = load_lottie_json(ASSETS_DIR / "health_loading.json")
# ────── 세션 초기화 ─────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "intro"
if "selected_body_part" not in st.session_state:
    st.session_state.selected_body_part = ""
if "history" not in st.session_state:
    st.session_state.history = []

# ────── 신체 부위 예시 ─────────────────────────────────────
body_part_examples = {
    "신경계": "기억력 저하, 긴장, 수면의 질, 피로",
    "소화/대사계": "위, 간, 장, 체지방, 칼슘흡수",
    "생식/비뇨계": "전립선, 배뇨, 요로",
    "신체 방어/면역계": "면역, 항산화",
    "감각계": "눈, 치아, 피부",
    "심혈관계": "혈중 중성지방, 콜레스테롤, 혈압, 혈행",
    "내분비계": "혈당, 갱년기 여성, 갱년기 남성, 월경 전 증후군, 생리불순 등",
    "근육계": "관절, 근력, 뼈, 운동수행능력"
}

#색상 스터마이징 스타일 (빨간색, 흰색, 노란색 계열) ---
st.markdown(
    """
    <style>
    html, body, [class*="css"] {
        font-family: 'Segoe UI', sans-serif;
        base = "light"
        background-color: #fff8f0;
        secondaryBackgroundColor = "#fffefb" # 컨테이너‧사이드바 등
        color: #1f1f1f;

    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 900px;
        margin: auto;
        background-color: #fffefb;
        border-radius: 18px;
        padding-left: 2rem;
        padding-right: 2rem;
        box-shadow: 0 0 10px rgba(255, 215, 0, 0.1);
    }
    div.stButton > button {
        background: linear-gradient(135deg, #ff6b6b, #ffd93d);
        color: white;
        padding: 14px 20px;
        width: 100%;
        max-width: 320px;
        border: none;
        border-radius: 14px;
        font-size: 16px;
        font-weight: bold;
        margin: 10px auto;
        display: block;
        box-shadow: 0 6px 18px rgba(0,0,0,0.2);
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #ff3b3b, #ffe24d);
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
    }
    .stCaption {
        color: #666666;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ────── 유틸: 버튼 ↔ 페이지 전환 ───────────────────────────

def render_uniform_button(label: str, target_page: str):
    col = st.columns([3, 3, 3])[1]
    with col:
        if st.button(label, key=label):
            st.session_state.history.append(st.session_state.page)
            st.session_state.page = target_page
            st.rerun()

def render_main_buttons():
    render_uniform_button("검진 기반 추천", "검진 기반 추천")
    render_uniform_button("신체 부위 기반 추천", "신체 부위 기반 추천")
    render_uniform_button("연령대 기반 추천", "연령대 기반 추천")

loading_messages = [
    "🧬 건강 데이터를 정밀 분석하는 중입니다...",
    "🍃 당신의 건강을 위한 자연의 조합을 준비하고 있어요...",
    "💊 당신의 몸에 꼭 맞는 영양소를 찾고 있어요...",
    "☕ AI가 건강 상담 중입니다. 따뜻한 차 한 잔 어떠세요?",
    "💪 맞춤 영양 루틴 생성 중입니다. 잠시만 기다려주세요!"
]

# ────── 인트로 페이지 ───────────────────────────────────
if st.session_state.page == "intro":
    st.session_state.history.clear()
    st.markdown("""
        <div style='text-align: center; margin-top: 5rem;'>
            <h1 style='font-size: 2.8rem;'>당신의 건강을 위하여</h1>
            <p style='font-size: 18px; color: #d1d5db;'>AI 기반 건강 분석 및 맞춤 추천을 받아보세요.</p>
        </div>
    """, unsafe_allow_html=True)
    render_main_buttons()
    st.stop()

# ────── 상단 네비게이션 (공통) ───────────────────────────
col1, col2, col3 = st.columns([3, 3, 4])
with col1:
    if st.button("사용자 기본정보"):
        st.session_state.history.append(st.session_state.page)
        st.session_state.page = "사용자 설정"
        st.rerun()
with col2:
    if st.session_state.page != "intro":
        if st.button("홈으로"):
            st.session_state.page = "intro"
            st.rerun()

# 이전 버튼
if st.session_state.page != "intro":
    col_a, col_b = st.columns([5, 1])
    with col_b:
        if st.button("이전으로"):
            if st.session_state.history:
                st.session_state.page = st.session_state.history.pop()
            else:
                st.session_state.page = "intro"
            st.rerun()

# ────── 중앙 카드 시작 ───────────────────────────────────
st.markdown("""
    <div style='
        max-width: 720px;
        margin: 0 auto;
        padding: 2rem;
        display: flex;
        flex-direction: column;
        align-items: center;
    '>
""", unsafe_allow_html=True)

# ────── PAGE: 건강검진 기반 추천 ───────────────────────
if st.session_state.page == "검진 기반 추천":
    st.subheader("건강검진 기반 추천")

    # 사용자 기본 입력
    user_name = st.text_input("이름", key="username_exam")
    gender    = st.radio("성별", ["여성", "남성"], horizontal=True, key="gender_exam")

    uploaded_file = st.file_uploader("건강검진 결과 PDF / 이미지", type=["jpg", "jpeg", "png", "pdf"], key="exam_file")

    if uploaded_file and user_name and gender:
        if st.button("분석 실행", key="run_exam"):
            with st.spinner(random.choice(loading_messages)):
                if lottie_health:
                    st_lottie(lottie_health, height=160)
                else:
                    st.warning("🔄 분석 중입니다... (애니메이션 로딩 실패)")
                file_bytes = uploaded_file.read()
                file_type  = "pdf" if uploaded_file.type == "application/pdf" else "image"

                # 1) OCR & 파싱
                exam_dict, ocr_text = parse_health_exam(file_bytes, file_type)

                # 2) 이상치 탐지
                ref_data   = load_reference()
                abnormal   = find_abnormal(exam_dict, ref_data, gender)

                # 3) 성분 & 제품 추천
                ingredients       = get_ingredients_from_abnormal_tuple(abnormal)
                ing_info_df       = load_ingredient_info()
                msd_manual        = load_msd_manual()
                try:
                    supplements_df = pd.read_json("data/supplements.json")
                except FileNotFoundError:
                    supplements_df = pd.DataFrame()
                products          = recommend_products(ingredients, supplements_df.to_dict("records"))

                # 4) GPT 맞춤형 응답
                output = build_structured_data(
                    exam_dict, abnormal, ingredients, products,
                    ing_info_df, msd_manual, user_name
                )
                time.sleep(1.5)

            # ─ 결과 표시 ─
            st.success("✅ 분석 완료! 결과가 준비되었습니다.")
            st.subheader("💡 맞춤형 건강 조언")
            st.markdown(output["gpt_response"])

            with st.expander("🔎 세부 데이터 보기"):
                st.json(output["structured_data"])
            with st.expander("📝 OCR 원문"):
                st.text(ocr_text)

    else:
        st.info("🗂️ 이름·성별·파일을 모두 입력하면 분석 버튼이 활성화됩니다.")

# ────── PAGE: 신체 부위 기반 추천 ────────────────────────
elif st.session_state.page == "신체 부위 기반 추천":
    st.subheader("신체 부위 기반 건강 고민")
    API_BASE = "http://127.0.0.1:8000" 
    TIMEOUT = 90
    body_part = st.radio("신체 부위를 선택하세요", list(body_part_examples.keys()), horizontal=True)
    if body_part:
        st.session_state.selected_body_part = body_part
    default_text = body_part_examples.get(st.session_state.selected_body_part, "")
    user_input = st.text_area(f"{body_part} 관련 건강 고민을 입력하세요", value=default_text)

    if st.button("추천 요청", key="run_bodypart") and user_input:
        with st.spinner(random.choice(loading_messages)):
            if lottie_health:
                st_lottie(lottie_health, height=160)
            time.sleep(1.5)
        try:
            # 3-1) 기능 매칭
            match_res = requests.post(
                f"{API_BASE}/bodypart/bodyfunction/match",
                json={"body_part": body_part, "function": user_input},
                timeout=TIMEOUT
            )
            match_res.raise_for_status()
            matched_fn = match_res.json().get("matched_function", user_input)

            # 3-2) 본 추천
            rec_res = requests.post(
                f"{API_BASE}/bodypart/recommend",
                json={"body_part": body_part, "function": matched_fn},
                timeout=TIMEOUT
            )
            rec_res.raise_for_status()
            data = rec_res.json()

            # 4) 결과 렌더링
            st.success("✅ 추천 결과")
            st.markdown(data.get("recommendation", "결과가 없습니다."))

            # 예시 제품 표
            if data.get("matched_supplements"):
                st.markdown("#### 예시 제품")
                st.dataframe(data["matched_supplements"], use_container_width=True)


        except Exception as e:
            st.error(f"API 호출 실패: {e}")

# ────── PAGE: 연령대 기반 추천 ────────────────────────────
elif st.session_state.page == "연령대 기반 추천":
    st.subheader("연령대 기반 추천")
    age_group = st.selectbox(
        "연령대를 선택하세요",
        ["", "10대 남성", "10대 여성", "20대 남성", "20대 여성", "30대", "40대 남성", "40대 여성", "50대 이상 남성", "50대 이상 여성"]
    )
    age_table_data = {
        "10대 남성": """
| 핵심 3-종 세트 | 섭취 방법 | 주요 기능 요약 | 복용 시 주의·Tip |
|----------------|-----------|----------------|------------------|
| 종근당파워칼슘앤마그네슘<br>종근당 비타민D 1000 IU<br>중외복합오메가3플러스 | ▸ Ca·Mg·D : 1 정 × 2 회, 씹어서<br>▸ D 제피정 : 1 정 × 1 회, 물과 함께<br>▸ Ω-3 : 2 캡슐 × 2 회 | 뼈·치아 형성 & 근·신경 기능, Ca·P 흡수(비타민 D), 혈중 중성지질·혈행 개선 & 항산화(오메가-3 + E) | Ca 와 철 보충제는 2–3 h 이상 간격, Ω-3는 식후 흡수↑ |
""",
    "10대 여성": """
| 핵심 3-종 세트 | 섭취 방법 | 주요 기능 요약 | 복용 시 주의·Tip |
|----------------|-----------|----------------|------------------|
| 멀티플렉스철분앤엽산<br>종근당 비타민D 1000 IU<br>중외복합오메가3플러스 | ▸ 철·엽산 캡슐 : 1 캡슐/일, 공복 ↔ Ca 간격 유지<br>▸ D·Ω-3는 위와 동일 | 철-결핍 예방 & 태아 신경관 발달 대비(엽산), 나머지는 동일 | 6세 이하는 과량 섭취 금지, 공복 섭취 시 속이 불편하면 식후로 |
""",
    "20대 남성": """
| 핵심 3-종 세트 | 섭취 방법 | 주요 기능 요약 | 복용 시 주의·Tip |
|----------------|-----------|----------------|------------------|
| 멀티비타민칼슘<br>종근당 비타민D 1000 IU<br>리셋프로바이오캡 | ▸ Ca 멀티 : 3 정 × 2 회, 씹어서<br>▸ D : 1 정/일<br>▸ 프로바이오 : 1 캡슐/일, 아침 공복 | Ca·K2·B-군·아연 복합 → 골밀도 & 에너지 대사, 유산균 증식·배변 개선 | 프로바이오틱스는 빈속이 흡수율↑ |
""",
    "20대 여성": """
| 핵심 3-종 세트 | 섭취 방법 | 주요 기능 요약 | 복용 시 주의·Tip |
|----------------|-----------|----------------|------------------|
| 멀티플렉스철분앤엽산<br>종근당 비타민D 1000 IU<br>리셋프로바이오캡 | 10대 여성과 동일 | 철 14 mg RNI 충족, 장 건강 | 동일 |
""",
    "30대": """
| 핵심 3-종 세트 | 섭취 방법 | 주요 기능 요약 | 복용 시 주의·Tip |
|----------------|-----------|----------------|------------------|
| 슈퍼바이탈비타민B복합<br>중외복합오메가3플러스<br>비타민D 1200 IU | ▸ B-군 : 2 정/일, 식후<br>▸ Ω-3 : 2 캡 × 2 회<br>▸ D : 1 정/일 | 항산화·피로 회복(B·C·셀레늄), 심혈관 & 눈 건강, Ca-흡수 지원(D) | 카페인 과다 시 B-군 저하 → 오후 복용 권장 |
""",
    "40대 남성": """
| 핵심 3-종 세트 | 섭취 방법 | 주요 기능 요약 | 복용 시 주의·Tip |
|----------------|-----------|----------------|------------------|
| 미슬 코큐텐<br>중외복합오메가3플러스<br>비타민D 1200 IU | ▸ CoQ10 바이알 1 병/일 (흔들어 섭취)<br>▸ 나머지는 위와 동일 | 항산화 & 혈압 관리(CoQ10) + Ω-3·D | 항고혈압제 복용 중이면 의사 상담 |
""",
    "40대 여성": """
| 핵심 3-종 세트 | 섭취 방법 | 주요 기능 요약 | 복용 시 주의·Tip |
|----------------|-----------|----------------|------------------|
| 미슬 코큐텐<br>종근당파워칼슘앤마그네슘<br>중외복합오메가3플러스 | Ca·Mg·D는 오전, CoQ10·Ω-3는 저녁 | 골다공증 전단계 Ca·Mg·D 강화 + 항산화 | Ca 과다(> 2500 mg) 주의 |
""",
        "50대 이상 남성": """
| 핵심 3-종 세트 | 섭취 방법 | 주요 기능 요약 | 복용 시 주의·Tip |
|----------------|-----------|----------------|------------------|
| 중외파워루테인<br>종근당파워칼슘앤마그네슘<br>리셋프로바이오캡 | ▸ 루테인 1 캡/일, 식후<br>▸ Ca·Mg·D : 1 정 × 2 회<br>▸ 프로바이오틱스 : 아침 | 황반색소 유지·눈 건강, 장-Ca 흡수, 골밀도 | 루테인 과다 섭취 시 피부 황색 변할 수 있음 |
""",
        "50대 이상 여성": """
| 핵심 3-종 세트 | 섭취 방법 | 주요 기능 요약 | 복용 시 주의·Tip |
|----------------|-----------|----------------|------------------|
| 중외파워루테인<br>종근당파워칼슘앤마그네슘<br>뉴트리파워 단백질 | ▸ 단백질 파우더 30 g × 3 회, 물/우유와<br>▸ 나머지는 위와 동일 | 근감소·폐경 후 골 소실 예방(단백질+Ca·D), 눈 건강 | 단백질 알레르기 여부 확인 |
"""
    }
    if age_group and age_group in age_table_data:
        st.markdown("#### 추천 정보")
        st.markdown(age_table_data[age_group], unsafe_allow_html=True)

# ────── PAGE: 사용자 설정 ────────────────────────────────
elif st.session_state.page == "사용자 설정":
    st.subheader("건강 문진표 입력")
    API_BASE = "http://127.0.0.1:8000"
    TIMEOUT = 90
    name = st.text_input("이름", key="username_basic")
    gneder = st.radio("성별", ["남성", "여성"], horizontal=True, key="gender_basic")
    birth = st.date_input("생년월일", key="birth_basic")
    family = st.multiselect("가족력", ["고혈압", "당뇨병", "심장병", "암", "기타"], key="family_basic")
    past = st.multiselect("과거 병력", ["간염", "천식", "고지혈증", "우울증", "기타"], key="past_basic")
    allergy = st.multiselect("알러지", ["계란", "우유", "갑각류", "약물", "기타"], key="allergy_basic")
    meds = st.text_area("복용 중인 약물", key="drug_basic")
    smoke = st.radio("흡연 여부", ["비흡연", "과거 흡연", "현재 흡연"], horizontal=True, key="smoke_basic")
    drink = st.radio("음주 여부", ["전혀 안 함", "가끔", "자주"], horizontal=True, key="alcohol_basic")
    sleep = st.slider("하루 평균 수면 시간 (시간)", 0, 12, 7, key="sleep_basic")

    if st.button("저장", key="save_basic"):
        survey = {
            "name":               st.session_state.username_basic,
            "gender":             st.session_state.gender_basic,
            "birth_date":         st.session_state.birth_basic.isoformat(),
            "family_history":     st.session_state.family_basic,
            "past_medical_history": st.session_state.past_basic,
            "allergies":          st.session_state.allergy_basic,
            "current_medications": st.session_state.drug_basic,
            "smoking_status":     st.session_state.smoke_basic,
            "drinking_status":    st.session_state.alcohol_basic,
            "average_sleep_hours": st.session_state.sleep_basic,
        }

        try:
            res = requests.post(f"{API_BASE}/user/survey", json=survey, timeout=TIMEOUT)
            res.raise_for_status()
            st.success("✅ 건강 문진표가 저장되었습니다.")
        except Exception as e:
            st.error(f"문진표 저장 실패: {e}")

# ────── fallback (잘못된 page 값) ──────────────────────────
else:
    st.session_state.page = "intro"
    st.rerun()

# ────── 카드 종료 & footer ───────────────────────────────
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("---")
st.caption("ⓒ 2025 The Wellness Paranoids(TWP) 팀 · 영양제 추천 챗봇  \n실제 의료 상담은 전문가와 상의하세요.")