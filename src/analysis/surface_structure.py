# src/analysis/surface_structure.py
# HOIN Insight Surface vs Structure Layer
# 목적: 뉴스 표면과 실제 자본 구조 분리

class SurfaceStructureLayer:
    @staticmethod
    def analyze(signal: dict) -> dict:
        surface = signal.get("topic", "정보 없음")
        
        # Structure 생성 규칙 (v1.0)
        state = signal.get("flow_state", "UNKNOWN")
        strength = signal.get("price_strength", "sideways")
        
        structure = "데이터 기반 구조 분석 중"
        
        if state == "CONFIRMED_UPTREND":
            structure = "가격 상승과 자금 유입이 일치하는 건강한 추세 구조"
        elif state == "DISTRIBUTION":
            structure = "가격은 오르지만 내부 자금은 이탈하는 붕괴 전조 구조"
        elif state == "ACCUMULATION":
            structure = "가격 하락을 이용해 저가 매수세가 결집되는 기회 구조"
        elif state == "CONFIRMED_DOWNTREND":
            structure = "자금과 가격이 동반 하락하는 구조적 약세장"
        
        if "strong" in strength:
            structure += " (에너지 집중됨)"
            
        return {
            "surface": surface,
            "structure": structure
        }
