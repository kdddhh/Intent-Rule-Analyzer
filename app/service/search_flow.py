from app.analyze.analyzer import router
from app.llm.ai_client import get_embedding, extract_params_via_llm
from app.service.elasticService import execute_template
from typing import Any

TARGET_INDEX = "jjc_20260511_claim_test_index"

async def process_user_query(user_query: str) -> dict[str, Any]:
    # 1. 라우터 분석
    route_info = router.route(user_query)
    intent = route_info["intent"]
    
    # ==========================================
    # Fast-Path (DTC 분석)
    # ==========================================
    if route_info["fast_path"]:
        template_id = "dtc_analysis_template"
        es_params = {"dtc": route_info["params"]["dtc"]}
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

    # 기본 파라미터 구성
    es_params = {
        "symptom": symptom_text,
        "query_vector": query_vector,
        "start_date": llm_params.get("start_date"),
        "end_date": llm_params.get("end_date")
    }

    # 의도(Intent)별 추가 파라미터 분기
    match intent: # Python 3.10+ Pattern Matching 활용 (모던 파이썬)
        case "cause_analysis":
            es_params["model"] = model_name
            es_params["top_n"] = llm_params.get("top_n", 5)
        case "trend_analysis":
            es_params["interval"] = llm_params.get("interval", "month")
        case "similar_case":
            es_params["size"] = llm_params.get("size", 3)
        case "supplier_analysis":
            pass

    # Mustache 에러 방지를 위해 None 값 제거 (Pythonic)
    clean_params = {k: v for k, v in es_params.items() if v is not None}
    
    template_id = f"{intent}_template"
    es_result = await execute_template(TARGET_INDEX, template_id, clean_params)
    
    return {"intent": intent, "template_used": template_id, "data": es_result}