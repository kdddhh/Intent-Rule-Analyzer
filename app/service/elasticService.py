from fastapi import HTTPException
from app.conn.esConnect import ElasticClientManager

async def execute_smart_search(intent: str, entities: list):
    es = ElasticClientManager.get_client()
    
    # 1. 파라미터 매핑
    params = {}
    for ent in entities:
        if ent['type'] == 'vehicle': params['model'] = ent['value']
        if ent['type'] == 'symptom': params['symptom'] = ent['value']

    if not params:
        raise HTTPException(status_code=400, detail="분석할 주요 키워드(차종, 증상 등)를 찾을 수 없습니다.")

    # 2. 비동기 ES 템플릿 호출
    template_id = f"{intent}_template"
    try:
        response = await es.search_template(
            index="repair-logs-*",
            id=template_id,
            params=params
        )
        # LLM 전달용 데이터 사이즈 최적화 (Hits 제외, Aggs만 반환)
        return response.get("aggregations", {})
    except Exception as e:
        # ES 서버 에러 로깅 (실무에서는 logger 사용)
        raise HTTPException(status_code=500, detail="검색 엔진 처리 중 오류가 발생했습니다.")