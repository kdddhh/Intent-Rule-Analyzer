from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.routes import router
from app.conn.esConnect import es

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup (앱 켜질 때) ---
    try:
        info = await es.info()
        print(f"✅ ES Cluster Connected: {info['cluster_name']}")
    except Exception as e:
        print(f"❌ ES Connection Failed: {e}")
        
    yield  # 이 시점에 트래픽을 받기 시작합니다.
    
    # --- Shutdown (앱 꺼질 때) ---
    await es.close()
    print("🔌 ES Connection Closed safely.")

app = FastAPI(
    title="Elastic Hybrid Search API", 
    version="2.0.0",
    lifespan=lifespan
)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)