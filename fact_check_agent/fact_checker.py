from typing import Dict, Any, Tuple
from google.cloud import aiplatform
from google.cloud.aiplatform.matching_engine import MatchingEngineIndexEndpoint
from google.cloud import ai_generativelanguage as genai
import os


class FactChecker:
    def __init__(self):
        """팩트체크 에이전트 초기화"""
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = "us-central1"  # Google Cloud 리전
        self.index_endpoint = None
        self.model = None
        self._initialize_components()

    def _initialize_components(self):
        """Google Cloud 컴포넌트 초기화"""
        # Vertex AI 초기화
        aiplatform.init(project=self.project_id, location=self.location)

        # Gemini Pro 모델 초기화
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel("gemini-pro")

    async def check_fact(self, text: str) -> Tuple[bool, float, str]:
        """
        주어진 텍스트의 사실 여부를 검증합니다.

        Args:
            text (str): 검증할 텍스트

        Returns:
            Tuple[bool, float, str]: (사실 여부, 신뢰도, 설명)
        """
        # Gemini Pro를 사용하여 팩트체크 수행
        prompt = f"""
        다음 문장의 사실 여부를 검증해주세요:
        "{text}"
        
        다음 형식으로 응답해주세요:
        1. 사실 여부 (true/false)
        2. 신뢰도 (0.0-1.0)
        3. 설명 (왜 그렇게 판단했는지)
        """

        response = await self.model.generate_content_async(prompt)
        result = response.text.strip().split("\n")

        is_fact = result[0].lower() == "true"
        confidence = float(result[1])
        explanation = result[2]

        return is_fact, confidence, explanation

    async def verify_with_sources(
        self, text: str, sources: list[str]
    ) -> Dict[str, Any]:
        """
        주어진 소스들을 참고하여 텍스트의 사실 여부를 검증합니다.

        Args:
            text (str): 검증할 텍스트
            sources (list[str]): 참고할 소스 텍스트 목록

        Returns:
            Dict[str, Any]: 검증 결과
        """
        sources_text = "\n".join(
            [f"소스 {i+1}: {source}" for i, source in enumerate(sources)]
        )

        prompt = f"""
        다음 문장의 사실 여부를 주어진 소스들을 참고하여 검증해주세요:

        검증할 문장:
        "{text}"

        참고할 소스들:
        {sources_text}

        다음 형식으로 응답해주세요:
        1. 사실 여부 (true/false)
        2. 신뢰도 (0.0-1.0)
        3. 설명 (왜 그렇게 판단했는지)
        4. 참고한 소스 번호
        """

        response = await self.model.generate_content_async(prompt)
        result = response.text.strip().split("\n")

        return {
            "is_fact": result[0].lower() == "true",
            "confidence": float(result[1]),
            "explanation": result[2],
            "referenced_sources": [int(s.strip()) for s in result[3].split(",")],
        }
