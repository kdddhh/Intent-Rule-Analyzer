from pydantic import BaseModel, Field
from typing import List, Dict, Any

# 1. 요청 모델 (Input DTO)
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=200, description="사용자 질문")

# 2. 응답 모델 (Output DTO) - 실무 권장 사항
class SearchResponse(BaseModel):
    intent_detected: str = Field(..., description="파악된 사용자 의도")
    entities_extracted: List[Dict[str, str]] = Field(..., description="추출된 개체 목록")
    summary_data: Dict[str, Any] = Field(..., description="Elasticsearch Aggregation 결과")