from dotenv import load_dotenv
import os
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl
from pydantic import ConfigDict

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
METADATA_FILE_SUPPLEMENT = os.getenv("METADATA_FILE_SUPPLEMENT")
API_TITLE       = os.getenv("API_TITLE")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
APP_PORT        = os.getenv("APP_PORT")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS")
ROWS_PER_REQ    = os.getenv("ROWS_PER_REQ")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

class Settings(BaseSettings):
    CHROMA_DIR: str
    COLLECTION_NAME: str
    EMBED_MODEL_ID: str

    VECTORS_FILE: str 
    MAPPING_FILE: str 
    METADATA_FILE_BODY: str
    METADATA_FILE_INGREDIENT: str
    METADATA_FILE_ALLERGY: str
    METADATA_FILE_SUPPLEMENT: str

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
