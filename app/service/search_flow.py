from datetime import datetime
from dateutil.relativedelta import relativedelta
from app.analyze.analyzer import router
from app.llm.ai_client import get_embedding, extract_params_via_llm
from app.service.elasticService import execute_template
from typing import Any

TARGET_INDEX = "claim_data_nori"

def _get_formatted_dates(start_date: str | None, end_date: str | None) -> tuple[str, str]:
    """
    날짜가 없으면 최근 2년 범위 생성, 
    값이 있다면 엘라스틱서치 형식(YYYYMMDD)에 맞게 하이픈(-) 제거
    """
    today = datetime.now()
    
    if not end_date:
        final_end = today.strftime("%Y%m%d")
    else:
        final_end = end_date.replace("-", "")
        
    if not start_date:
        final_start = (today - relativedelta(years=2)).strftime("%Y%m%d")
    else:
        final_start = start_date.replace("-", "")
        
    return final_start, final_end


async def process_user_query(user_query: str) -> dict[str, Any]:
    # 1. 라우터 분석
    route_info = router.route(user_query)
    intent = route_info["intent"]
    
    # ==========================================
    # Fast-Path (DTC 분석)
    # ==========================================
    if route_info["fast_path"]:
        template_id = "dtc_analysis_template"
        
        # 🚨 중요: DTC 템플릿에도 날짜 필터가 생겼으므로 강제로 2년 세팅
        start_date, end_date = _get_formatted_dates(None, None)
        
        es_params = {
            "dtc": route_info["params"]["dtc"],
            "start_date": start_date,
            "end_date": end_date
        }
        result = await execute_template(TARGET_INDEX, template_id, es_params)
        return {"intent": intent, "template_used": template_id, "data": result}

    # ==========================================
    # Slow-Path (하이브리드 & 자연어 처리)
    # ==========================================
    raw_query = route_info["params"]["raw_query"]
    model_name = route_info["params"]["model"]
    
    # 비동기 LLM 처리
    llm_params = await extract_params_via_llm(raw_query)
    symptom_text = llm_params["symptom"]
    query_vector = await get_embedding(symptom_text)

    # ✨ 새롭게 추가된 날짜 전처리 (하이픈 제거 및 None 방어)
    start_date, end_date = _get_formatted_dates(
        llm_params.get("start_date"), 
        llm_params.get("end_date")
    )

    # 기본 파라미터 구성
    es_params = {
        "symptom": symptom_text,
        "query_vector": query_vector,
        "start_date": start_date,  # 무조건 "YYYYMMDD" (절대 None 아님)
        "end_date": end_date       # 무조건 "YYYYMMDD" (절대 None 아님)
    }

    # 의도(Intent)별 추가 파라미터 분기
    match intent: 
        case "cause_analysis":
            es_params["model"] = model_name
            es_params["top_n"] = llm_params.get("top_n", 5)
        case "trend_analysis":
            es_params["interval"] = llm_params.get("interval", "month")
        case "similar_case":
            es_params["size"] = llm_params.get("size", 3)
        case "supplier_analysis":
            pass

    # Mustache 에러 방지를 위해 None 값 제거
    # (이제 start_date, end_date는 항상 값이 있으므로 안전합니다)
    clean_params = {k: v for k, v in es_params.items() if v is not None}
    
    template_id = f"{intent}_template"
    es_result = await execute_template(TARGET_INDEX, template_id, clean_params)
    
    return {"intent": intent, "template_used": template_id, "data": es_result}