## 메타데이터 관련 설정

# 라이브러리 모음
from pathlib import Path
import json, os

# 1. 경로 설정
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
VECTOR_FILE = Path(os.getenv("VECTORS_FILE",  DATA_DIR / "vectorized_data.json"))
SUPP_FILE   = Path(os.getenv("SUPPLEMENT_FILE", DATA_DIR / "supplement.json"))

# 2. 파일 로드
def _load(fp: Path):
    if not fp.exists():
        raise FileNotFoundError(fp)
    with fp.open(encoding="utf-8") as f:
        return json.load(f)

vector_rows = _load(VECTOR_FILE)
supp_rows = _load(SUPP_FILE)

# 3. 보조 인덱스 설정
supp_index = {
    str(r["PRDLST_REPORT_NO"]): r
    for r in supp_rows
    if "PRDLST_REPORT_NO" in r
}

print(f"vectors {len(vector_rows)} · metatable {len(supp_index)} loaded")

metadata_supplement = list(supp_index.values())
