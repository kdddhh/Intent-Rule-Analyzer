from pydantic import BaseModel, Field
from typing import Any

class SearchRequest(BaseModel):
    # Field의 description을 명확히 주어 Swagger UI 자동화 문서의 품질을 높입니다.
    query: str = Field(..., min_length=2, description="사용자 질문 (예: P0101 조치방법, NX4 시동불량 원인)")

class SearchResponse(BaseModel):
    status: str
    intent: str
    template_used: str
    data: dict[str, Any] # Python 3.10+ 네이티브 타입