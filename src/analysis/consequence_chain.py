# src/analysis/consequence_chain.py
# HOIN Insight Chain of Consequence
# 목적: Trigger -> Final Beneficiary 인과 관계 강제 연결

class ConsequenceChain:
    @staticmethod
    def build(signal: dict) -> list:
        trigger = signal.get("trigger_event", "Market Shift")
        topic = signal.get("topic", "")
        
        # 기본 인과 체계 (v1.0 - 지표별 매핑 확장 가능)
        reaction = "시장 유동성/심리 변화"
        movement = "안전/위험 자산 간 자금 이동"
        beneficiary = "구조적 수혜 섹터"
        
        if any(x in topic.lower() for x in ["금리", "yield", "fomc"]):
            trigger = "금리 변동 및 통화 정책 변화"
            reaction = "기술주 밸류에이션 압박 및 금융 자산 재평가"
            movement = "성장주에서 가치주/현금성 자산으로 이동"
            beneficiary = "금융(은/보), 배당주, 현금 흐름 우수 기업"
        elif any(x in topic.lower() for x in ["oil", "wti", "energy", "유가"]):
            trigger = "에너지 가격 변동"
            reaction = "물가 상승 압력 및 운송 비중 높은 기업 비용 증가"
            movement = "소비재 자금 이탈 및 에너지 섹터 집중"
            beneficiary = "정유, 가스, 신재생 에너지, 자원 개발 기업"
            
        return [
            f"Trigger: {trigger}",
            f"Market Reaction: {reaction}",
            f"Capital Movement: {movement}",
            f"Final Beneficiary: {beneficiary}"
        ]
