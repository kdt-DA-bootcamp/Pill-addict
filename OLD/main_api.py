from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import tempfile
from healthcheck_parser import run_healthcheck_pipeline

app = FastAPI()

# 🚨 CORS 허용 (Streamlit이 다른 포트일 경우 필요)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 특정 도메인으로 제한 가능
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    suffix = "." + file.filename.split(".")[-1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    result = run_healthcheck_pipeline(tmp_path)
    return result
