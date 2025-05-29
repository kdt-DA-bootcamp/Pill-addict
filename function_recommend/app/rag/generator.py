## LLM 답변 생성 프롬프트
## 이후 수정 필요

# 라이브러리 모음
from typing import List
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain.schema import Document
import time
import os


# 프롬프트 작성
_llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.2, openai_api_key=os.getenv("OPENAI_API_KEY"))
RATE_LIMIT_DELAY = 2.0 
#--- 0529 수정부분---------------------#
PROMPT = """당신은 관절, 뼈, 근육, 뇌, 소화계 등의 증상에 따라 적절한 건강기능식품을 추천하는 영양제 전문가입니다.
아래 **컨텍스트**는 두 부분으로 이루어집니다.
중요: 
- 반드시 컨텍스트에 주어진 문서(`metadata["name"]`)에 있는 ‘실제 제품명’만 사용하세요. 
- 루테인, 밀크씨슬 등 "카테고리 명"만 쓰지 말고, 예) "중외루테인맥스" 같은 실제 제품명을 권장합니다.
#------------------------------------------#

① *제품·성분 컨텍스트*  
② *MSD 매뉴얼에서 추출한 부작용·주의사항 컨텍스트* 

두 컨텍스트와 사용자의 질문을 모두 반영해, 다음 형식으로 마크다운 리포트를 작성하세요.

컨텍스트:
{context}                     # ① + ② 는 각각 <제품 주의사항>, <MSD>로 구분지어서 들어옴

질문:
{question}

📌 문제 설명
{question}와(과) 관련된 신체 기전·원인을 2~3문장으로 요약합니다.

## 추천 기능성 성분
| 성분명 | 기능성 설명 | 
|--------|------------|
| 예) 홍삼 | 면역 증진·피로 개선 도움 |
| 예) 매실추출물 | 소화 효소 활성화 |

## 부작용·약물 상호작용  ★ MSD 기반
#아래 내용을 ‘사실 그대로’ 간결히 요약하세요.  
#(근거 출처: MSD 매뉴얼)

- **주요 부작용:** •••  
- **약물 상호작용:** •••  
- **고위험군(임산부·항응고제 복용자 등):** •••  

## 추천 영양제 리스트
아래에는 **컨텍스트의 메타데이터**(`name` 필드)에 있는 **실제 제품명**을 그대로 사용하여 2~3개를 선택하세요.  
### 1. {{제품명}}
- ✅ **주성분**: …  
- 💊 **권장 복용법**: …  
- ⚠️ **주의사항**: MSD 부작용 요약에서 해당 성분 부분 참조

… (2–3개 제품)

## 📌 복약 팁
- 효과 발현 예상 기간 …  
- 식전/식후, 수분 섭취 등 …  

📚 **참고문헌**  
- 국내 건강기능식품 정보 포털  
- MSD 매뉴얼 부작용·상호작용
"""


# def generate_answer(context_docs: List[Document], question: str) -> str:
    
#     context = "\n".join([d.page_content for d in context_docs])
#     prompt = PROMPT.format(context=context, question=question)
#     time.sleep(RATE_LIMIT_DELAY)
#     return _llm.invoke(prompt).content.strip()
#----------프롬프트 수정 (가희님 테스트 부탁드려요) -------------------------#
def generate_answer(context_docs: List[Document], question: str) -> str:
    # 1) 먼저 문서들에서 제품명 메타데이터만 추출해 텍스트로 구성
    product_names = [
        doc.metadata["name"] for doc in context_docs
        if "name" in doc.metadata
    ]
    product_list_str = "\n".join(f"- {pn}" for pn in product_names)

    # 2) LLM prompt에 ‘사용가능한 실제 제품명 리스트’를 먼저 노출
    #    → LLM이 여기서 실제 제품명을 가져다가 사용하기 용이해짐
    products_heading = (
        "사용 가능한 실제 제품명 리스트:\n" +
        (product_list_str if product_names else "(제품명 없음)") +
        "\n\n"
    )

    # 3) 기존 문서 내용도 함께 연결
    context_str = products_heading + "\n".join([d.page_content for d in context_docs])

    # 4) 최종 프롬프트
    prompt = PROMPT.format(context=context_str, question=question)

    # LLM 호출
    time.sleep(RATE_LIMIT_DELAY)
    return _llm.invoke(prompt).content.strip()

