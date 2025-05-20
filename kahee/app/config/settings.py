# pill-addict/kahee/app/config/settings.py
from dotenv import load_dotenv
import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from pathlib import Path

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]  # == pill-addict/kahee/app

DATA_DIR = BASE_DIR / "data"


class Settings(BaseSettings):
    API_TITLE: str = "RAG Server"
    OPENAI_API_KEY: str = ""
    APP_PORT: int = 8000
    ALLOWED_ORIGINS: str = "*"

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()
