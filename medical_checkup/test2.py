import streamlit as st
import time
import random
import json
import pandas as pd
from streamlit_lottie import st_lottie

# ────── 📦 PILL-ADDICT PIPELINE ──────────────────────────────
# 같은 프로젝트 폴더 안에 있는 pipeline.py 를 그대로 import
from pipeline import (
    parse_health_exam, load_reference, find_abnormal,
    get_ingredients_from_abnormal_tuple, load_ingredient_info,
    load_msd_manual, recommend_products, build_structured_data
)
# ▸ pipeline.py 가 다른 디렉터리에 있으면 PYTHONPATH 추가 or sys.path 수정 필요
# ─────────────────────────────────────────────────────────────

st.set_page_config(layout="centered", page_title="건강 챗봇 UI")

# ────── Lottie JSON 로드 ────────────────────────────────────
try:
    with open("health_loading.json", "r", encoding="utf-8") as f:
        lottie_health = json.load(f)
except Exception:
    lottie_health = None

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

# ────── 글로벌 CSS ─────────────────────────────────────────
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: 'Segoe UI', sans-serif;
    background-color: #111827;
    color: #ffffff;
}
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 900px;
    margin: auto;
    background-color: #1f2937;
    border-radius: 18px;
    padding-left: 2rem;
    padding-right: 2rem;
    box-shadow: 0 0 10px rgba(255, 255, 255, 0.05);
}
div.stButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
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
    box-shadow: 0 6px 18px rgba(0,0,0,0.3);
    transition: all 0.2s ease-in-out;
}
div.stButton > button:hover {
    background: linear-gradient(135deg, #7c3aed, #a78bfa);
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(0,0,0,0.4);
}
.stCaption {
    color: #9ca3af;
}
</style>
""", unsafe_allow_html=True)

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
    body_part = st.radio("신체 부위를 선택하세요", list(body_part_examples.keys()), horizontal=True)
    if body_part:
        st.session_state.selected_body_part = body_part
    default_text = body_part_examples.get(st.session_state.selected_body_part, "")
    user_input = st.text_area(f"{body_part} 관련 건강 고민을 입력하세요", value=default_text)

    if st.button("추천 요청", key="run_bodypart") and user_input:
        with st.spinner(random.choice(loading_messages)):
            if lottie_health:
                st_lottie(lottie_health, height=160)
            # TODO: pipeline이 아닌 LLM 프롬프트만 호출 → 이후 연결
            time.sleep(2)
        st.success(f"✅ '{body_part}' 관련 추천이 완료되었습니다! (샘플)")

# ────── PAGE: 연령대 기반 추천 ────────────────────────────
elif st.session_state.page == "연령대 기반 추천":
    st.subheader("연령대 기반 추천")
    age_group = st.selectbox("연령대를 선택하세요", ["", "10대", "20대", "30대", "40대", "50대 이상"], key="age_group")

    if st.button("추천 요청", key="run_age") and age_group:
        with st.spinner(random.choice(loading_messages)):
            if lottie_health:
                st_lottie(lottie_health, height=160)
            # TODO: 나이 기반 LLM 호출 후 결과 출력
            time.sleep(2)
        st.success(f"✅ {age_group} 연령대에 적합한 추천이 완료되었습니다! (샘플)")

# ────── PAGE: 사용자 설정 ────────────────────────────────
elif st.session_state.page == "사용자 설정":
    st.subheader("건강 문진표 입력")
    st.text_input("이름", key="username_basic")
    st.radio("성별", ["남성", "여성"], horizontal=True, key="gender_basic")
    st.date_input("생년월일", key="birth_basic")
    st.multiselect("가족력", ["고혈압", "당뇨병", "심장병", "암", "기타"], key="family_basic")
    st.multiselect("과거 병력", ["간염", "천식", "고지혈증", "우울증", "기타"], key="past_basic")
    st.multiselect("알러지", ["계란", "우유", "갑각류", "약물", "기타"], key="allergy_basic")
    st.text_area("복용 중인 약물", key="drug_basic")
    st.radio("흡연 여부", ["비흡연", "과거 흡연", "현재 흡연"], horizontal=True, key="smoke_basic")
    st.radio("음주 여부", ["전혀 안 함", "가끔", "자주"], horizontal=True, key="alcohol_basic")
    st.slider("하루 평균 수면 시간 (시간)", 0, 12, 7, key="sleep_basic")

    if st.button("저장", key="save_basic"):
        st.success("✅ 건강 문진표가 저장되었습니다.")

# ────── fallback (잘못된 page 값) ──────────────────────────
else:
    st.session_state.page = "intro"
    st.rerun()

# ────── 카드 종료 & footer ───────────────────────────────
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("---")
st.caption("ⓒ 2025 Pill-Addict 팀 · 영양제 추천 챗봇  |  실제 의료 상담은 전문가와 상의하세요.")