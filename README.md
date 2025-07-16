# 🩺 건강검진 기반 영양제 추천 챗봇

개인 건강검진 데이터를 기반으로 맞춤형 영양제를 추천해주는 AI 챗봇입니다. OCR로 검진표를 인식하고, 검진 수치에 따라 필요한 영양제를 제안하는 기능을 제공합니다.

---

## 📌 프로젝트 개요

- **목표:** 건강검진표의 주요 지표를 바탕으로 사용자의 건강 상태를 분석하고, 부족한 영양소를 보충할 수 있는 영양제를 추천
- **주요 기능:**
  - **OCR 인식:** 건강검진표 이미지에서 텍스트 추출
  - **데이터 파싱:** 검진 수치 및 이상 여부 자동 판별
  - **질병/지표별 영양제 매핑:** 특정 수치에 따른 영양제 추천 로직
  - **챗봇 인터페이스:** Streamlit을 통한 UI 제공
  - **RAG 기반 추천:** Vector DB와 LLM을 결합한 심화 질의 응답 지원

---

## 🛠️ 기술 스택

- **Backend:** FastAPI
- **Frontend:** Streamlit
- **OCR:** Tesseract, AWS Textract
- **Vector DB:** FAISS, Weaviate
- **LLM:** OpenAI GPT API
- **Deployment:** AWS EC2, Docker

---

## ⚙️ 담당 역할 (by 지민성)

- **Streamlit 프론트엔드 개발**
  - OCR 이미지 업로드 및 FastAPI 연동
  - 챗봇 UI 기획 및 인터페이스 전반 개발
- **FastAPI 서버 구축**
  - OCR 결과를 처리하는 API 설계
  - 추천 결과 반환 API 구성
- **OCR 통합**
  - AWS Textract와 Tesseract 기반 OCR 비교 적용
  - OCR 결과 데이터 파싱 및 이상 수치 판별 로직 초안 설계
- **영양제 추천 로직 기획**
  - 검진 지표 이상 수치 기반 영양제 추천 기준 초안 정의
- **RAG 아키텍처 구성**
  - FAISS와 OpenAI API를 이용한 Vector DB + GPT 조합 설계 및 테스트
- **AWS EC2 인프라 구성**
  - FastAPI, OCR, LLM 통합 서버 구축
  - 서버 배포 및 운영

---

## 📊 데이터 처리 흐름

`건강검진표 업로드 → OCR → 데이터 파싱 및 이상 수치 판별 → 영양제 추천 → 챗봇 응답`

---

## 🧩 향후 개선 방향

- OCR 정확도 향상 및 자동화
- 개인 맞춤형 추천 고도화 (성별, 나이, 복용 약물 고려)
- 챗봇 UX 고도화
- Vector DB를 활용한 검색 정확도 개선

---
email : abwm2020@naver.com 
