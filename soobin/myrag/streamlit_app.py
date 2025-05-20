import streamlit as st
import time
import random
from streamlit_lottie import st_lottie
import json
import requests

st.set_page_config(layout="centered", page_title="건강 챗봇 UI")

# --- Lottie JSON 가져오기 ---
try:
    with open("health_loading.json", "r", encoding="utf-8") as f:
        lottie_health = json.load(f)
except Exception:
    lottie_health = None

# --- 세션 스테이트 초기화 ---
if "page" not in st.session_state:
    st.session_state.page = "intro"
if "selected_body_part" not in st.session_state:
    st.session_state.selected_body_part = ""
if "history" not in st.session_state:
    st.session_state.history = []

# --- 신체 부위별 예시 문구 ---
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

# --- 통일된 버튼 + 레이아웃 ---
st.markdown(
    """
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
    """,
    unsafe_allow_html=True
)

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

# --- 인트로 화면 ---
if st.session_state.page == "intro":
    st.session_state.history.clear()
    st.markdown(
        """
        <div style='text-align: center; margin-top: 5rem;'>
            <h1 style='font-size: 2.8rem;'>당신의 건강을 위하여</h1>
            <p style='font-size: 18px; color: #d1d5db;'>AI 기반 건강 분석 및 맞춤 추천을 받아보세요.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    render_main_buttons()
    st.stop()

# --- 사용자 기본정보 + 홈으로 버튼 ---
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

# --- 이전 버튼 ---
if st.session_state.page != "intro":
    col_a, col_b = st.columns([5, 1])
    with col_b:
        if st.button("이전으로"):
            if st.session_state.history:
                st.session_state.page = st.session_state.history.pop()
            else:
                st.session_state.page = "intro"
            st.rerun()

# --- 중앙 카드 시작 ---
st.markdown(
    """
    <div style='
        max-width: 720px;
        margin: 0 auto;
        padding: 2rem;
        display: flex;
        flex-direction: column;
        align-items: center;
    '>
    """,
    unsafe_allow_html=True
)

# =============================================================================
# 📌 페이지별 로직
# =============================================================================

if st.session_state.page == "신체 부위 기반 추천":
    st.subheader("신체 부위 기반 건강 고민")
    body_part = st.radio("신체 부위를 선택하세요", list(body_part_examples.keys()), horizontal=True)
    if body_part:
        st.session_state.selected_body_part = body_part
    default_text = body_part_examples.get(st.session_state.selected_body_part, "")
    user_input = st.text_area(f"{body_part} 관련 건강 고민을 입력하세요", value=default_text)

    if st.button("추천 요청"):
        with st.spinner(random.choice(loading_messages)):
            if lottie_health:
                st_lottie(lottie_health, height=160)
            else:
                st.warning("🔄 추천 중입니다... (애니메이션 로딩 실패)")
            time.sleep(1.5)

        # 📌 FastAPI 추천 API 연결
        try:
            payload = {
                "exam_info": None,
                "body_part": body_part,
                "symptom": user_input
            }
            # --- 실제 운영 주소로 바꿔주세요! ---
            API_URL = "http://localhost:8000/soobin/recommend"
            res = requests.post(API_URL, json=payload, timeout=30)
            if res.status_code == 200:
                data = res.json()
                st.write("🔎 [API 응답 결과]", data)  # 원본 응답 확인용

                # 결과 렌더링 예시
                answer = data.get("recommendation") or data.get("answer") or data.get("pipeline_data")
                if answer:
                    if isinstance(answer, dict) or isinstance(answer, list):
                        st.json(answer)
                    else:
                        st.markdown(str(answer))
                else:
                    st.error("추천 결과가 비어 있습니다. (answer/pipeline_data 없음)")
            else:
                st.error(f"서버 에러: {res.status_code} {res.text}")
        except Exception as e:
            st.error(f"API 연결 실패: {e}")

elif st.session_state.page == "검진 기반 추천":
    st.subheader("건강검진 기반 추천")
    uploaded_file = st.file_uploader("건강검진 결과 이미지 업로드", type=["jpg", "jpeg", "png", "pdf"])
    if uploaded_file:
        with st.spinner(random.choice(loading_messages)):
            if lottie_health:
                st_lottie(lottie_health, height=160)
            else:
                st.warning("🔄 분석 중입니다... (애니메이션 로딩 실패)")
            time.sleep(3)
        # 🚩 여기도 API 연동 필요

        st.success("✅ 분석 완료! 결과가 준비되었습니다.")

elif st.session_state.page == "연령대 기반 추천":
    st.subheader("연령대 기반 추천")
    age_group = st.selectbox("연령대를 선택하세요", ["", "10대", "20대", "30대", "40대", "50대 이상"])
    if age_group:
        with st.spinner(random.choice(loading_messages)):
            if lottie_health:
                st_lottie(lottie_health, height=160)
            else:
                st.warning("🔄 추천 중입니다... (애니메이션 로딩 실패)")
            time.sleep(2)
        # 🚩 여기도 API 연동 필요

        st.success(f"✅ {age_group} 연령대에 적합한 추천이 완료되었습니다!")

elif st.session_state.page == "사용자 설정":
    st.subheader("건강 문진표 입력")
    st.text_input("이름")
    st.radio("성별", ["남성", "여성"], horizontal=True)
    st.date_input("생년월일")
    st.multiselect("가족력", ["고혈압", "당뇨병", "심장병", "암", "기타"])
    st.multiselect("과거 병력", ["간염", "천식", "고지혈증", "우울증", "기타"])
    st.multiselect("알러지", ["계란", "우유", "갑각류", "약물", "기타"])
    st.text_area("복용 중인 약물")
    st.radio("흡연 여부", ["비흡연", "과거 흡연", "현재 흡연"], horizontal=True)
    st.radio("음주 여부", ["전혀 안 함", "가끔", "자주"], horizontal=True)
    st.slider("하루 평균 수면 시간 (시간)", 0, 12, 7)
    if st.button("저장"):
        # 🚩 TODO: 문진표 정보(이름, 성별 등)를 서버에 전송, DB 저장 or 세션에 유지
        st.success("✅ 건강 문진표가 저장되었습니다!")

else:
    # 🚩 알 수 없는 상태면 intro로 이동
    st.session_state.page = "intro"
    st.rerun()

# --- 카드 종료 ---
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("---")
st.caption("ⓒ 2025 Pill-Addict 팀 · 영양제 추천 챗봇 \n실제 의료 상담은 전문가와 상담하세요.")
