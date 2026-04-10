# tests/test_filters.py

import pytest
from pathlib import Path
from src.core.filters import SignalFilters

FIXTURES = Path(__file__).parent / "fixtures"


class TestFilter2Paradox:
    def setup_method(self):
        self.f = SignalFilters()

    def test_war_news_but_market_up(self):
        """전쟁 뉴스인데 KOSPI 급등 — 역설 감지"""
        market = {"data": {"kospi_1d_change": 3.5, "usd_krw": 1480}}
        sentiment = {"data": {"news_headlines": [
            {"title": "미국-이란 전쟁 확전 우려 고조"}
        ], "authority_signals": []}}
        hit, details = self.f.filter2_paradox(market, sentiment)
        assert hit is True

    def test_normal_market_no_paradox(self):
        """평시 시장 — 역설 없음"""
        market = {"data": {"kospi_1d_change": 0.5}}
        sentiment = {"data": {"news_headlines": [], "authority_signals": []}}
        hit, details = self.f.filter2_paradox(market, sentiment)
        assert hit is False

    def test_high_oil_but_kospi_up(self):
        """유가 폭등인데 KOSPI 상승 — 역설 감지"""
        market = {"data": {"wti_oil": 100.0, "kospi_1d_change": 2.0}}
        sentiment = {"data": {"news_headlines": [], "authority_signals": []}}
        hit, details = self.f.filter2_paradox(market, sentiment)
        assert hit is True


class TestFilter3Mispricing:
    def setup_method(self):
        self.f = SignalFilters()

    def test_high_exchange_rate_mispricing(self):
        """환율 급등 → 미반영 격차 감지"""
        market = {"data": {"usd_krw": 1500, "wti_oil": 100}}
        sentiment = {"data": {"news_headlines": [], "authority_signals": []}}
        hit, details = self.f.filter3_mispricing(market, sentiment)
        assert hit is True

    def test_normal_exchange_no_mispricing(self):
        """정상 환율 — 미반영 없음"""
        market = {"data": {"usd_krw": 1300, "wti_oil": 70}}
        sentiment = {"data": {"news_headlines": [], "authority_signals": []}}
        hit, details = self.f.filter3_mispricing(market, sentiment)
        assert hit is False

    def test_defense_news_mispricing(self):
        """방산 뉴스 → 부품주 미반영 감지"""
        market = {"data": {"usd_krw": 1300, "wti_oil": 70}}
        sentiment = {"data": {"news_headlines": [
            {"title": "한화에어로스페이스 미사일 방산 수출 대형 계약"}
        ], "authority_signals": []}}
        hit, details = self.f.filter3_mispricing(market, sentiment)
        assert hit is True


class TestFilter5CausalChain:
    def setup_method(self):
        self.f = SignalFilters()

    def test_war_oil_chain(self):
        """중동 전쟁 → 유가 → 제조업 연결고리"""
        market = {"data": {"usd_krw": 1480, "wti_oil": 102}}
        sentiment = {"data": {"news_headlines": [
            {"title": "이란 전쟁 호르무즈 해협 봉쇄 지속"}
        ], "authority_signals": []}}
        hit, details = self.f.filter5_causal_chain(market, sentiment)
        assert hit is True

    def test_exchange_rate_chain(self):
        """환율 급등 연결고리"""
        market = {"data": {"usd_krw": 1520, "wti_oil": 80}}
        sentiment = {"data": {"news_headlines": [], "authority_signals": []}}
        hit, details = self.f.filter5_causal_chain(market, sentiment)
        assert hit is True

    def test_low_exchange_no_chain(self):
        """정상 환율 — 연결고리 없음"""
        market = {"data": {"usd_krw": 1300, "wti_oil": 70}}
        sentiment = {"data": {"news_headlines": [], "authority_signals": []}}
        hit, details = self.f.filter5_causal_chain(market, sentiment)
        assert hit is False


class TestFilter7UncorrelatedSector:
    def setup_method(self):
        self.f = SignalFilters()

    def test_defense_in_falling_market(self):
        """하락장에 방산 뉴스 — 공포 무관 섹터"""
        market = {"data": {"kospi_1d_change": -2.5, "vix": 25}}
        sentiment = {"data": {"news_headlines": [
            {"title": "한화에어로스페이스 미사일 수출 계약"}
        ], "authority_signals": []}}
        hit, details = self.f.filter7_uncorrelated_sector(market, sentiment)
        assert hit is True

    def test_no_trigger_in_rising_market(self):
        """상승장 — 공포 무관 섹터 미감지"""
        market = {"data": {"kospi_1d_change": 2.0, "vix": 15}}
        sentiment = {"data": {"news_headlines": [], "authority_signals": []}}
        hit, details = self.f.filter7_uncorrelated_sector(market, sentiment)
        assert hit is False

    def test_vix_fearful_triggers_sector(self):
        """VIX 고점 + 바이오 뉴스 — 공포 무관 감지"""
        market = {"data": {"kospi_1d_change": 0.0, "vix": 30}}
        sentiment = {"data": {"news_headlines": [
            {"title": "셀트리온 신약 FDA 승인 임상 완료"}
        ], "authority_signals": []}}
        hit, details = self.f.filter7_uncorrelated_sector(market, sentiment)
        assert hit is True
