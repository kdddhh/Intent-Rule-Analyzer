import os
from elasticsearch import AsyncElasticsearch

# 운영 환경의 보안 통신을 대비해 환경 변수 처리
ES_URL = os.getenv("ELASTIC_URL", "http://localhost:9200")

# 재사용 가능한 싱글톤 비동기 클라이언트
es = AsyncElasticsearch([ES_URL])