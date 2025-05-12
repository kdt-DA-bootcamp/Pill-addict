## LLM 프롬프트트
#추후 구체화 필요

# 라이브러리 및 설정 가져오기
from typing import List, Optional
from openai import OpenAI
from app.config.settings import settings

# LLM 호출 및 프롬프트
_llm = OpenAI(api_key=settings.OPENAI_API_KEY)

def get_most_similar_function(user_input: str, candidates: List[str]) -> Optional[str]:
    if not candidates:
        return None
    options = "\n".join(f"- {c}" for c in candidates)
    prompt = f"""\
너는 건강 기능 추천 전문가야.
아래 리스트 중 사용자 고민과 가장 관련 있는 기능 하나만 선택해.
{options}
사용자 고민: {user_input}
-> 기능 이름만 한 줄로 출력해.
"""
    try:
        resp = _llm.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":prompt}],
            temperature=0.0
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return None
