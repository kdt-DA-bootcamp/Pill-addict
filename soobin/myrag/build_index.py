# build_index.py (MSD 청크 → Chroma 인덱스)
"""
MSD 매뉴얼 청크(JSON) → Chroma 벡터 인덱스 생성 스크립트
python -m soobin.myrag.build_index
"""
from __future__ import annotations
import os, json, logging
from pathlib import Path
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from dotenv import load_dotenv

# --------------------------------------------------------------------- #
BASE_DIR  = Path(__file__).resolve().parent.parent      # .../soobin
DATA_DIR  = BASE_DIR / "ragdata"
PERSIST_DIR = BASE_DIR / "msd_chroma_db"
MSD_JSON_PATH = DATA_DIR / "msd_manual_chunks_clean.json"
# --------------------------------------------------------------------- #

load_dotenv()
logging.basicConfig(level=logging.INFO,
                    format="[%(asctime)s] %(levelname)s: %(message)s")

def load_chunks(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"{path} not found.")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def build_index(chunks: list[dict], persist_dir: Path,
                openai_api_key: str) -> Chroma:
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    docs = [
        Document(
            page_content=c["content"],
            metadata={"section": c["section"], "source": c["source"]},
        ) for c in chunks
    ]
    vectordb = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=str(persist_dir),
    )
    vectordb.persist()        # Chroma 0.4.x 이후 자동-persist 이지만 호환 차원
    return vectordb

def main() -> None:
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        logging.error("OPENAI_API_KEY env var not set.")
        return

    chunks = load_chunks(MSD_JSON_PATH)
    logging.info("Loaded %d chunks from %s", len(chunks), MSD_JSON_PATH)

    db = build_index(chunks, PERSIST_DIR, api_key)
    logging.info("Indexed %d documents into %s", db._collection.count(),
                 PERSIST_DIR)

if __name__ == "__main__":
    main()