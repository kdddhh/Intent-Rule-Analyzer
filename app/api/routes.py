from fastapi import APIRouter
from app.schema.search_schema import SearchRequest, SearchResponse
from app.analyze.analyzer import analyzer_instance
from app.service.elasticService import execute_smart_search

router = APIRouter()

# response_model을 지정하면 FastAPI가 알아서 SearchResponse 형태에 맞춰 필터링 및 문서화를 해줍니다.
@router.post("/api/elastic/search", response_model=SearchResponse)
async def smart_search(request: SearchRequest):
    # 1. 의도 분석
    intent, entities = analyzer_instance.analyze(request.query)
    
    # 2. ES 검색 실행
    summary_data = await execute_smart_search(intent, entities)
    
    # 3. 결과 반환 (이 딕셔너리는 자동으로 SearchResponse 클래스로 검증/변환됩니다)
    return {
        "intent_detected": intent,
        "entities_extracted": entities,
        "summary_data": summary_data
    }