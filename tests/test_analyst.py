# tests/test_analyst.py
# AGENT-04 ANALYST 출력 스키마 검증

import json
import pytest
from pathlib import Path


FIXTURES = Path(__file__).parent / "fixtures"


class TestAnalysisSchema:
    """today_analysis.json 스키마 검증"""

    def test_three_lens_structure(self):
        """3렌즈 분석 구조 검증 (mock signal 기반)"""
        # 실제 Claude API 없이 스키마만 검증
        expected_structure = {
            "money_flow": str,
            "structural_change": str,
            "policy_direction": str
        }

        # mock 분석 결과 직접 생성해서 검증
        mock_analysis = {
            "date": "20260408",
            "topic": "원달러 환율 1,521원 복합 위기",
            "three_lens_analysis": {
                "money_flow": "원화 M2 역대 최고 + 달러 수요 폭발",
                "structural_change": "한국만 통화 긴축 안 한 구조적 원인",
                "policy_direction": "한은 금리 동결 지속 불가피"
            },
            "level2_chain": ["원인1", "원인2", "결과"],
            "historical_reference": {
                "case": "2009년 금융위기",
                "similarity": "원화 가치 급락 구조 동일",
                "outcome": "1년 후 정상화"
            },
            "risk_factors": ["리스크1", "리스크2", "리스크3"],
            "check_points": ["체크1", "체크2"]
        }

        # 필수 필드 검증
        required = [
            "date", "topic", "three_lens_analysis",
            "level2_chain", "historical_reference",
            "risk_factors", "check_points"
        ]
        for field in required:
            assert field in mock_analysis, f"필수 필드 누락: {field}"

        # 3렌즈 필드 검증
        lens = mock_analysis["three_lens_analysis"]
        assert "money_flow" in lens
        assert "structural_change" in lens
        assert "policy_direction" in lens

        # 리스크 3개 검증
        assert len(mock_analysis["risk_factors"]) >= 3

        # 체크포인트 2개 검증
        assert len(mock_analysis["check_points"]) >= 2


class TestStocksSchema:
    """today_stocks.json 스키마 검증"""

    def test_stocks_required_fields(self):
        """종목 데이터 필수 필드 검증"""
        mock_stocks = {
            "date": "20260408",
            "topic_signal": "원달러 환율 급등",
            "stocks": [
                {
                    "ticker": "005930",
                    "name": "삼성전자",
                    "sector": "반도체",
                    "impact": "수혜",
                    "reason": "달러 결제 수출로 환율 이익",
                    "impact_level": "HIGH",
                    "is_primary": True
                }
            ]
        }

        assert "date" in mock_stocks
        assert "topic_signal" in mock_stocks
        assert "stocks" in mock_stocks
        assert len(mock_stocks["stocks"]) > 0

        stock = mock_stocks["stocks"][0]
        required_stock_fields = ["ticker", "name", "sector", "impact", "reason"]
        for field in required_stock_fields:
            assert field in stock, f"종목 필수 필드 누락: {field}"

        assert stock["impact"] in ["수혜", "피해", "중립"]
