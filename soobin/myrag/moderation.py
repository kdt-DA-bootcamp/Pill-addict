#pill-addict/soobin/myrag/moderation.py
"""
🔒 OpenAI Moderation API를 통해
사용자 입력(비속어/혐오 표현 등)을 사전 검열하는 모듈

📝 사용법:
1) .env에 OPENAI_API_KEY 설정
2) moderate_text("사용자 입력") → True/False 반환
   - True: 통과 (안전)
   - False: 부적절 (flagged)
"""

import os
import requests

OPENAI_MODERATION_URL = "https://api.openai.com/v1/moderations"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

def moderate_text(text: str) -> bool:
    """
    🏷️ 사용자 입력 text를 OpenAI Moderation API에 보내
    1) True  → 문구가 '정상'(flagged 되지 않음)
    2) False → 부적절(flagged) → 사용 불가

    ⛔️ 키가 없으면 Moderation API 호출 불가 → 모든 입력을 통과(True)
    """
    # (1) .env에 API 키가 없으면 그냥 True로 통과 처리
    if not OPENAI_API_KEY:
        # 키가 없으므로 API 호출 못 함
        return True

    # (2) API 요청 준비
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    payload = {"input": text}

    # (3) 실제 HTTP 호출
    try:
        resp = requests.post(
            url=OPENAI_MODERATION_URL,
            headers=headers,
            json=payload
        )
        resp.raise_for_status()  # 4xx/5xx 발생 시 예외

        # (4) Moderation 결과 파싱
        result = resp.json()
        # "results" 리스트의 첫 번째 항목에 "flagged"가 True면 부적절
        flagged = result["results"][0].get("flagged", False)
        return not flagged  # flagged=False → True(통과)

    except requests.exceptions.RequestException as e:
        # 네트워크/Timeout/HTTP에러 시 일단 True(통과) 처리
        print("⚠️ Moderation API error:", e)
        return True
