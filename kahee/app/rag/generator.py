## LLM 답변 생성 프롬프트
## 이후 수정 필요요

# 라이브러리 모음
from typing import List
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain.schema import Document


# 프롬프트 작성
_llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.2)

PROMPT = """당신은 기능성 영양제 전문가입니다.
다음 컨텍스트를 참고하여 사용자의 질문에 한국어로 정확히 답하세요.

컨텍스트:
{context}

질문: {question}
답변:
"""

def generate_answer(context_docs: List[Document], question: str) -> str:
    context = "\n".join([d.page_content for d in context_docs])
    prompt = PROMPT.format(context=context, question=question)
    return _llm.invoke(prompt).content.strip()

