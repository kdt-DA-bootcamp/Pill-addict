import openai
from app.config import settings

openai.api_key = settings.OPENAI_API_KEY  # .env에 키 추가시 사용

def generate_answer(context_list, user_query):
    context = "\n".join(context_list)
    prompt = f"""
다음 컨텍스트를 참고하여 사용자의 질문에 답해주세요.

--- 컨텍스트 ---
{context}
---------------

질문: {user_query}

답변:
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "당신은 영양제 추천 전문가입니다."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    return response["choices"][0]["message"]["content"].strip()
