## 🛠 설치 및 설정 (Setup)

프로젝트를 로컬 환경에서 실행하기 위해 아래의 단계를 순서대로 진행해 주세요.

### 1. 가상환경 구성 (Virtual Environment)
파이썬 환경의 독립성을 위해 가상환경 사용을 권장합니다.

```bash
# 가상환경 생성 (폴더명은 원하는대로 수정 가능)
python -m venv venv

# 가상환경 활성화 (Windows)
.\venv\Scripts\activate

# 가상환경 활성화 (macOS/Linux)
source venv/bin/activate
```

### 2. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

### 3. 환경변수 설정
.env인 파일이 필요. (파일명 없이 확장자만 존재)
프로젝트 루트에 파일 생성 후, 아래의 내용을 채움

ES_HOST=
ES_USER=
ES_PASSWORD=
ES_SCHEME=https
ES_PORT=

#OPEN AI KEY
OPENAI_API_KEY = ""

### 4. Rest API 테스트 설정
확장 프로그램인 REST Client 설치 (설치 후, vscode 재실행 권장)

### 5. 실행
```bash
# 1. 실행을 위해선 가상환경이 활성화되어 있어야 함.

# 가상환경 활성화 (Windows)
.\venv\Scripts\activate

# 가상환경 활성화 (macOS/Linux)
source venv/bin/activate

# 2. 로컬에서 서버 실행
uvicorn app.main:app --reload # ES Cluster Connected: elasticsearch라는 문구가 떠야 성공

```

이후엔 test.http 파일에서 각 테스트 코드마다 위치한 Send Request를 클릭

