# src/agents/extensions/flow_overlay.py
# HOIN Insight Flow Overlay Layer (v1.0)
# 목적: 수집된 Flow 데이터(외국인, ETF, 이벤트)를 시그널에 오버레이하여 신뢰도 검증

import json
import os
from pathlib import Path

class FlowOverlay:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.flow_dir = base_dir / "data/flow"

    def apply(self, signal: dict, all_data: dict = None) -> dict:
        """선정된 시그널에 Flow 데이터 오버레이 및 상태 판별 (v1.2 정밀화)"""
        # 0. 초기 필드 설정
        signal["flow_confirmation"] = False
        signal["flow_strength"] = 0.0
        signal["flow_direction"] = "outflow"
        signal["flow_state"] = "UNKNOWN"
        signal["flow_state_detail"] = "UNKNOWN"
        signal["flow_interpretation"] = ""
        signal["trigger_event"] = "none"
        signal["price_strength"] = "sideways"
        signal["flow_consistency"] = 0
        
        # 1. 데이터 로드
        flow_data = self._load_flow_data()
        if not flow_data:
            return signal

        # 2. Flow Vector 및 Consistency 계산 (v1.2)
        vectors = {"foreign": -1, "etf": -1, "domestic": 0} # Domestic은 추후 확장
        
        foreign = flow_data.get("foreign", {})
        if foreign.get("trend_3d") == "inflow":
            vectors["foreign"] = 1
        
        etf = flow_data.get("etf", {})
        if etf.get("KOSPI_ETF", {}).get("trend") == "inflow" or etf.get("SPY", {}).get("trend") == "inflow":
            vectors["etf"] = 1
            
        consistency = sum(vectors.values())
        signal["flow_consistency"] = consistency
        signal["flow_direction"] = "inflow" if consistency > 0 else "outflow"
        signal["flow_confirmation"] = consistency >= 1

        # 3. Price Direction 재정의 (v1.2)
        price_strength = self._infer_price_strength(signal, all_data)
        signal["price_strength"] = price_strength
        # 기존 up/down 호환용
        price_dir = "up" if "up" in price_strength else "down" if "down" in price_strength else "sideways"

        # 4. Flow State 및 Detail 결정
        state = self._classify_flow_state(price_dir, signal["flow_direction"])
        signal["flow_state"] = state
        signal["flow_state_detail"] = self._get_state_detail(state, price_strength, consistency)
        signal["flow_interpretation"] = self._get_interpretation(signal["flow_state_detail"])

        # 5. 이벤트 확인 (보너스 점수용)
        fs_bonus = 0.0
        events = flow_data.get("event", {}).get("events", [])
        high_impact_event = next((e for e in events if e.get("impact") == "high"), None)
        if high_impact_event:
            signal["trigger_event"] = high_impact_event.get("type", "macro")
            fs_bonus += 1.0

        # 6. State 기반 스코어링 (기존 구조 유지)
        state_bonus = 0.0
        if state == "CONFIRMED_UPTREND": state_bonus = 3.0
        elif state == "DISTRIBUTION": state_bonus = -3.0
        elif state == "ACCUMULATION": state_bonus = 2.0
        elif state == "CONFIRMED_DOWNTREND": state_bonus = -2.0

        # 최종 점수 보정
        base_score = signal.get("extended_strength", signal.get("strength", 5.0))
        final_score = base_score + state_bonus + fs_bonus
        
        signal["extended_strength"] = round(min(10.0, max(0.0, final_score)), 2)
        signal["flow_strength"] = abs(state_bonus)
        
        return signal

    def _infer_price_strength(self, signal: dict, all_data: dict) -> str:
        """Z-score와 Momentum을 결합한 가격 강도 판별 (v1.2)"""
        z = 0.0
        momentum = 0.0
        
        if all_data:
            stats = all_data.get("market", {}).get("data", {}).get("multi_period_stats", {})
            indicators = signal.get("key_indicators", [])
            if indicators and indicators[0] in stats:
                z = stats[indicators[0]].get("z_score_20d", 0.0)
                momentum = stats[indicators[0]].get("5d_change_pct", 0.0) # 3일 대신 5일 활용

        if z > 1.5 and momentum > 0: return "strong_up"
        elif z > 0 and momentum > 0: return "weak_up"
        elif z < -1.5 and momentum < 0: return "strong_down"
        elif z < 0 and momentum < 0: return "weak_down"
        else: return "sideways"

    def _classify_flow_state(self, price_dir: str, flow_dir: str) -> str:
        if price_dir == "up" and flow_dir == "inflow": return "CONFIRMED_UPTREND"
        elif price_dir == "up" and flow_dir == "outflow": return "DISTRIBUTION"
        elif price_dir == "down" and flow_dir == "inflow": return "ACCUMULATION"
        else: return "CONFIRMED_DOWNTREND"

    def _get_state_detail(self, state: str, price_strength: str, consistency: int) -> str:
        """상태 세분화 (v1.2)"""
        if state == "DISTRIBUTION":
            return "STRONG_DISTRIBUTION" if consistency <= -2 else "WEAK_DISTRIBUTION"
        elif state == "ACCUMULATION":
            return "LATE_ACCUMULATION" if price_strength == "weak_down" else "EARLY_ACCUMULATION"
        return state

    def _get_interpretation(self, detail: str) -> str:
        mapping = {
            "CONFIRMED_UPTREND": "강력한 유동성이 뒷받침되는 건강한 상승 추세",
            "STRONG_DISTRIBUTION": "가격 방어선이 무너지며 큰 자금이 본격적으로 이탈 중 (위험)",
            "WEAK_DISTRIBUTION": "상승세는 유지되나 자금 유입이 둔화되며 고점 징후 포착",
            "EARLY_ACCUMULATION": "급락을 틈타 스마트머니가 조용히 매집을 시작한 단계",
            "LATE_ACCUMULATION": "하락세가 진정되며 본격적인 반등을 위한 자금 응집 단계",
            "CONFIRMED_DOWNTREND": "자금 이탈과 가격 하락이 동반되는 전형적인 약세장"
        }
        return mapping.get(detail, "시장 상태 데이터 분석 중")

    def _load_flow_data(self) -> dict:
        data = {}
        paths = {
            "foreign": self.flow_dir / "foreign_flow.json",
            "etf": self.flow_dir / "etf_flow.json",
            "event": self.flow_dir / "event_calendar.json"
        }
        for key, p in paths.items():
            if p.exists():
                try:
                    data[key] = json.loads(p.read_text())
                except: pass
        return data

    def _load_flow_data(self) -> dict:
        data = {}
        paths = {
            "foreign": self.flow_dir / "foreign_flow.json",
            "etf": self.flow_dir / "etf_flow.json",
            "event": self.flow_dir / "event_calendar.json"
        }
        for key, p in paths.items():
            if p.exists():
                try:
                    data[key] = json.loads(p.read_text())
                except: pass
        return data
