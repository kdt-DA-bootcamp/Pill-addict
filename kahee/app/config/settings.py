from dotenv import load_dotenv
import os
from pydantic_settings import BaseSettings

# .env 파일 로드
load_dotenv()

# 환경 구분
ENV = os.getenv("APP_ENV", "dev")

# 공통 환경변수 지정
CHROMA_DIR      = os.getenv("CHROMA_DIR")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
EMBED_MODEL_ID  = os.getenv("EMBED_MODEL_ID") 
METADATA_FILE_BODY        = os.getenv("METADATA_FILE_BODY")
METADATA_FILE_INGREDIENT  = os.getenv("METADATA_FILE_INGREDIENT")
METADATA_FILE_ALLERGY     = os.getenv("METADATA_FILE_ALLERGY")
API_TITLE       = os.getenv("API_TITLE")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
APP_PORT        = os.getenv("APP_PORT")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS")
ROWS_PER_REQ    = os.getenv("ROWS_PER_REQ")



class Settings(BaseSettings):
    CHROMA_DIR: str
    COLLECTION_NAME: str
    EMBED_MODEL_ID: str
    METADATA_FILE_BODY: str
    METADATA_FILE_INGREDIENT: str
    METADATA_FILE_ALLERGY: str
    APP_PORT: int
    ALLOWED_ORIGINS: str
    ROWS_PER_REQ: int
    APP_ENV: str
    API_TITLE: str
    OPENAI_API_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()
