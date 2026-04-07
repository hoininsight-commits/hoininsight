# tests/test_detector.py
# AGENT-03 DETECTOR 검증

import json
import pytest
from pathlib import Path


FIXTURES = Path(__file__).parent / "fixtures"


class TestDetectorFilters:
    """7개 필터 로직 검증"""

    def setup_method(self):
        self.raw_data = {
            "market": json.loads((FIXTURES / "mock_market.json").read_text()),
            "macro": json.loads((FIXTURES / "mock_macro.json").read_text()),
            "sentiment": json.loads((FIXTURES / "mock_sentiment.json").read_text()),
        }

    def test_filter1_high_exchange_rate(self):
        """환율 1400 이상이면 필터1 적중"""
        from src.core.filters import SignalFilters
        f = SignalFilters()
        market = self.raw_data["market"]
        macro = self.raw_data["macro"]
        hit, details = f.filter1_historical_threshold(market, macro)
        assert hit is True
        assert len(details) > 0

    def test_strength_calculation(self):
        """필터 2개 이상이면 강도 4.0 이상"""
        from src.core.filters import SignalFilters
        f = SignalFilters()
        filters_hit = ["필터1_역사적임계값", "필터4_시의성"]
        strength = f.calculate_strength(filters_hit)
        assert strength >= 4.0

    def test_content_type_longform(self):
        """강도 8.0 이상이면 롱폼"""
        from src.core.filters import SignalFilters
        f = SignalFilters()
        assert f.determine_content_type(8.2) == "롱폼"

    def test_content_type_shorts(self):
        """강도 6.0~7.9이면 쇼츠"""
        from src.core.filters import SignalFilters
        f = SignalFilters()
        assert f.determine_content_type(6.5) == "쇼츠"

    def test_content_type_rejected(self):
        """강도 4.0 미만이면 탈락"""
        from src.core.filters import SignalFilters
        f = SignalFilters()
        assert f.determine_content_type(3.0) == "탈락"


class TestSignalSchema:
    """today_signal.json 스키마 검증"""

    def test_mock_signal_required_fields(self):
        """신호 JSON 필수 필드 존재 여부"""
        signal = json.loads((FIXTURES / "mock_signal.json").read_text())

        required = [
            "date", "topic", "strength", "content_type",
            "filters_hit", "level2_chain", "is_republish", "urgency"
        ]
        for field in required:
            assert field in signal, f"필수 필드 누락: {field}"

    def test_signal_strength_range(self):
        """신호 강도는 0~10 사이"""
        signal = json.loads((FIXTURES / "mock_signal.json").read_text())
        assert 0 <= signal["strength"] <= 10

    def test_signal_content_type_valid(self):
        """콘텐츠 유형은 롱폼 또는 쇼츠"""
        signal = json.loads((FIXTURES / "mock_signal.json").read_text())
        assert signal["content_type"] in ["롱폼", "쇼츠"]

    def test_level2_chain_not_empty(self):
        """레벨2 체인은 비어있으면 안 됨"""
        signal = json.loads((FIXTURES / "mock_signal.json").read_text())
        assert len(signal["level2_chain"]) >= 3
