from app.config import settings
import openai

openai.api_key = settings.openai_api_key


def get_most_similar_function(user_input: str, candidates: list[str]) -> str:
    """
    사용자의 자유 입력과 candidates 리스트를 비교하여 가장 유사한 항목 1개 반환
    """
    import difflib
    return difflib.get_close_matches(user_input, candidates, n=1, cutoff=0.3)[0] if candidates else None

    """
    ▶ TODO ❶
    • user_profile  : 설문 + 입력 텍스트가 dict 로 들어옴
    • 반환           : [{product_id, product_name, score, rationale}, ...]

    예시 흐름:
    - 사용자 프로필에서 증상/기능 키워드 추출
    - 벡터 DB에서 관련 논문/지식 검색
    - LLM에 인젝션하여 추천 문장 생성 및 점수화
    """
    prompt = f"""
    너는 건강기능식품 추천 전문가야. 아래 사용자의 상태에 따라 가장 적절한 5개 제품을 추천해 줘.

    사용자 정보:
    {user_profile}

    추천 형식:
    - 제품명
    - 추천 이유
    - 성분 및 주의사항
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o", 
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )


    return [{
        "product_id": "P0001",
        "product_name": "오메가3 고함량",
        "score": 0.95,
        "rationale": response.choices[0].message.content.strip()
    }]


def chat_llm(user_msg: str, user_profile: dict) -> str:
    """
    ▶ TODO ❷
    • 사용자 질문(user_msg)과 프로필을 받아 LLM 응답 생성

    사용 예시:
    "폐경 여성인데 어떤 영양제가 좋아요?"
    """
    prompt = f"""
    너는 건강기능식품 전문 AI 챗봇이야.
    아래 사용자 질문에 대해 친절하게 한국어로 답변해 줘.

    [사용자 정보]
    {user_profile}

    [질문]
    {user_msg}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
    )

    return response.choices[0].message.content.strip()
