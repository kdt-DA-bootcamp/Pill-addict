## .env 파일 설정 적용 및 전체 코드 변수 설정

# 라이브러리 모음 
from dotenv import load_dotenv
import os
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl
from pydantic import ConfigDict
from pathlib import Path 

# .env 파일 로드
load_dotenv()

# 기본 경로 설정
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

class Settings(BaseSettings):
    #FastAPI 관련
    APP_PORT: int
    ALLOWED_ORIGINS: str
    ROWS_PER_REQ: int
    APP_ENV: str
    API_TITLE: str
    OPENAI_API_KEY: str
    FASTAPI_URL: str | None = None
    api_url: AnyHttpUrl

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()