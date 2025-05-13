"""
moderation.py
OpenAI Moderation API를 사용해
사용자 입력(비속어/혐오 표현 등) 사전 검열
"""

import os
import requests

OPENAI_MODERATION_URL = "https://api.openai.com/v1/moderations"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

def moderate_text(text: str) -> bool:
    """
    Returns True if text is OK (not flagged)
    Returns False if text is flagged.
    """
    if not OPENAI_API_KEY:
        # 키가 없으면 Moderation 무시(전부 통과)
        return True

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    payload = {"input": text}

    try:
        resp = requests.post(OPENAI_MODERATION_URL, headers=headers, json=payload)
        resp.raise_for_status()
        result = resp.json()
        # 첫 번째 결과만 확인
        flagged = result["results"][0].get("flagged", False)
        return not flagged  # True면 통과, False면 부적절
    except requests.exceptions.RequestException as e:
        print("Moderation API error:", e)
        # 에러시 일단 통과
        return True
