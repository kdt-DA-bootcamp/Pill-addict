#!/usr/bin/env python3
import json
import re
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 1) 파일 경로 설정
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE  = os.path.join(BASE_DIR, "msd_multi_pages.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "msd_manual_chunks_clean.json")

# 2) JSON 로드
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    pages = json.load(f)

# 3) 불필요 텍스트 제거 함수
REMOVE_PATTERNS = [
    r"honeypot link",
    r"skip to main content",
    r"주제 참고 자료.*",
    r"Copyright\s*©\s*\d{4}.*All rights reserved\.",
]
def clean_text(text: str) -> str:
    for pat in REMOVE_PATTERNS:
        text = re.sub(pat, "", text)
    text = re.sub(r"작성자:\n.*\n검토/개정일.*\n\|\s*수정.*\n", "", text)
    # 연속 공백 줄바꿈은 하나로
    text = re.sub(r"\n\s*\n+", "\n", text)
    return text.strip()

# 4) LangChain RecursiveCharacterTextSplitter 설정
splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100,
    separators=["\n\n", "\n", ".", " ", ""]
)

documents = []
seen = set()

for page in pages:
    url  = page.get("url", "")
    text = clean_text(page.get("extracted_text", ""))
    lines = text.splitlines()

    # 5) TOC에서 섹션 제목만 추출
    toc_idx = None
    for i, line in enumerate(lines):
        if line.strip() == "이 장에서 다루는 다른 주제":
            toc_idx = i
            break
    if toc_idx is None:
        continue

    titles = []
    for l in lines[toc_idx+1:]:
        l = l.strip()
        if not l or re.match(r"작성자:|검토/개정일|주제 참고 자료", l):
            break
        titles.append(l)

    # 6) 각 섹션별로 본문 추출
    for idx, title in enumerate(titles):
        # 제목 라인 찾기
        try:
            start = lines.index(title) + 1
        except ValueError:
            continue
        # 다음 제목이 있으면 그 위치를 end로, 아니면 끝까지
        if idx+1 < len(titles):
            try:
                end = lines.index(titles[idx+1])
            except ValueError:
                end = len(lines)
        else:
            end = len(lines)
        section_text = "\n".join(lines[start:end]).strip()
        if not section_text:
            continue

        # 7) 분할기 적용해서 청크 생성 & 중복·짧은 청크 필터링
        for chunk in splitter.split_text(section_text):
            content = chunk.strip()
            token_count = len(content.split())
            if token_count < 20:  # 너무 짧으면 스킵
                continue
            if content in seen:  # 중복 제거
                continue
            seen.add(content)
            documents.append({
                "section": title,
                "content": content,
                "tokens": token_count,
                "source": url
            })

# 8) 결과 저장
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(documents, f, ensure_ascii=False, indent=2)

print(f"✅ 총 생성된 유니크 청크 수: {len(documents)}")
print(f"✅ 결과 파일 저장: {OUTPUT_FILE}")