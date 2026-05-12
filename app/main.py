from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.routes import router
from app.conn.esConnect import ElasticClientManager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 서버 기동 시 ES 연결 풀 생성
    await ElasticClientManager.connect()
    yield
    # 서버 종료 시 안전하게 연결 해제
    await ElasticClientManager.disconnect()

app = FastAPI(lifespan=lifespan, title="JINION AI")

# API 라우터 등록
app.include_router(router)