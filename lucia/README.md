# Pill-addict
# 🩺 Health Check Analyzer API (FastAPI)

건강검진 결과지를 업로드하면, OCR 및 기준표를 기반으로 항목을 추출하고  
비정상 수치를 자동으로 판별해주는 API입니다. PDF 및 이미지 파일(jpg, png) 모두 지원합니다.

---
(필요한 패키지)
pdfplumber
pytesseract
opencv-python
python-dotenv
Pillow

---

## 🚀 설치 및 실행 방법

### 1️⃣ 가상환경 설정 (선택)

```bash
python3 -m venv venv   
source venv/bin/activate
