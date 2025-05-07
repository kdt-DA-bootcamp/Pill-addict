import json, os
from app.config.settings import settings

def load_body_function_options() -> list[dict]:
    """몸 부위‑기능 매핑 옵션 로드"""
    with open(settings.abs_metadata_file_body, encoding="utf‑8") as f:
        return json.load(f)

def fetch_functions_by_body(body_part: str) -> list[str]:
    """특정 부위에 해당하는 기능 목록 반환"""
    whole = load_body_function_options()
    return [row["function"] for row in whole if row["body_part"] == body_part] 
