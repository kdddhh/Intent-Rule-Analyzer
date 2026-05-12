import os
from elasticsearch import AsyncElasticsearch

# 운영 환경의 보안 통신을 대비해 환경 변수 처리
ES_SCHEME = os.getenv("ES_SCHEME")
ES_HOST = os.getenv("ES_HOST")
ES_PORT = os.getenv("ES_PORT")
ES_USER = os.getenv("ES_USER")
ES_PASSWORD = os.getenv("ES_PASSWORD")

# 재사용 가능한 싱글톤 비동기 클라이언트
# 1. 접속 URL 구성 (아이디/비번은 URL에 노출하지 않고 별도 인자로 전달하는 게 더 깔끔함)
ES_URL = f"{ES_SCHEME}://{ES_HOST}:{ES_PORT}"

# 2. 클라이언트 생성
es = AsyncElasticsearch(
    [ES_URL],
    # basic_auth 인자에 튜플로 전달 (아이디, 비밀번호)
    basic_auth=(ES_USER, ES_PASSWORD) if ES_USER and ES_PASSWORD else None,
    verify_certs=False,  # 사설 IP/인증서 무시 설정 유지
    ssl_show_warn=False
)