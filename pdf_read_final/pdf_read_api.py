from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from analyzer import run_healthcheck_pipeline
from io import BytesIO  

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "건강검진 분석 API입니다. PDF 파일을 업로드하세요."}

@app.post("/analyze/")
async def analyze(file: UploadFile = File(...)):
    contents = await file.read()
    try:
        result = run_healthcheck_pipeline(file_obj=BytesIO(contents))
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
