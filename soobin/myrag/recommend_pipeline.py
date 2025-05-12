"""
recommend_pipeline.py
────────────────────────────────────────────────────────────
exam_info / body_part / symptom  →  기능 → 성분
        → MSD(부작용) + 제품 DB 매칭 → 구조화 JSON
        → generate_natural_answer() 로 Markdown 답변 생성
"""

from __future__ import annotations

import json, os
from pathlib import Path
from typing import Dict, List, Optional

# ────────────── 프로젝트 경로 설정 ──────────────────────────
BASE_DIR   = Path(__file__).resolve().parent.parent        # .../soobin
DATA_DIR   = BASE_DIR / "ragdata"                          # .../soobin/ragdata
PERSIST_DIR = BASE_DIR / "msd_chroma_db"                   # Chroma index

# ────────────── 공통 유틸 ──────────────────────────────────
def load_json(path: Path):
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(encoding="utf-8") as f:
        return json.load(f)

# 캐싱해 두면 파일 I/O 최소화
_function_ingredient = load_json(DATA_DIR / "function_ingredient.json")
_body_function       = load_json(DATA_DIR / "body_function.json")
_supplement_data     = load_json(DATA_DIR / "supplement.json")

# ────────────── MSD RAG 검색 클래스 ────────────────────────
class MsdRagSearch:
    """Chroma(벡터 DB) + OpenAI Embeddings wrapper"""

    def __init__(self, openai_api_key: str, persist_dir: Path = PERSIST_DIR):
        from langchain_openai import OpenAIEmbeddings
        from langchain_community.vectorstores import Chroma

        emb = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self.db = Chroma(
            persist_directory=str(persist_dir),
            embedding_function=emb,
        )

    def search_side_effects(self, ingredient: str, k: int = 1) -> List[str]:
        docs = self.db.similarity_search(ingredient, k=k)
        if not docs:
            return ["추가 정보 없음"]
        return [d.page_content[:200].strip() + "…" for d in docs]

# ────────────── 파싱 헬퍼들 ────────────────────────────────
def parse_exam_info(text: Optional[str]) -> List[str]:
    if not text:
        return []
    out: List[str] = []
    if "간" in text:
        out.append("간 건강")
    if "혈압" in text:
        out.append("혈압")
    # 필요 시 추가 규칙…
    return out

def parse_body_function(body_part: Optional[str]) -> List[str]:
    if not body_part:
        return []
    matched: List[str] = []
    for item in _body_function:
        if body_part in item["body"]:
            matched.extend([x.strip() for x in item["function"].split(",")])
    return matched

def parse_symptom(symptom: Optional[str]) -> List[str]:
    if not symptom:
        return []
    out: List[str] = []
    if "피로" in symptom:
        out.append("피로")
    if "속쓰림" in symptom or "소화" in symptom:
        out.append("위")
    return out

def get_ingredients(func_list: List[str]) -> List[str]:
    if not func_list:
        return []
    matched: List[str] = []
    for f in func_list:
        for item in _function_ingredient:
            if f in item["function"]:
                matched.extend([x.strip() for x in item["ingredient"].split(",")])
    return list(set(matched))

def get_supplements(ingredients: List[str]) -> List[Dict]:
    results: List[Dict] = []
    for sup in _supplement_data:
        # .get()가 None일 경우 ""로 대체
        raw_str = sup.get("RAWMTRL_NM") or ""
        fnc_str = sup.get("PRIMARY_FNCLTY") or ""
        combined = (raw_str + fnc_str).lower()

        if any(ing.lower() in combined for ing in ingredients):
            results.append(sup)
    return results


# ────────────── 핵심 파이프라인 ────────────────────────────
def process_recommendation(
    *,
    exam_info: Optional[str],
    body_part: Optional[str],
    symptom: Optional[str],
    openai_api_key: str,
) -> Dict:
    # 1) 텍스트 → 기능 키워드
    funcs = set(
        parse_exam_info(exam_info)
        + parse_body_function(body_part)
        + parse_symptom(symptom)
    )
    if not funcs:
        funcs = {"기능 없음"}

    # 2) 기능 → 성분
    ingredients = get_ingredients(list(funcs)) or ["성분 없음"]

    # 3) MSD 부작용 검색
    msd_info: Dict[str, List[str]] = {}
    if "성분 없음" not in ingredients:
        rag = MsdRagSearch(openai_api_key)
        for ing in ingredients:
            msd_info[ing] = rag.search_side_effects(ing, k=1)

    # 4) 보충제 제품 후보
    supplements = (
        get_supplements(ingredients) if "성분 없음" not in ingredients else []
    )

    # 5) 구조화 데이터 반환
    return {
        "기능": list(funcs),
        "성분": ingredients,
        "MSD": msd_info or "없음",
        "제품": supplements or "없음",
    }

# ────────────── 자연어 답변 생성 (선택) ─────────────────────
def generate_natural_answer(data: Dict, openai_api_key: str) -> str:
    """
    process_recommendation() 결과 JSON → Markdown 답변
    """
    from langchain_openai import ChatOpenAI
    from langchain.schema import SystemMessage, HumanMessage

    llm = ChatOpenAI(
        openai_api_key=openai_api_key,
        model_name="gpt-4o",
        temperature=0.3,
    )

    sys_msg = SystemMessage(
        content=(
            "당신은 영양제 전문가 어시스턴트입니다. "
            "근거 기반 정보만 제공하고, 데이터에 없는 내용은 '해당 정보 없음'이라고 답합니다."
        )
    )

    bullet = (
        lambda xs: "\n".join(f"- {x}" for x in xs)
        if isinstance(xs, list)
        else str(xs)
    )

    human_msg = HumanMessage(
        content=f"""
[기능]
{bullet(data['기능'])}

[성분]
{bullet(data['성분'])}

[MSD 스니펫]
{json.dumps(data['MSD'], ensure_ascii=False, indent=2)}

[추천 제품]
{json.dumps(data['제품'][:3], ensure_ascii=False, indent=2)}

위 정보를 바탕으로

1) 사용자의 건강 고민을 한 문장으로 요약  
2) 도움이 될 핵심 성분(2~3개) + 간단 효과  
3) 부작용·약물상호작용(있으면) 제시  
4) 예시 제품 1~2개를 표로 (없으면 '제품 정보 없음')  

Markdown 형식으로 작성하세요.
"""
    )

    answer = llm.invoke([sys_msg, human_msg]).content
    return answer.strip()
 