# src/analysis/beneficiary_mapper.py
# HOIN Insight Theme vs Structural Beneficiary
# 목적: 단순 테마주와 실제 구조적 수혜주 분리

class BeneficiaryMapper:
    @staticmethod
    def map(signal: dict) -> dict:
        topic = signal.get("topic", "")
        
        theme = "뉴스 관련 시장 테마주"
        structural = "장기적 구조 수혜주"
        
        if any(x in topic.lower() for x in ["ai", "반도체", "칩"]):
            theme = "개별 AI 모델, 중소형 테마 부품주"
            structural = "HBM, 데이터센터 인프라, 전력 설비(변압기)"
        elif any(x in topic.lower() for x in ["코로나", "바이오", "감염"]):
            theme = "진단키트, 일회성 테마 바이오"
            structural = "백신 CDMO, 글로벌 제약사, 장기 치료제 인프라"
            
        return {
            "theme": theme,
            "structural": structural
        }
