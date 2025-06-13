from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from .agent import FactCheckAgent

app = FastAPI(
    title="Fact Check Agent API",
    description="Google ADK 기반 팩트체크 에이전트 API",
    version="0.1.0",
)


# API 요청/응답 모델
class FactCheckRequest(BaseModel):
    text: str
    sources: Optional[List[str]] = None


class FactCheckResponse(BaseModel):
    status: str
    result: Optional[dict] = None
    error: Optional[str] = None


# 에이전트 인스턴스 생성
agent = FactCheckAgent()


@app.post("/api/v1/fact-check", response_model=FactCheckResponse)
async def fact_check(request: FactCheckRequest) -> FactCheckResponse:
    """
    텍스트의 사실 여부를 검증하는 API 엔드포인트

    Args:
        request (FactCheckRequest): 검증 요청 데이터

    Returns:
        FactCheckResponse: 검증 결과
    """
    try:
        result = await agent.check_fact(request.text, request.sources)
        return FactCheckResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """API 서버 상태 확인"""
    return {"status": "healthy"}
