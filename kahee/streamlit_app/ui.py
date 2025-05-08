import streamlit as st
import os, requests, json, streamlit as st
from dotenv import load_dotenv
load_dotenv()

API_BASE = os.getenv("FASTAPI_URL", "http://localhost:8000")
API_URL = (os.getenv("FASTAPI_URL")
    or "http://localhost:8000"
)

st.set_page_config(layout="centered", page_title="건강 챗봇 UI")

@st.cache_data(show_spinner=False)
def get_bodypart_options() -> dict[str,list[str]]:
    res = requests.get(f"{API_BASE}/bodypart/options", timeout=15)
    res.raise_for_status()
    return res.json().get("options", {})


@st.cache_data
def match_function(body_part: str, user_input: str) -> str | None:
    payload = {"body_part": body_part, "function": user_input}
    res = requests.post(f"{API_BASE}/bodypart/bodyfunction/match",
                        json=payload, timeout=15)
    if not res.ok:
        return None
    return res.json().get("matched_function")

def get_recommendation(body_part: str, best_func: str) -> dict:
    url = f"{API_BASE}/bodypart/recommend"
    payload = {"body_part": body_part, "function": best_func}
    print("🔎 추천 API 호출 URL:", url)
    print("🔎 추천 API payload:", payload)
    res = requests.post(url, json=payload)
    return res.json()        # {"recommendation": ..., "context": [...]}

# --- 세션 초기화 ---
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

# --- 통일된 버튼 스타일 + 레이아웃 수정 ---
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

# --- 공통 버튼 렌더 함수 ---
def render_uniform_button(label: str, target_page: str):
    col = st.columns([3, 3, 3])[1]
    with col:
        if st.button(label, key=label):
            st.session_state.history.append(st.session_state.page)
            st.session_state.page = target_page
            st.rerun()

# --- 메인 탭 버튼 묶음 ---
def render_main_buttons():
    render_uniform_button("검진 기반 추천", "검진 기반 추천")
    render_uniform_button("신체 부위 기반 추천", "신체 부위 기반 추천")
    render_uniform_button("연령대 기반 추천", "연령대 기반 추천")

# --- 인트로 화면 ---
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

# --- 사용자 기본정보 + 홈으로 버튼 (한 줄 정렬) ---
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

# --- 이전 버튼은 우측 정렬 (유지) ---
if st.session_state.page != "intro":
    col_a, col_b = st.columns([5, 1])
    with col_b:
        if st.button("이전으로"):
            if st.session_state.history:
                st.session_state.page = st.session_state.history.pop()
            else:
                st.session_state.page = "intro"
            st.rerun()

# --- 중앙 카드 영역 시작 ---
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

# --- 콘텐츠 렌더링 ---
if st.session_state.page == "검진 기반 추천":
    st.subheader("건강검진 기반 추천")
    uploaded_file = st.file_uploader("건강검진 결과 이미지 업로드", type=["jpg", "jpeg", "png", "pdf"])
    if uploaded_file:
        st.info("이미지를 서버로 전송 중...")

elif st.session_state.page == "신체 부위 기반 추천":
    st.subheader("신체 부위 기반 건강 고민")

    # 1) 백엔드에서 실제 부위‑기능 옵션 가져오기
    try:
        options = get_bodypart_options()
    except Exception as e:
        st.error(f"서버에 연결할 수 없습니다: {e}")
        st.stop()

    body_part = st.radio(
        "신체 부위를 선택하세요",
        list(options.keys()),
        horizontal=True
    )

    # 자동 예시 문구
    default_text = ", ".join(options.get(body_part, []))
    user_input = st.text_area(
        f"{body_part} 관련 건강 고민을 입력하세요",
        value=default_text,
        key="bodypart_textarea",
    )

    if st.button("추천 요청"):
        with st.spinner("서버에 요청 중…"):
            # 2) 유사 기능 매칭
            best_func = match_function(body_part, user_input)
            if not best_func:
                st.warning("유사한 기능을 찾지 못했습니다.")
                st.stop()

            # 3) RAG 추천
            result = get_recommendation(body_part, best_func)

        st.success("추천 결과")
        st.markdown(f"**매칭된 기능** : `{best_func}`")
        st.markdown("### AI 추천")
        st.write(result["recommendation"])

        with st.expander("🔍 근거로 사용된 문맥 보기"):
            for ctx in result["context"]:
                st.markdown(f"- {ctx}")


elif st.session_state.page == "연령대 기반 추천":
    st.subheader("연령대 기반 추천")
    age_group = st.selectbox("연령대를 선택하세요", ["", "10대", "20대", "30대", "40대", "50대 이상"])
    if age_group:
        st.info(f"{age_group} 연령대 정보가 전송됩니다...")

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
        st.success("✅ 건강 문진표가 저장되었습니다.")

else:
    st.session_state.page = "intro"
    st.rerun()

# --- 카드 종료 및 하단 ---
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("---")
st.caption("영양제 추천 해드려요")