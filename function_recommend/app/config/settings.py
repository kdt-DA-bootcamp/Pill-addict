## .env 파일 설정 적용 및 전체 코드 변수 설정

# .env 파일 설정 적용 및 전체 코드 변수 설정

from dotenv import load_dotenv
import os
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl
from pathlib import Path

# .env 파일 로드
BASE_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = BASE_DIR / ".env"

print("📌 .env 경로 확인:", ENV_PATH)
load_dotenv(dotenv_path=ENV_PATH)

class Settings(BaseSettings):
    # FastAPI 관련 설정
    APP_PORT: int = int(os.getenv("APP_PORT", 8000))
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "*")
    ROWS_PER_REQ: int = int(os.getenv("ROWS_PER_REQ", 10))
    APP_ENV: str = os.getenv("APP_ENV", "local")
    API_TITLE: str = os.getenv("API_TITLE", "My API")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    FASTAPI_URL: str = os.getenv("FASTAPI_URL", "")
    api_url: AnyHttpUrl = os.getenv("FASTAPI_URL", "http://localhost:8000")

settings = Settings()

print("✅ OPENAI_API_KEY =", os.getenv("OPENAI_API_KEY"))