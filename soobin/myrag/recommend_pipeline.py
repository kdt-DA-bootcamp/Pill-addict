
# pill-addict/soobin/myrag/recommend_pipeline.py
"""
- 성분(ingredients)을 최대 3개까지만 사용
- search_side_effects()에서 RAG 문서를 최대 300자로 잘라서 LLM에 넘김
- Chroma -> Faiss로 변경
"""

from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Dict, List, Optional

# 🏷️ 경로 설정

BASE_DIR    = Path(__file__).resolve().parent # 예: .../soobin
DATA_DIR    = BASE_DIR / "ragdata"
# 🔔 Faiss 인덱스 폴더 경로 (이전 persist_dir=Chroma 대체)
FAISS_INDEX_DIR = BASE_DIR / "faiss_index_msd"

print(FAISS_INDEX_DIR) 

def load_json(path: Path):
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(encoding="utf-8") as f:
        return json.load(f)

_function_ingredient = load_json(DATA_DIR / "function_ingredient.json")
_body_function       = load_json(DATA_DIR / "body_function.json")
_supplement_data     = load_json(DATA_DIR / "supplement.json")


# ─────────────────────────────────────────────────────────────────
# 🏷️ Faiss 기반 RAG 검색 클래스
# ─────────────────────────────────────────────────────────────────
class MsdRagSearch:
    """Faiss(벡터 DB) + OpenAI Embeddings"""

    def __init__(self, openai_api_key: str, index_dir: Path = FAISS_INDEX_DIR):
        from langchain_openai import OpenAIEmbeddings
        from langchain_community.vectorstores import FAISS

        embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        # 🔔 Faiss 인덱스 로드
        self.db = FAISS.load_local(
            folder_path=str(index_dir),
            embeddings=embeddings,
            allow_dangerous_deserialization=True
        )

    def search_side_effects(self, ingredient: str, k: int = 1) -> List[str]:
        """
        ingredient 키워드 → similarity_search
        최대 k개 문서, 각 문서는 300자까지 슬라이스
        """
        docs = self.db.similarity_search(ingredient, k=k)
        if not docs:
            return ["추가 정보 없음"]

        # ── 최대 300자 슬라이스 ──
        results = []
        for d in docs:
            snippet = d.page_content[:300].strip() + "…"
            results.append(snippet)
        return results


# ─────────────────────────────────────────────────────────────────
# 🏷️ 파싱 함수들
# ─────────────────────────────────────────────────────────────────
def parse_exam_info(text: Optional[str]) -> List[str]:
    if not text:
        return []
    out: List[str] = []
    if "간" in text:
        out.append("간 건강")
    if "혈압" in text:
        out.append("혈압")
    return out

def parse_body_function(body_part: Optional[str]) -> List[str]:
    if not body_part:
        return []
    matched: List[str] = []
    for item in _body_function:
        if body_part in item["body"]:
            matched.extend(x.strip() for x in item["function"].split(","))
    return matched

def parse_symptom(symptom: Optional[str]) -> List[str]:
    if not symptom:
        return []
    out: List[str] = []
    if "피로" in symptom:
        out.append("피로")
    if "기억력" in symptom:
        out.append("기억력")
    return out

def get_ingredients(func_list: List[str]) -> List[str]:
    if not func_list:
        return []
    matched: List[str] = []
    for f in func_list:
        for item in _function_ingredient:
            if f in item["function"]:
                matched.extend(x.strip() for x in item["ingredient"].split(","))
    return list(set(matched))

def get_supplements(ingredients: List[str]) -> List[Dict]:
    if not ingredients:
        return []
    results: List[Dict] = []
    for sup in _supplement_data:
        raw_name = sup.get("RAWMTRL_NM") or ""
        fnclty   = sup.get("PRIMARY_FNCLTY") or ""
        combined = (raw_name + fnclty).lower()
        if any(ing.lower() in combined for ing in ingredients):
            results.append(sup)
    return results


# ─────────────────────────────────────────────────────────────────
# 🏷️ 메인 파이프라인
# ─────────────────────────────────────────────────────────────────
def process_recommendation(
    *,
    exam_info: Optional[str],
    body_part: Optional[str],
    symptom: Optional[str],
    openai_api_key: str,
) -> Dict:
    # 1) parse exam_info/body_part/symptom -> 기능
    funcs = set(
        parse_exam_info(exam_info)
        + parse_body_function(body_part)
        + parse_symptom(symptom)
    )
    if not funcs:
        funcs = {"기능 없음"}

    # 2) 기능 -> 성분
    ingredients = get_ingredients(list(funcs)) or ["성분 없음"]
    if "성분 없음" not in ingredients:
        # 최대 3개 제한
        ingredients = ingredients[:3]

    # 3) MSD 부작용 RAG (Faiss)
    msd_info: Dict[str, List[str]] = {}
    if "성분 없음" not in ingredients:
        rag = MsdRagSearch(openai_api_key)
        for ing in ingredients:
            msd_info[ing] = rag.search_side_effects(ing, k=1)

    # 4) 보충제 제품
    supplements = []
    if "성분 없음" not in ingredients:
        supplements = get_supplements(ingredients)

    # 5) 결과 반환
    return {
        "기능": list(funcs),
        "성분": ingredients,
        "MSD": msd_info or "없음",
        "제품": supplements or "없음",
    }


# ─────────────────────────────────────────────────────────────────
# 🏷️ LLM 자연어 생성
# ─────────────────────────────────────────────────────────────────
def generate_natural_answer(
    data: Dict,
    openai_api_key: str,
    user_input: str
) -> str:
    """
    data: process_recommendation() 결과 JSON
    user_input: 사용자 원문
    """
    from langchain_openai import ChatOpenAI
    from langchain.schema import SystemMessage, HumanMessage
    import json

    llm = ChatOpenAI(
        openai_api_key=openai_api_key,
        model_name="gpt-4o",
        temperature=0.5,
    )

    sys_msg = SystemMessage(
        content=(
            "당신은 영양제 전문가 어시스턴트입니다. "
            "사용자의 입력을 최우선으로 고려하고, "
            "비속어나 부적절한 표현은 그대로 출력하지 말고 정중히 안내하세요. "
            "근거 없는 내용은 '해당 정보 없음'이라고 답하세요."
        )
    )

    def bullet(xs):
        if isinstance(xs, list):
            return "\n".join(f"- {x}" for x in xs)
        return str(xs)

    msd_str = json.dumps(data.get("MSD", {}), ensure_ascii=False, indent=2)
    product_str = json.dumps(data.get("제품", {}), ensure_ascii=False, indent=2)

    human_msg = HumanMessage(
        content=f"""
[사용자 직접 입력]
{user_input}

[기능(시스템 추론)]
{bullet(data.get('기능', []))}

[성분(시스템 추론)]
{bullet(data.get('성분', []))}

[MSD(부작용)]
{msd_str}

[추천 제품]
{product_str}

---

지시사항:
1) 사용자 입력을 먼저 한 문장으로 요약
2) 도움이 될 성분(2~3개) + 간단 효과
3) 부작용·약물상호작용(있으면)
4) 예시 제품(1~2개)
---
"""
    )

    answer = llm.invoke([sys_msg, human_msg]).content
    return answer.strip()
