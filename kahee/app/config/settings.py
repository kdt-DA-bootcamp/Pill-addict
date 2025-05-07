from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

# 환경 구분
ENV = os.getenv("APP_ENV", "dev")

# 공통 환경변수 지정
CHROMA_DIR      = os.getenv("CHROMA_DIR")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
EMBED_MODEL_ID  = os.getenv("EMBED_MODEL_ID")
METADATA_FILE   = os.getenv("METADATA_FILE")
METADATA_DB     = os.getenv("METADATA_DB")
API_TITLE       = os.getenv("API_TITLE")
