from app.conn.esConnect import es
from typing import Any

async def execute_template(index_name: str, template_id: str, params: dict[str, Any]) -> dict[str, Any]:
    """Elasticsearch search_template API 호출"""
    try:
        response = await es.search_template(
            index=index_name,
            body={
                "id": template_id,
                "params": params
            }
        )
        # ES 8.x 클라이언트는 .body 또는 객체 직접 접근을 지원합니다.
        return dict(response) 
    except Exception as e:
        print(f"❌ ES Template Execution Error [{template_id}]: {e}")
        raise e