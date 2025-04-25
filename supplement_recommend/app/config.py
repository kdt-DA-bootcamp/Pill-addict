from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    # DB 설정
    db_url: str = "mysql+pymysql://USER:PASSWORD@localhost:3306/supplement_db" 

    # App options
    app_port: int = 8000
    allowed_origins: str = "http://localhost:8501"
    rows_per_req: int = 1000
    openai_api_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow" )
    

@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
