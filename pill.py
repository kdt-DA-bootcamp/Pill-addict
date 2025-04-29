import streamlit as st
import requests

st.set_page_config(layout="centered", page_title="건강 챗봇 UI")

# --- 세션 초기화 ---
if "page" not in st.session_state:
    st.session_state.page = "intro"
if "selected_body_part" not in st.session_state:
    st.session_state.selected_body_part = ""

# --- FastAPI 자리 (예정) ---
def send_image_to_api(image_file): pass
def send_body_part_question(body_part, question): pass
def get_age_recommendation(age_group): pass

# --- 통일된 버튼 스타일 CSS ---
st.markdown("""
    <style>
    div.stButton > button {
        background-color: #6c63ff;
        color: white;
        padding: 14px 20px;
        width: 100%;
        max-width: 320px;
        border: none;
        border-radius: 12px;
        font-size: 16px;
        margin: 10px auto;
        display: block;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        cursor: pointer;
    }
    div.stButton > button:hover {
        background-color: #7c73ff;
    }
    </style>
""", unsafe_allow_html=True)

# --- 공통 버튼 렌더 함수 ---
def render_uniform_button(label: str, target_page: str):
    col = st.columns([3, 3, 3])[1]
    with col:
        if st.button(label, key=label):
            st.session_state.page = target_page

# --- 메인 탭 버튼 묶음 ---
def render_main_buttons():
    render_uniform_button("검진 기반 추천", "검진 기반 추천")
    render_uniform_button("신체 부위 기반 추천", "신체 부위 기반 추천")
    render_uniform_button("연령대 기반 추천", "연령대 기반 추천")

# --- 인트로 화면 ---
if st.session_state.page == "intro":
    st.markdown("""
        <div style='text-align: center; margin-top: 5rem;'>
            <h1 style='font-size: 2.8rem; color: #ffffff;'>당신의 건강을 위하여</h1>
            <p style='color: #cccccc; font-size: 18px;'>AI 기반 건강 분석 및 맞춤 추천을 받아보세요.</p>
        </div>
    """, unsafe_allow_html=True)
    render_main_buttons()
    st.stop()

# --- 사용자 기본정보 버튼 (우측 상단) ---
col_user_btn, _ = st.columns([6, 1])
with col_user_btn:
    if st.button("사용자 기본정보"):
        st.session_state.page = "사용자 설정"

# --- 홈으로 버튼 ---
if st.session_state.page != "intro":
    render_uniform_button("홈으로", "intro")

# --- 중앙 카드 영역 시작 ---
st.markdown("""
    <div style='
        max-width: 720px;
        margin: 0 auto;
        padding: 0rem 2rem 2rem 2rem;
        display: flex;
        flex-direction: column;
        align-items: center;
    '>
""", unsafe_allow_html=True)

# --- 메인 버튼들 (main 상태일 때) ---
if st.session_state.page == "main":
    render_main_buttons()

st.markdown("<hr style='width:100%;'>", unsafe_allow_html=True)

# --- 콘텐츠 렌더링 ---
if st.session_state.page == "검진 기반 추천":
    st.subheader("건강검진 기반 추천")
    uploaded_file = st.file_uploader("건강검진 결과 이미지 업로드", type=["jpg", "jpeg", "png", "pdf"])
    if uploaded_file:
        st.info("이미지를 서버로 전송 중...")

elif st.session_state.page == "신체 부위 기반 추천":
    st.subheader("신체 부위 기반 건강 고민")
    st.image("https://gptonline.ai/media/human_body_sample.png", use_column_width=True, caption="인체 기능별 부위 선택")

    body_part = st.radio(
        "신체 부위를 선택하세요",
        ["신경계", "소화/대사계", "생식/비뇨계", "신체 방어/면역계", "감각계", "심혈관계", "내분비계", "근육계"],
        horizontal=True
    )

    if body_part:
        st.session_state.selected_body_part = body_part

    if st.session_state.selected_body_part:
        user_input = st.text_area(f"{body_part} 관련 건강 고민을 입력하세요")

        if st.button("추천 요청"):
            st.info(f"'{body_part}' 관련 건강 고민을 서버에 전송 중입니다...")

            # [1] FastAPI: 고민 -> 기능 매칭
            BASE_API_URL = "https://5d7d-125-243-42-212.ngrok-free.app"

            match_response = requests.post(
                f"{BASE_API_URL}/bodypart/bodyfunction/match",
                json={
                    "body_part": st.session_state.selected_body_part,
                    "function": user_input
                }
            )

            if match_response.status_code == 200:
                matched_function = match_response.json()["matched_function"]
                st.success(f"선택한 고민과 가장 유사한 기능: {matched_function}")

                recommend_req_data = {
                    "body_part": st.session_state.selected_body_part,
                    "function": matched_function
                }

                # [2] FastAPI: 매칭된 기능 -> 영양제 추천
                response = requests.post(f"{BASE_API_URL}/bodypart/recommend", json=recommend_req_data)

                top_n = 5  # 최대 추천 수를 우선 5개로 설정. 추후 기준 선정 필요.

                if response.status_code == 200:
                    supplements = response.json()
                    if not supplements:
                        st.warning("죄송합니다. 현재 입력하신 고민에 적합한 추천 제품이 없습니다.")
                    else:
                        st.success(f"당신을 위한 추천 제품 {min(len(supplements), top_n)}개를 소개할게요!")

                        for supplement in supplements[:top_n]:
                            st.markdown(f"""
                                <div style="border:1px solid #ddd; border-radius:10px; padding:10px; margin:10px 0;">
                                    <b>제품명:</b> {supplement['product_name']}<br>
                                    <b>주요 기능:</b> {supplement['primary_function'] or '정보 없음'}<br>
                                    <b>섭취 주의사항:</b> {supplement.get('caution', '특이사항 없음')}
                                </div>
                            """, unsafe_allow_html=True)
            else:
                st.error("서버 오류가 발생했습니다. 다시 시도해주세요.")
           

elif st.session_state.page == "연령대 기반 추천":
    st.subheader("연령대 기반 추천")
    age_group = st.selectbox("연령대를 선택하세요", ["", "10대", "20대", "30대", "40대", "50대 이상"])
    if age_group:
        st.info("연령대 전송 중...")

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

# --- 카드 종료 ---
st.markdown("</div>", unsafe_allow_html=True)

# --- 하단 안내 ---
st.markdown("---")
st.caption("영양제 추천 해드려요")