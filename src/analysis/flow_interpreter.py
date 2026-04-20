# src/analysis/flow_interpreter.py
# HOIN Insight Flow Interpreter (Analyst Extension)
# 목적: Detector의 Flow 상태를 "경제사냥꾼 언어"로 변환

class FlowInterpreter:
    @staticmethod
    def interpret(signal: dict) -> str:
        state = signal.get("flow_state", "UNKNOWN")
        detail = signal.get("flow_state_detail", state)
        
        mapping = {
            "CONFIRMED_UPTREND": "진짜 돈이 붙은 상승 (추세 지속 가능 구간)",
            "WEAK_DISTRIBUTION": "상승세는 유지되나 자금 유입이 둔화되는 고점 징후",
            "STRONG_DISTRIBUTION": "가격은 오르지만 큰 손들은 이미 털고 나가는 함정(Trap) 구간",
            "EARLY_ACCUMULATION": "가격은 빠지지만 큰 손들은 담기 시작한 기회 초기 단계",
            "LATE_ACCUMULATION": "바닥 형성 후 자금이 응집되는 폭발 직전 단계",
            "CONFIRMED_DOWNTREND": "자금 이탈과 하락이 동반되는 리스크 확대 구간",
            "ACCUMULATION": "자본이 유입되는 매집 구간",
            "DISTRIBUTION": "자본이 이탈하는 분매 구간"
        }
        
        return mapping.get(detail, mapping.get(state, "자금 흐름의 의도를 분석 중인 단계"))
