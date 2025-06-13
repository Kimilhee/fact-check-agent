# Fact Check Agent

Google ADK(Agent Development Kit)를 이용한 팩트체크 에이전트입니다. 이 에이전트는 주어진 텍스트의 사실 여부를 검증하고, 다른 에이전트의 서브에이전트로 사용하거나 독립적인 API 서비스로 사용할 수 있습니다.

## 기능

- 텍스트의 사실 여부 검증
- Google ADK를 통한 에이전트 구현
- FastAPI를 통한 REST API 제공
- 다른 에이전트의 서브에이전트로 통합 가능

## 설치 방법

1. 가상환경 생성 및 활성화:

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 또는
.venv\Scripts\activate  # Windows
```

2. 의존성 설치:

```bash
pip install -r requirements.txt
```

3. Google Cloud 인증 설정:

- Google Cloud Console에서 프로젝트 생성
- 서비스 계정 키 생성 및 다운로드
- 환경 변수 설정:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service-account-key.json"
```

## 사용 방법

### API 서버 실행

```bash
uvicorn fact_check_agent.api:app --reload
```

### API 엔드포인트

- POST `/api/v1/fact-check`
  - 요청 본문: `{"text": "검증할 텍스트"}`
  - 응답: `{"is_fact": true/false, "confidence": 0.95, "explanation": "설명"}`

### 다른 에이전트에서 서브에이전트로 사용

```python
from fact_check_agent.agent import FactCheckAgent

agent = FactCheckAgent()
result = agent.check_fact("검증할 텍스트")
```

## 라이선스

MIT License
