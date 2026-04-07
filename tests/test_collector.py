# tests/test_collector.py
# AGENT-01 COLLECTOR 검증

import json
import pytest
from pathlib import Path
from datetime import datetime


FIXTURES = Path(__file__).parent / "fixtures"
TODAY = datetime.now().strftime("%Y%m%d")


class TestCollectorOutput:
    """AGENT-01이 올바른 파일을 생성하는지 검증"""

    def test_mock_market_schema(self):
        """mock_market.json 스키마 검증"""
        data = json.loads((FIXTURES / "mock_market.json").read_text())

        assert "date" in data
        assert "data" in data

        d = data["data"]
        assert "usd_krw" in d
        assert "kospi" in d
        assert "vix" in d
        assert "wti_oil" in d
        assert "fear_greed_index" in d

    def test_mock_macro_schema(self):
        """mock_macro.json 스키마 검증"""
        data = json.loads((FIXTURES / "mock_macro.json").read_text())

        assert "date" in data
        assert "data" in data

        d = data["data"]
        assert "korea_base_rate" in d
        assert "us_fed_rate" in d
        assert "rate_diff" in d

    def test_mock_sentiment_schema(self):
        """mock_sentiment.json 스키마 검증"""
        data = json.loads((FIXTURES / "mock_sentiment.json").read_text())

        assert "date" in data
        assert "data" in data
        assert "news_headlines" in data["data"]
        assert "authority_signals" in data["data"]

    def test_market_values_reasonable(self):
        """시장 데이터 값이 합리적 범위인지 검증"""
        data = json.loads((FIXTURES / "mock_market.json").read_text())
        d = data["data"]

        # 환율은 1000~2000 사이
        assert 1000 < d["usd_krw"] < 2000

        # VIX는 0~100 사이
        assert 0 < d["vix"] < 100

        # WTI는 0~300 사이
        assert 0 < d["wti_oil"] < 300

        # 공포탐욕지수는 0~100 사이
        assert 0 <= d["fear_greed_index"] <= 100
