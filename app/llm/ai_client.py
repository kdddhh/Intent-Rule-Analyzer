import os
from typing import Any
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

# OpenAI 비동기 클라이언트 초기화 (자동으로 OPENAI_API_KEY 환경변수를 읽음)
ai_client = AsyncOpenAI()

# ==========================================
# 1. Pydantic 스키마 정의 (LLM 구조화된 출력 강제용)
# ==========================================
class SearchParams(BaseModel):
    symptom: str = Field(
        description="조사('은', '는', '이', '가', '알려줘' 등)를 제거하고 정제된 핵심 증상 키워드. (예: '시동 꺼짐', '엔진 소음', '브레이크 밀림')"
    )
    start_date: str | None = Field(
        default=None, 
        description="시작일. 명시되지 않으면 null. Elasticsearch Date Math 표현식을 사용하세요. (예: 최근 3개월 -> 'now-3M/M', 작년 -> 'now-1y/y', 지난주 -> 'now-1w/w')"
    )
    end_date: str | None = Field(
        default=None, 
        description="종료일. 명시되지 않으면 null. 보통 'now'를 사용합니다."
    )
    top_n: int = Field(
        default=5, 
        description="원인 분석 시 상위 몇 개를 볼지. 사용자가 개수를 명시하지 않으면 기본값 5."
    )
    size: int = Field(
        default=3, 
        description="유사 사례 검색 시 가져올 문서 수. 사용자가 개수를 명시하지 않으면 기본값 3."
    )
    interval: str = Field(
        default="month", 
        description="추이 분석 간격. 'day', 'week', 'month', 'year' 중 하나. 명시되지 않으면 기본값 'month'."
    )

# ==========================================
# 2. 핵심 비즈니스 로직 함수
# ==========================================
async def get_embedding(text: str) -> list[float]:
    """
    텍스트를 1536차원 임베딩 벡터로 변환합니다.
    사용 모델: 최신 가성비 모델인 text-embedding-3-small
    """
    try:
        response = await ai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"❌ Embedding Generation Error: {e}")
        # 실패 시 시스템이 뻗지 않도록 빈 벡터 반환 (실무 방어 코드)
        return [0.0] * 1536 

async def extract_params_via_llm(query: str) -> dict[str, Any]:
    """
    OpenAI Structured Outputs를 사용하여 자연어에서 파라미터를 정확히 추출합니다.
    """
    system_prompt = """
    당신은 자동차 정비 데이터 검색 시스템의 쿼리 분석기입니다.
    사용자의 질문에서 검색에 필요한 핵심 파라미터를 추출하세요.
    특히, 날짜나 기간이 언급되면 Elasticsearch의 Date Math(예: now-1M/M, now-1y/y) 형식으로 똑똑하게 변환해야 합니다.
    """

    try:
        # beta.chat.completions.parse API를 사용하면 response_format에 맞춘 JSON을 보장합니다.
        response = await ai_client.beta.chat.completions.parse(
            model="gpt-4o-mini", # 파싱 작업은 mini 모델로도 충분히 빠르고 저렴하게 가능합니다.
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"사용자 질문: {query}"}
            ],
            response_format=SearchParams,
            temperature=0.0 # 창의성이 필요 없으므로 0으로 고정
        )
        
        # Pydantic 객체로 받아진 결과를 파이썬 딕셔너리로 변환하여 반환
        extracted_data = response.choices[0].message.parsed.model_dump()
        return extracted_data

    except Exception as e:
        print(f"❌ LLM Parsing Error: {e}")
        # 실패 시 기본값 Fallback (장애 격리)
        return {
            "symptom": query, 
            "start_date": None, 
            "end_date": None,
            "top_n": 5,
            "size": 3,
            "interval": "month"
        }