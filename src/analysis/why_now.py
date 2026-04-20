# src/analysis/why_now.py
# HOIN Insight Hunter Why Now
# 목적: 자본이 움직일 수밖에 없는 "지금"의 이유 설명

class WhyNowProjector:
    @staticmethod
    def project(signal: dict) -> str:
        state = signal.get("flow_state", "UNKNOWN")
        trigger = signal.get("trigger_event", "none")
        hint = signal.get("why_now_hint", "")
        
        reason = "현재 시장 지표의 이탈과 자금 흐름이 결합되는 분기점입니다."
        
        if trigger != "none":
            reason = f"주요 이벤트({trigger})를 기점으로 자금의 성격이 변하고 있으며, {hint or '수급 불균형'}이 발생하고 있습니다."
            
        if state == "STRONG_DISTRIBUTION":
            reason += " 가격 상승의 에너지가 고갈되고 큰 자본이 엑시트하는 타이밍입니다."
        elif state == "EARLY_ACCUMULATION":
            reason += " 대중의 공포와 달리 스마트머니의 저성 매수세가 포착되는 초기 구간입니다."
            
        return reason
