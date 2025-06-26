import json
import requests
from typing import Dict, List
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import google_search


def extract_claims(text: str) -> Dict:
    """텍스트에서 검증 가능한 주장들을 추출합니다."""
    # 실제로는 더 정교한 클레임 추출 로직이 필요
    claims = []
    sentences = text.split(".")
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 10:  # 최소 길이 필터
            claims.append(sentence)

    return {
        "status": "success",
        "claims": claims[:5],  # 최대 5개 클레임만 처리
        "total_claims": len(claims),
    }


def search_fact_check_sources(claim: str) -> Dict:
    """특정 클레임에 대한 팩트체크 소스를 검색합니다."""
    try:
        # Google Custom Search API를 사용하여 팩트체크 사이트에서 검색
        search_query = (
            f"{claim} site:snopes.com OR site:factcheck.org OR site:politifact.com"
        )

        # 실제 구현에서는 Google Custom Search API 사용
        # 여기서는 모의 응답 제공
        mock_results = {
            "status": "success",
            "sources": [
                {
                    "title": f"Fact-check: {claim[:50]}...",
                    "url": "https://example-factcheck.com/article1",
                    "snippet": "According to verified sources, this claim requires further investigation...",
                    "source": "FactCheck.org",
                }
            ],
            "search_query": search_query,
        }

        return mock_results
    except Exception as e:
        return {"status": "error", "error_message": f"검색 중 오류 발생: {str(e)}"}


def verify_with_google_factcheck_api(claim: str) -> Dict:
    """Google Fact Check Tools API를 사용하여 기존 팩트체크 결과를 검색합니다."""
    try:
        # 실제 구현에서는 Google Fact Check Tools API 사용
        # https://factchecktools.googleapis.com/v1alpha1/claims:search

        # 모의 응답
        mock_response = {
            "status": "success",
            "fact_checks": [
                {
                    "claim": claim,
                    "rating": "MIXED",
                    "publisher": "Example Fact Checker",
                    "url": "https://example.com/factcheck",
                    "review_date": "2025-06-01",
                }
            ],
        }

        return mock_response
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"팩트체크 API 호출 중 오류: {str(e)}",
        }


# 클레임 추출 에이전트
claim_extractor = LlmAgent(
    name="claim_extractor",
    model="gemini-2.0-flash",
    description="텍스트에서 검증 가능한 사실적 주장들을 추출하는 에이전트",
    instruction="""
    주어진 텍스트를 분석하여 검증 가능한 사실적 주장들을 추출하세요.
    다음 기준을 따르세요:
    1. 구체적이고 검증 가능한 사실만 추출
    2. 의견이나 주관적 판단은 제외
    3. 날짜, 숫자, 인명, 지명 등이 포함된 구체적 주장 우선
    4. 각 주장을 명확하고 간결하게 표현
    5. 최대 5개의 주요 주장만 선별
    """,
    tools=[extract_claims],
    output_key="extracted_claims",
)

# 사실 검증 에이전트
fact_verifier = LlmAgent(
    name="fact_verifier",
    model="gemini-2.0-pro",
    description="추출된 주장들을 다양한 소스를 통해 검증하는 에이전트",
    instruction="""
    추출된 각 주장에 대해 다음 단계로 검증을 수행하세요:
    1. 신뢰할 수 있는 팩트체크 사이트에서 관련 정보 검색
    2. Google Fact Check API를 통한 기존 팩트체크 결과 확인
    3. 여러 소스의 정보를 종합하여 신뢰도 평가
    4. 각 주장을 '사실', '거짓', '부분적 사실', '검증 불가' 중 하나로 분류
    5. 판단 근거와 참조 소스 명시
    """,
    tools=[search_fact_check_sources, verify_with_google_factcheck_api, google_search],
    output_key="verification_results",
)

# 보고서 생성 에이전트
report_generator = LlmAgent(
    name="report_generator",
    model="gemini-2.0-flash",
    description="팩트체크 결과를 종합하여 최종 보고서를 생성하는 에이전트",
    instruction="""
    팩트체크 결과를 바탕으로 다음 형식의 종합 보고서를 작성하세요:
    
    ## 팩트체크 보고서
    
    ### 📋 분석 개요
    - 총 검증된 주장 수: X개
    - 사실: X개 | 거짓: X개 | 부분적 사실: X개 | 검증 불가: X개
    
    ### 🔍 상세 검증 결과
    각 주장별로:
    1. **주장**: [원문 주장]
    2. **판정**: [사실/거짓/부분적 사실/검증 불가]
    3. **근거**: [판정 이유와 참조 소스]
    4. **신뢰도**: [높음/중간/낮음]
    
    ### 📊 전체 평가
    - 텍스트의 전반적 신뢰도
    - 주요 문제점 및 권장사항
    """,
    output_key="final_report",
)

# 메인 팩트체크 에이전트 (순차 실행)
root_agent = SequentialAgent(
    name="fact_check_system",
    description="텍스트의 사실 여부를 종합적으로 검증하는 멀티 에이전트 시스템",
    instruction="""
    입력된 텍스트에 대해 다음 단계로 팩트체크를 수행합니다:
    1. 텍스트에서 검증 가능한 주장들을 추출
    2. 각 주장을 다양한 소스를 통해 검증
    3. 검증 결과를 종합하여 최종 보고서 생성
    
    정확하고 객관적인 분석을 제공하며, 모든 판단에 대한 근거를 명시합니다.
    """,
    sub_agents=[claim_extractor, fact_verifier, report_generator],
)
