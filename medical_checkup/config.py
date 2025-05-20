#pill-addict/medical_checkup/config
import os
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME     = os.getenv("MODEL_NAME", "gpt-4o")

# ✅ 경로 변수: 파이프라인에서 쓰는 이름으로 통일
REFERENCE_TABLE_PATH   = os.getenv("REFERENCE_TABLE_PATH",
                                   "database/[별표4]일반건강검진판정기준.pdf")

SUPPLEMENT_DATA_PATH = os.getenv("SUPPLEMENT_DATA_PATH")
INGREDIENT_JSON_PATH = os.getenv("INGREDIENT_JSON_PATH")

MSD_MANUAL_JSON_PATH   = os.getenv("MSD_MANUAL_JSON_PATH",
                                   "database/msd_manual_chunks_clean.json")

LOG_LEVEL              = os.getenv("LOG_LEVEL", "INFO")
OCR_ENGINE_PATH        = os.getenv("OCR_ENGINE_PATH", "/usr/local/bin/tesseract")

# (필요 시 그대로 유지)
S3_BUCKET              = os.getenv("S3_BUCKET", "")
S3_KEY                 = os.getenv("S3_KEY", "")
AWS_ACCESS_KEY_ID      = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY  = os.getenv("AWS_SECRET_ACCESS_KEY", "")
API_TIMEOUT_SECONDS    = int(os.getenv("API_TIMEOUT_SECONDS", "30"))
RETRY_COUNT            = int(os.getenv("RETRY_COUNT", "3"))
