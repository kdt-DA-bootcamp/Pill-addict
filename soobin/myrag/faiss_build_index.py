"""
faiss_build_index.py
- msd_manual_chunks_clean.json → Document
- OpenAIEmbeddings(model="text-embedding-3-small")
- FAISS 인덱스 생성 & 로컬 저장
python faiss_build_index.py
"""

import os
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

from langchain.schema import Document
# Deprecation 경고 해소용 import 변경
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS


def main():
    load_dotenv()
    logging.basicConfig(level=logging.INFO,
                        format="[%(asctime)s] %(levelname)s: %(message)s")

    api_key = os.getenv("OPENAI_API_KEY","")
    if not api_key:
        logging.error("OPENAI_API_KEY missing in .env")
        return

    # 1) base_dir = soobin/myrag
    BASE_DIR = Path(__file__).resolve().parent
    # => parent => soobin
    DATA_DIR = BASE_DIR.parent / "ragdata"  # soobin/ragdata
    MSD_JSON = DATA_DIR / "msd_manual_chunks_clean.json"

    # 2) Faiss 인덱스 저장할 경로
    FAISS_INDEX_DIR = BASE_DIR / "faiss_index_msd"

    if not MSD_JSON.exists():
        logging.error(f"{MSD_JSON} not found. Cannot proceed.")
        return

    with MSD_JSON.open("r", encoding="utf-8") as f:
        msd_chunks = json.load(f)

    logging.info(f"Loaded {len(msd_chunks)} chunks from {MSD_JSON}")

    docs = []
    for c in msd_chunks:
        text = c.get("content", "").strip()
        if not text:
            continue
        meta = {
            "section": c.get("section", ""),
            "source":  c.get("source", "msd")
        }
        docs.append(Document(page_content=text, metadata=meta))

    logging.info(f"Total {len(docs)} documents after cleaning")

    # 3) OpenAIEmbeddings: text-embedding-3-small 모델
    embeddings = OpenAIEmbeddings(
        openai_api_key=api_key,
        model="text-embedding-3-small"
    )

    # 4) 문서 → 임베딩 → FAISS 인덱스 생성
    db = FAISS.from_documents(docs, embeddings)

    # 5) 인덱스 로컬 저장
    db.save_local(str(FAISS_INDEX_DIR))
    logging.info(f"Faiss index saved to {FAISS_INDEX_DIR}/")

if __name__ == "__main__":
    main()
