from app.config import settings
import openai
from typing import Optional

# client 객체 생성
client = openai.OpenAI(
    api_key=settings.openai_api_key
)

def get_most_similar_function(user_input: str, candidates: list[str]) -> Optional[str]:
    """
    사용자의 자유 입력(user_input)과 candidates 리스트를 비교하여
    의미상 가장 가까운 기능을 LLM을 통해 고른다.
    """
    if not candidates:
        return None

    options_text = "\n".join([f"- {func}" for func in candidates])

    prompt = f"""
너는 건강 기능 추천 전문가야.
다음은 건강 기능 리스트야:
{options_text}

사용자가 '{user_input}' 라고 고민을 입력했어.
리스트 중 가장 관련 있는 기능 **하나만** 정확히 골라서 답해.
리스트에 없는 기능을 새로 만들지 말고, 반드시 주어진 리스트 중에서 하나만 선택해.
답변은 기능 이름만 짧게 해줘.
최종 답변 카드에는 해당 제품명을 검색해서 그 이미지를 같이 첨부해줘.
"""

    print("[LLM 요청 prompt]")
    print(prompt)

    try:
        # client 사용해서 호출
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        # response 파싱
        best_function = response.choices[0].message.content.strip()

        print("[LLM 응답 best_function]")
        print(best_function)

        return best_function
    except Exception as e:
        print(f"LLM 호출 중 에러 발생: {e}")
        return None