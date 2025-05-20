# pill-addict/soobin/myrag/summarize.py
# (새로 추가한 파일 예시)

from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

def summarize_text(long_text: str, openai_api_key: str, max_chars=300) -> str:
    """
    긴 텍스트를 LLM으로 간단 요약.
    max_chars=300 정도 선에서 최대 길이를 제약.
    """
    if not long_text:
        return "추가 정보 없음"

    # 혹시 정말 짧다면 그냥 반환
    if len(long_text) < max_chars:
        return long_text

    # 요약 LLM
    llm = ChatOpenAI(
        openai_api_key=openai_api_key,
        model_name="gpt-4o",
        temperature=0.0,
    )

    system_msg = SystemMessage(
        content="당신은 능숙한 요약가입니다. 아래 텍스트를 간단히 요약하세요."
    )
    human_msg = HumanMessage(content=f"다음 텍스트를 최대 200자 내외로 요약:\n\n{long_text}")

    summary = llm.invoke([system_msg, human_msg]).content.strip()
    # 2차 가공: 글자 수가 여전히 길다면 슬라이스
    return summary[:max_chars]
