"""
streamlit_app.py
Streamlit UI
 - JSON 노출 제거
 - 동일 (신체 부위 라디오, text_area)
"""

import os
import requests
import streamlit as st

# FastAPI URL
API_URL = os.getenv("RECO_API", "http://127.0.0.1:8000/recommend")

st.set_page_config(layout="centered", page_title="건강 챗봇 UI")

if "page" not in st.session_state:
    st.session_state.page = "intro"
if "history" not in st.session_state:
    st.session_state.history = []
if "selected_body_part" not in st.session_state:
    st.session_state.selected_body_part = ""

# 신체 부위 예시
body_part_examples = {
    "신경계":     "기억력 저하, 긴장, 수면의 질, 피로",
    "소화/대사계":"위, 간, 장, 체지방, 칼슘흡수",
    "생식/비뇨계": "전립선, 배뇨, 요로",
    "신체 방어/면역계": "면역, 항산화",
    "감각계":     "눈, 치아, 피부",
    "심혈관계":   "혈압, 콜레스테롤, 혈행",
    "내분비계":   "혈당, 갱년기, 월경 불순",
    "근육계":     "관절, 근력, 뼈",
}

# CSS
st.markdown("""
<style>
html, body, [class*="css"] {
  font-family: 'Segoe UI', sans-serif;
  background-color: #111827;
  color: #ffffff;
}
.main .block-container {
  max-width: 900px;
  margin: auto;
  padding: 2rem 2rem 3rem;
  background: #1f2937;
  border-radius: 18px;
  box-shadow: 0 0 10px rgba(255,255,255,0.05);
}
div.stButton>button {
  background: linear-gradient(135deg,#6366f1,#8b5cf6);
  color: #fff;
  width: 100%;
  max-width: 320px;
  padding: 14px 20px;
  margin: 10px auto;
  border: none;
  border-radius: 14px;
  font-size: 16px;
  font-weight: bold;
  box-shadow: 0 6px 18px rgba(0,0,0,0.3);
  transition: 0.2s;
}
div.stButton>button:hover {
  background: linear-gradient(135deg,#7c3aed,#a78bfa);
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(0,0,0,0.4);
}
.stCaption{ color: #9ca3af; }
</style>
""", unsafe_allow_html=True)

def nav_button(label: str, target: str):
    col = st.columns([3,3,3])[1]
    with col:
        if st.button(label, key=label):
            st.session_state.history.append(st.session_state.page)
            st.session_state.page = target
            st.rerun()

def render_main_buttons():
    nav_button("검진 기반 추천", "검진 기반 추천")
    nav_button("신체 부위 기반 추천","신체 부위 기반 추천")
    nav_button("연령대 기반 추천", "연령대 기반 추천")

# 인트로
if st.session_state.page == "intro":
    st.session_state.history.clear()
    st.markdown("""
    <div style='text-align:center;margin-top:5rem;'>
      <h1 style='font-size:2.8rem;'>당신의 건강을 위하여</h1>
      <p style='font-size:18px;color:#d1d5db;'>AI 기반 건강 분석 및 맞춤 추천</p>
    </div>
    """, unsafe_allow_html=True)
    render_main_buttons()
    st.stop()

col1, col2, col3 = st.columns([3,3,4])
with col1:
    if st.button("사용자 기본정보"):
        pass
with col2:
    if st.session_state.page != "intro" and st.button("홈으로"):
        st.session_state.page = "intro"
        st.rerun()

# 이전으로
if st.session_state.page != "intro":
    col_a, col_b = st.columns([5,1])
    with col_b:
        if st.button("이전으로"):
            st.session_state.page = (
                st.session_state.history.pop() if st.session_state.history else "intro"
            )
            st.rerun()

st.markdown("<div style='max-width:720px;margin:0 auto;'>", unsafe_allow_html=True)

if st.session_state.page == "검진 기반 추천":
    st.subheader("건강검진 기반 추천 ")
    st.file_uploader("건강검진 결과 이미지 업로드", type=["jpg","jpeg","png","pdf"])
    st.info("🔧 OCR 파이프라인과 연결 예정")

elif st.session_state.page == "신체 부위 기반 추천":
    st.subheader("신체 부위 기반 건강 고민")
    body_part = st.radio("신체 부위를 선택하세요",
                         list(body_part_examples.keys()),
                         horizontal=True)
    st.session_state.selected_body_part = body_part
    default_text = body_part_examples[body_part]
    user_input = st.text_area(f"{body_part} 관련 고민", value=default_text)

    if st.button("추천 요청"):
        with st.spinner("서버에 질문 전송 중..."):
            payload = {
                "exam_info": None,
                "body_part": body_part,
                "symptom":   user_input.strip()
            }
            try:
                res = requests.post(API_URL, json=payload, timeout=60)
                if res.status_code != 200:
                    st.error(f"❌ 서버 오류: {res.status_code}\n{res.text}")
                else:
                    data = res.json()
                    if "error" in data:
                        st.error(data["error"])
                    else:
                        answer_md = data.get("answer") or data.get("result") or "❌ 응답없음"
                        st.markdown(answer_md, unsafe_allow_html=True)

                    # JSON 노출 X (주석 처리):
                    # with st.expander("세부 JSON"):
                    #     st.json(data, expanded=False)

            except requests.exceptions.RequestException as e:
                st.error(f"요청 실패: {e}")

elif st.session_state.page == "연령대 기반 추천":
    st.subheader("연령대 기반 추천 (데모)")
    age_group = st.selectbox("연령대", ["","10대","20대","30대","40대","50대+"])
    st.info("🔧 연령대별 통계 DB와 연결 예정")

elif st.session_state.page == "사용자 설정":
    st.subheader("건강 문진표 입력 (데모)")
    st.text_input("이름")
    st.radio("성별", ["남성","여성"], horizontal=True)
    st.date_input("생년월일")
    st.multiselect("가족력", ["고혈압","당뇨","심장병","암","기타"])
    st.text_area("복용 중인 약물")

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("---")
st.caption("ⓒ 2025 Pill-Addict 팀 · 영양제 추천 챗봇 \n실제 의료 상담은 전문가와 상담하세요.")
