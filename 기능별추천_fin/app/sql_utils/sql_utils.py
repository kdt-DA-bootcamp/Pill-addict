## 메타데이터 파일 필터링용 SQL 로직 정리  

# 라이브러리 및 설정 가져오기
import json
from app.config.settings import settings
from app.config.settings import BASE_DIR

# 주요 로직
def load_body_function_options() -> list[dict]:
    with open(BASE_DIR / "data" / "body_function.json", encoding="utf-8") as f:
        return json.load(f)


def fetch_functions_by_body(body_part: str) -> list[str]:
    for row in load_body_function_options():
        if row["body"] == body_part:
            return [fn.strip() for fn in row["function"].split(",")]
    return []