## LLM 답변 생성 프롬프트
## 이후 수정 필요요

# 라이브러리 모음
from typing import List
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain.schema import Document


# 프롬프트 작성
_llm = ChatOpenAI(model_name="gpt-4o", temperature=0.2)

PROMPT = """당신은 관절, 뼈, 근육, 뇌, 소화계 등의 증상에 따라 적절한 건강기능식품을 추천하는 영양제 전문가입니다.
다음 컨텍스트와 질문을 기반으로, 아래 형식에 따라 마크다운 리포트를 작성해주세요.

컨텍스트:
{context}

질문:
{question}

📌 문제 설명 (해당 증상과 관련된 원인, 기전 등 요약)
## 추천 기능성 성분
| 성분명 | 기능성 설명 |
|--------|--------------|
| 예시성분 | 해당 성분이 왜 도움이 되는지 설명 |
...

## 추천 영양제 리스트
### 1. 실제 제품명
      (예: "1. 매스틱 검 제품 ❌" → "1. 매스틱가드플러스 ✅")
- ✅ 성분:
- 💊 복용법:
- ⚠️ 주의:

...

## 📌 복약 안내
- 효과가 나타나는 데 걸리는 시간
- 복용 팁 (식전/후, 수분 섭취 등)
- 부작용 주의사항

📚 참고문헌: 제품 DB, 건강기능식품 정보 포털 등
"""

def generate_answer(context_docs: List[Document], question: str) -> str:
    context = "\n".join([d.page_content for d in context_docs])
    prompt = PROMPT.format(context=context, question=question)
    return _llm.invoke(prompt).content.strip()

