from typing import Dict, Any, Optional
from google.cloud.aiplatform import Agent
from .fact_checker import FactChecker


class FactCheckAgent(Agent):
    """Google ADK 기반 팩트체크 에이전트"""

    def __init__(self):
        """에이전트 초기화"""
        super().__init__()
        self.fact_checker = FactChecker()

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        에이전트 요청 처리

        Args:
            request (Dict[str, Any]): 요청 데이터
                - text: 검증할 텍스트
                - sources: (선택사항) 참고할 소스 목록

        Returns:
            Dict[str, Any]: 응답 데이터
        """
        text = request.get("text")
        sources = request.get("sources")

        if not text:
            return {"error": "검증할 텍스트가 제공되지 않았습니다.", "status": "error"}

        try:
            if sources:
                result = await self.fact_checker.verify_with_sources(text, sources)
            else:
                is_fact, confidence, explanation = await self.fact_checker.check_fact(
                    text
                )
                result = {
                    "is_fact": is_fact,
                    "confidence": confidence,
                    "explanation": explanation,
                }

            return {"status": "success", "result": result}

        except Exception as e:
            return {"error": str(e), "status": "error"}

    async def check_fact(
        self, text: str, sources: Optional[list[str]] = None
    ) -> Dict[str, Any]:
        """
        텍스트의 사실 여부를 검증하는 편의 메서드

        Args:
            text (str): 검증할 텍스트
            sources (Optional[list[str]]): 참고할 소스 목록

        Returns:
            Dict[str, Any]: 검증 결과
        """
        request = {"text": text}
        if sources:
            request["sources"] = sources

        return await self.handle_request(request)
