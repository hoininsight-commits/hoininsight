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

    def apply(self, signal: dict) -> dict:
        """선정된 시그널에 Flow 데이터 오버레이 (Add-only)"""
        # 0. 초기 필드 설정
        signal["flow_confirmation"] = False
        signal["flow_strength"] = 0.0
        signal["flow_direction"] = "outflow"
        signal["trigger_event"] = "none"
        
        # 1. 데이터 로드
        flow_data = self._load_flow_data()
        if not flow_data:
            signal["extended_strength"] = round(max(0.0, signal.get("extended_strength", signal.get("strength", 0)) - 1.0), 2)
            return signal

        # 2. 로직 적용
        fs = 0.0
        
        # A. 외국인 수급 확인
        foreign = flow_data.get("foreign", {})
        if foreign.get("trend_3d") == "inflow":
            signal["flow_confirmation"] = True
            fs += 2.5
            signal["flow_direction"] = "inflow"
        
        # B. ETF 방향 확인
        etf = flow_data.get("etf", {})
        if etf.get("KOSPI_ETF", {}).get("trend") == "inflow":
            fs += 1.5
            if not signal["flow_confirmation"]: # ETF라도 들어오면 컨펌으로 인정
                 signal["flow_confirmation"] = True
                 signal["flow_direction"] = "inflow"

        # C. 이벤트 확인
        events = flow_data.get("event", {}).get("events", [])
        high_impact_event = next((e for e in events if e.get("impact") == "high"), None)
        if high_impact_event:
            signal["trigger_event"] = high_impact_event.get("type", "macro")
            fs += 1.0
            # why_now_hint 보강
            hint = signal.get("why_now_hint", "")
            if not hint:
                signal["why_now_hint"] = f"주요 이벤트({high_impact_event.get('name')})와 결합된 자금 흐름"

        # 3. 최종 점수 정규화 (10점 만점 기준 보조 지표)
        signal["flow_strength"] = round(fs, 1)
        
        # 4. select_best 결과에 대한 가점/감점 (Extended Strength 보정)
        base_score = signal.get("extended_strength", signal.get("strength", 5.0))
        
        if not signal["flow_confirmation"]:
            # Flow가 뒷받침되지 않는 Anomaly는 패널티 부여 (Weak Signal)
            final_score = base_score - 1.5
        else:
            final_score = base_score + (fs * 0.2) # Flow 비중에 따른 가점

        signal["extended_strength"] = round(min(10.0, max(0.0, final_score)), 2)
        
        return signal

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
