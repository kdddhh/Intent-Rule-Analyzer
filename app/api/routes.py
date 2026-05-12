from fastapi import APIRouter, HTTPException
from app.schema.search_schema import SearchRequest, SearchResponse
from app.service.search_flow import process_user_query

router = APIRouter(prefix="/api/v1", tags=["Search"])

@router.post("/search", response_model=SearchResponse)
async def search_endpoint(req: SearchRequest):
    try:
        result = await process_user_query(req.query)
        return SearchResponse(
            status="success",
            intent=result["intent"],
            template_used=result["template_used"],
            data=result["data"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))