# src/core/filters.py

import json
from pathlib import Path

class SignalFilters:
    """
    [AGNOSTIC PIPELINE]
    This class now only provides mathematical anomaly detection.
    All human-curated keyword guidelines (crisis, war, AI, etc.) have been removed.
    Narrative deduction is left entirely to the Arbiter LLM based on dynamic trend keywords.
    """

    def __init__(self, filter_weights_path: str = "data/learning/filter_weights.json"):
        self.weights = self._load_weights(filter_weights_path)

    def _load_weights(self, path: str) -> dict:
        default = {
            "필터1_역사적임계값": 1.5,
            "필터2_수급역설": 1.3,
            "필터3_변동성괴리": 1.4
        }
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return default

    # ──────────────────────────────────────────
    # 필터1: 수학적 임계값 돌파 (수치 기반)
    # ──────────────────────────────────────────
    def filter1_historical_threshold(self, market: dict) -> tuple:
        hits = []
        data = market.get("data", {})

        usd_krw = data.get("usd_krw", 0)
        if usd_krw and usd_krw > 1400:
            hits.append(f"환율 {usd_krw:.0f}원 — 수학적 위험 구간")

        vix = data.get("vix", 0)
        if vix and vix > 25:
            hits.append(f"VIX {vix:.1f} — 변동성 임계치 돌파")

        wti = data.get("wti_oil", 0)
        if wti and wti > 90:
            hits.append(f"WTI ${wti:.1f} — 고유가 임계치 돌파")

        fg = data.get("fear_greed_index", 50)
        if fg and fg < 20:
            hits.append(f"Fear&Greed {fg:.0f} — 극단적 공포")

        return (len(hits) > 0, hits)

    # ──────────────────────────────────────────
    # 필터2: 가격과 수급의 수학적 역설
    # ──────────────────────────────────────────
    def filter2_flow_paradox(self, market: dict) -> tuple:
        hits = []
        mdata = market.get("data", {})

        kospi_chg = mdata.get("kospi_1d_change", 0)
        kospi_foreign = mdata.get("kospi_foreign_net", None)
        usd_krw = mdata.get("usd_krw", 0)

        # 역설: 지수 급락인데 외국인 대량 순매수
        if kospi_chg and kospi_chg < -1.5 and kospi_foreign and kospi_foreign > 0:
            hits.append(f"지수 {kospi_chg:.1f}% 하락 중 외국인 순매수(수급 역설)")

        # 역설: 환율 폭등인데 외국인 순매수
        if usd_krw and usd_krw > 1450 and kospi_foreign and kospi_foreign > 0:
            hits.append(f"환율 {usd_krw:.0f}원 급등 중 외국인 순매수(수급 역설)")

        return (len(hits) > 0, hits)

    # ──────────────────────────────────────────
    # 필터3: 다중 자산 간 변동성 괴리
    # ──────────────────────────────────────────
    def filter3_volatility_divergence(self, market: dict) -> tuple:
        hits = []
        mdata = market.get("data", {})

        vix = mdata.get("vix", 0)
        gold = mdata.get("gold", 0)
        
        # 안전자산(금)과 위험지표(VIX) 동반 급등
        if vix and vix > 25 and gold and gold > 2500:
             hits.append(f"VIX({vix:.1f})와 금({gold:.0f}) 동반 상승 (안전자산 쏠림 현상)")

        return (len(hits) > 0, hits)

    # ──────────────────────────────────────────
    # 강도 계산
    # ──────────────────────────────────────────
    def calculate_strength(self, filters_hit: list, usd_krw: float = 0.0, vix: float = 0.0) -> float:
        if not filters_hit: return 0.0
        base = len(filters_hit) * 2.0
        weight_bonus = sum(self.weights.get(f, 1.0) for f in filters_hit)
        magnitude_bonus = 0.0
        if usd_krw > 1500: magnitude_bonus += 1.0
        if vix > 25: magnitude_bonus += 0.5
        return min(base + weight_bonus * 0.5 + magnitude_bonus, 10.0)

    def determine_content_type(self, strength: float) -> str:
        if strength >= 8.0: return "롱폼"
        elif strength >= 6.0: return "쇼츠"
        elif strength >= 4.0: return "후보"
        else: return "탈락"

    def run_all_filters(self, raw_data: dict) -> dict:
        market = raw_data.get("market", {})
        
        results = {}
        all_hits = []

        checks = [
            ("필터1_역사적임계값", self.filter1_historical_threshold(market)),
            ("필터2_수급역설",     self.filter2_flow_paradox(market)),
            ("필터3_변동성괴리",   self.filter3_volatility_divergence(market))
        ]

        for name, (hit, details) in checks:
            results[name] = {"hit": hit, "details": details}
            if hit:
                all_hits.append(name)

        strength = self.calculate_strength(all_hits)
        content_type = self.determine_content_type(strength)

        return {
            "filters_hit": all_hits,
            "filter_results": results,
            "strength": round(strength, 1),
            "content_type": content_type
        }
