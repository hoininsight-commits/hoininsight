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
        """선정된 시그널에 Flow 데이터 오버레이 및 상태 판별 (v1.1)"""
        # 0. 초기 필드 설정
        signal["flow_confirmation"] = False
        signal["flow_strength"] = 0.0
        signal["flow_direction"] = "outflow"
        signal["flow_state"] = "UNKNOWN"
        signal["flow_interpretation"] = ""
        signal["trigger_event"] = "none"
        
        # 1. 데이터 로드
        flow_data = self._load_flow_data()
        if not flow_data:
            return signal

        # 2. 자금 흐름 로직 적용
        fs_bonus = 0.0
        
        # A. 외국인 수급 확인
        foreign = flow_data.get("foreign", {})
        if foreign.get("trend_3d") == "inflow":
            signal["flow_confirmation"] = True
            signal["flow_direction"] = "inflow"
        
        # B. ETF 방향 확인
        etf = flow_data.get("etf", {})
        if etf.get("KOSPI_ETF", {}).get("trend") == "inflow":
            signal["flow_confirmation"] = True
            signal["flow_direction"] = "inflow"

        # C. 이벤트 확인
        events = flow_data.get("event", {}).get("events", [])
        high_impact_event = next((e for e in events if e.get("impact") == "high"), None)
        if high_impact_event:
            signal["trigger_event"] = high_impact_event.get("type", "macro")
            fs_bonus += 1.0

        # 3. Flow State 판별 (v1.1 핵심)
        price_dir = self._infer_price_direction(signal, all_data)
        flow_dir = signal["flow_direction"]
        
        state = self._classify_flow_state(price_dir, flow_dir)
        signal["flow_state"] = state
        signal["flow_interpretation"] = self._get_interpretation(state)

        # 4. State 기반 스코어링 변경 (v1.1)
        state_bonus = 0.0
        if state == "CONFIRMED_UPTREND":
            state_bonus = 3.0
        elif state == "DISTRIBUTION":
            state_bonus = -3.0
        elif state == "ACCUMULATION":
            state_bonus = 2.0
        elif state == "CONFIRMED_DOWNTREND":
            state_bonus = -2.0

        # 최종 점수 보정
        base_score = signal.get("extended_strength", signal.get("strength", 5.0))
        final_score = base_score + state_bonus + fs_bonus
        
        signal["extended_strength"] = round(min(10.0, max(0.0, final_score)), 2)
        signal["flow_strength"] = abs(state_bonus) # 절댓값으로 유효성 표시
        
        return signal

    def _infer_price_direction(self, signal: dict, all_data: dict) -> str:
        """시그널과 데이터로부터 가격 방향성(up/down) 추론"""
        topic = signal.get("topic", "").lower()
        if any(w in topic for w in ["상승", "신고가", "rally", "surge", "상향"]):
            return "up"
        if any(w in topic for w in ["하락", "신저가", "rout", "sink", "하향"]):
            return "down"
            
        # Z-score 기반 추론
        if all_data:
            stats = all_data.get("market", {}).get("data", {}).get("multi_period_stats", {})
            indicators = signal.get("key_indicators", [])
            if indicators and indicators[0] in stats:
                z = stats[indicators[0]].get("z_score_20d", 0.0)
                return "up" if z > 0 else "down"
        
        return "up" # Default

    def _classify_flow_state(self, price_dir: str, flow_dir: str) -> str:
        if price_dir == "up" and flow_dir == "inflow":
            return "CONFIRMED_UPTREND"
        elif price_dir == "up" and flow_dir == "outflow":
            return "DISTRIBUTION"
        elif price_dir == "down" and flow_dir == "inflow":
            return "ACCUMULATION"
        else:
            return "CONFIRMED_DOWNTREND"

    def _get_interpretation(self, state: str) -> str:
        mapping = {
            "CONFIRMED_UPTREND": "스마트머니의 유입이 가격 상승을 강력하게 지지함 (신뢰도 높음)",
            "DISTRIBUTION": "가격은 오르지만 큰 손들은 털고 나가는 중 (추세 전환 주의)",
            "ACCUMULATION": "가격 하락을 이용해 매집이 일어나는 구간 (바닥권 형성 가능성)",
            "CONFIRMED_DOWNTREND": "자금 이탈과 가격 하락이 동반되는 투매 구간 (추가 하락 위험)"
        }
        return mapping.get(state, "시장 상태 판별 불가")

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
