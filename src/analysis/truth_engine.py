# src/analysis/truth_engine.py
# HOIN Insight Truth Engine (v3.0)
# 목적: 과거 성과(Outcome)를 분석하여 의사결정 가중치 및 신뢰도 보정

import json
import os
from pathlib import Path
from datetime import datetime, timedelta

class TruthEngine:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.perf_file = base_dir / "data/history/performance_state.json"
        self.outcome_log = base_dir / "data/history/outcome_log.json"
        self._ensure_files()

    def _ensure_files(self):
        if not self.perf_file.exists():
            default_state = {
                "weights": {"flow": 0.35, "price": 0.25, "event": 0.25, "consistency": 0.15},
                "calibration_factor": 1.0,
                "recent_hit_ratio": 0.5,
                "consecutive_failures": 0
            }
            self.perf_file.parent.mkdir(parents=True, exist_ok=True)
            self.perf_file.write_text(json.dumps(default_state, indent=2))
        
        if not self.outcome_log.exists():
            self.outcome_log.write_text(json.dumps([], indent=2))

    def track(self, signal: dict, analysis: dict):
        """오늘의 결정 사항을 추적 로그에 기록"""
        log = json.loads(self.outcome_log.read_text())
        
        entry = {
            "date": signal.get("date", datetime.now().strftime("%Y%m%d")),
            "topic": signal.get("topic"),
            "decision": analysis.get("decision_engine", {}).get("action", "WATCH"),
            "bull_probability": analysis.get("decision_engine", {}).get("bull_probability", 0.5),
            "confidence": analysis.get("decision_engine", {}).get("confidence", 0.0),
            "price_at_signal": signal.get("base_price", 0), # 시장 지표 기준가
            "status": "PENDING",
            "evaluated_at": None
        }
        
        log.append(entry)
        self.outcome_log.write_text(json.dumps(log[-100:], indent=2, ensure_ascii=False)) # 최근 100개 유지

    def get_calibrated_params(self) -> dict:
        """성과 기반으로 보정된 가중치와 신뢰도 계수 반환"""
        state = json.loads(self.perf_file.read_text())
        
        # 신뢰도 캘리브레이션: 최근 연속 실패가 많으면 신뢰도 자동 감소
        cf = 1.0
        if state["consecutive_failures"] >= 5:
            cf = 0.5  # 50% 패널티 (엄격한 조건 우선)
        elif state["consecutive_failures"] >= 3:
            cf = 0.7  # 30% 패널티
            
        return {
            "weights": state["weights"],
            "calibration_factor": cf
        }

    def update_performance(self, results: list):
        """TruthAgent로부터 전달받은 최신 평가 결과를 바탕으로 상태 업데이트"""
        state = json.loads(self.perf_file.read_text())
        
        # 1. 연속 실패 및 히트율 계산
        failures = 0
        hits = 0
        for r in results[-10:]: # 최근 10개 기준
            if r == "FAILURE": failures += 1
            if r == "SUCCESS": hits += 1
            
        state["recent_hit_ratio"] = hits / len(results[-10:]) if results else 0.5
        state["consecutive_failures"] = failures if results and results[-1] == "FAILURE" else 0
        
        # 2. 가중치 미세 조정 (피드백 루프 - Simplified)
        # 예: 최근 성공 케이스가 많으면 현재 가중치 유지, 실패 시 불확실 요소인 Event 비중 축소 등
        if failures > hits:
            state["weights"]["event"] = max(0.1, state["weights"]["event"] - 0.01)
            state["weights"]["flow"] = min(0.5, state["weights"]["flow"] + 0.01)
            
        self.perf_file.write_text(json.dumps(state, indent=2))
