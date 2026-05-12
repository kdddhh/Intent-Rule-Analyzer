from elasticsearch import AsyncElasticsearch
from dotenv import load_dotenv
import os

load_dotenv()

class ElasticClientManager:
    es: AsyncElasticsearch = None

    @classmethod
    async def connect(cls):
        # 운영 환경 필수: 타임아웃 및 스니핑(Sniffing) 설정
        cls.es = AsyncElasticsearch(
            os.getenv("ES_URL"), 
            request_timeout=3.0,  # 3초 이상 응답 없으면 연결 끊기 (FastAPI 스레드 보호)
            max_retries=1
        )
    
    @classmethod
    async def disconnect(cls):
        if cls.es:
            await cls.es.close()

    @classmethod
    def get_client(cls) -> AsyncElasticsearch:
        return cls.es