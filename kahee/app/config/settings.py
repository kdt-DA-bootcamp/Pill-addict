## .env 파일 설정 적용 및 전체 코드 변수 설정

# 라이브러리 모음 
from dotenv import load_dotenv
import os
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl
from pydantic import ConfigDict
from pathlib import Path 


# .env 파일 로드 및 환경 구분
load_dotenv()
ENV = os.getenv("APP_ENV", "dev")


# 공통 환경변수 지정
# DB 관련
CHROMA_DIR = os.getenv("CHROMA_DIR")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
EMBED_MODEL_ID  = os.getenv("EMBED_MODEL_ID") 
#데이터 관련
METADATA_FILE_BODY = os.getenv("METADATA_FILE_BODY")
METADATA_FILE_INGREDIENT = os.getenv("METADATA_FILE_INGREDIENT")
METADATA_FILE_ALLERGY = os.getenv("METADATA_FILE_ALLERGY")
METADATA_FILE_SUPPLEMENT = os.getenv("METADATA_FILE_SUPPLEMENT")
#FastAPI 관련
API_TITLE = os.getenv("API_TITLE")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
APP_PORT = os.getenv("APP_PORT")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS")
ROWS_PER_REQ = os.getenv("ROWS_PER_REQ")


# 기본 경로 설정
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
CHROMA_DIR = Path(os.getenv("CHROMA_DIR", BASE_DIR / "chroma_db")).as_posix()


class Settings(BaseSettings):
    #DB 관련
    CHROMA_DIR: str
    COLLECTION_NAME: str
    EMBED_MODEL_ID: str

    #데이터 관련
    VECTORS_FILE: str 
    MAPPING_FILE: str 
    METADATA_FILE_BODY: str
    METADATA_FILE_INGREDIENT: str
    METADATA_FILE_ALLERGY: str
    METADATA_FILE_SUPPLEMENT: str

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


    @property
    def abs_mapping_file(self):
        return os.path.join(DATA_DIR, self.MAPPING_FILE)

    @property
    def abs_vectors_file(self):
        return os.path.join(DATA_DIR, self.VECTORS_FILE)

    @property
    def abs_metadata_body(self):
        return os.path.join(DATA_DIR, self.METADATA_FILE_BODY)

    @property
    def abs_metadata_ingredient(self):
        return os.path.join(DATA_DIR, self.METADATA_FILE_INGREDIENT)

    @property
    def abs_metadata_allergy(self):
        return os.path.join(DATA_DIR, self.METADATA_FILE_ALLERGY)
    
    @property
    def abs_metadata_supplement(self):
        return os.path.join(DATA_DIR, self.METADATA_FILE_SUPPLEMENT)

settings = Settings()