import json
from app.config.settings import settings

def load_body_function_options() -> list[dict]:
    with open(settings.abs_mapping_file, encoding="utf-8") as f:
        return json.load(f)

def fetch_functions_by_body(body_part: str) -> list[str]:
    for row in load_body_function_options():
        if row["body"] == body_part:
            return [fn.strip() for fn in row["function"].split(",")]
    return []