# src/analysis/decision_engine.py
# HOIN Insight Analyst Decision Engine (v2.0)
# 목적: 분석 데이터를 바탕으로 Bull/Bear 시나리오와 Action(BUY/HOLD/WATCH) 결정

class DecisionEngine:
    @staticmethod
    def evaluate(signal: dict) -> dict:
        state = signal.get("flow_state", "UNKNOWN")
        strength = signal.get("extended_strength", 5.0)
        
        # 1. 태세 결정 (State & Strength 기반)
        action = "WATCH"
        confidence = 0.5
        best_scenario = "NEUTRAL"
        
        if state == "CONFIRMED_UPTREND":
            action = "BUY" if strength >= 8.5 else "HOLD"
            confidence = strength / 10.0
            best_scenario = "BULL"
        elif state == "STRONG_DISTRIBUTION":
            action = "WATCH" # 함정 구간이기에 현금 확보
            confidence = 0.8
            best_scenario = "BEAR"
        elif state == "LATE_ACCUMULATION":
            action = "BUY"
            confidence = 0.75
            best_scenario = "BULL"
        elif state == "CONFIRMED_DOWNTREND":
            action = "WATCH"
            confidence = 0.9
            best_scenario = "BEAR"

        # 2. 시나리오별 킬스위치 및 트리거 시간 조건 기초 데이터
        return {
            "action": action,
            "confidence": round(confidence, 2),
            "best_scenario": best_scenario,
            "decision_hint": f"State {state} / Strength {strength} 기반 결정"
        }
