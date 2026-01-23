import json
from pathlib import Path
from datetime import datetime

class CandidateDetector:
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path(".")
        
    def detect_all(self, target_date_str=None):
        """
        Runs detection for all 6 pools.
        """
        if not target_date_str:
            target_date_str = datetime.now().strftime("%Y-%m-%d")
            
        candidates = []
        
        # 1. Sector Divergence
        candidates.extend(self._detect_sector_divergence(target_date_str))
        
        # 2. Index Regime
        candidates.extend(self._detect_index_regime(target_date_str))
        
        # 3. Big Contract (Mocked/Limited)
        candidates.extend(self._detect_big_contract(target_date_str))
        
        # 4. Policy (Mocked/Limited)
        candidates.extend(self._detect_policy(target_date_str))
        
        # 5. Earnings (Mocked/Limited)
        candidates.extend(self._detect_earnings(target_date_str))
        
        # 6. Flow/Liquidity (Mocked/Limited)
        candidates.extend(self._detect_flow(target_date_str))
        
        return {
            "date": target_date_str,
            "market": "MIXED", # US+KR
            "candidates": candidates
        }

    def _detect_sector_divergence(self, date_str):
        # MVP: Return a mock candidate for Bio Sector Drawdown if date matches
        # In production, this would calculate returns from `data/market/sectors/*.json`
        candidates = []
        # Mock Logic for Demo
        candidates.append({
            "candidate_id": "sector_bio_divergence",
            "category_pool": "SectorDivergence",
            "topic_anchor": "바이오 섹터 나홀로 하락",
            "trigger_event": "KOSPI 5000 돌파 중 바이오 급락",
            "observed_metrics": ["Bio Return -3%", "KOSPI +2%"],
            "driver_candidates": ["자본 이동 (Capital Shift)", "평가 기준 변화 (Valuation Reset)"],
            "scores": {"hook_score": 8, "number_score": 7, "why_now_score": 9},
            "confidence": "MEDIUM"
        })
        return candidates

    def _detect_index_regime(self, date_str):
        candidates = []
        # MVP: Return a mock "KOSPI 5000" candidate
        candidates.append({
            "candidate_id": "regime_kospi_5000",
            "category_pool": "IndexRegime",
            "topic_anchor": "코스피 5000 돌파 (대통령 포트폴리오)",
            "trigger_event": "KOSPI 5012.4pt 기록",
            "observed_metrics": ["KOSPI 5012.4", "개인 수익률 +103%"],
            "driver_candidates": ["코리아 디스카운트 해소", "유동성 대이동"],
            "scores": {"hook_score": 10, "number_score": 9, "why_now_score": 10},
            "confidence": "HIGH"
        })
        return candidates

    def _detect_big_contract(self, date_str):
        # MVP: Palantir x HD Hyundai
        return [{
            "candidate_id": "contract_palantir_hd",
            "category_pool": "BigContract",
            "topic_anchor": "팔란티어 x HD현대 계약",
            "trigger_event": "다보스 포럼 계약 체결",
            "observed_metrics": ["수억 달러 규모", "생산성 30% 증가 목표"],
            "driver_candidates": ["AI의 물리적 적용 (Physical AI)", "산업 생산성 혁명"],
            "scores": {"hook_score": 9, "number_score": 8, "why_now_score": 8},
            "confidence": "HIGH"
        }]

    def _detect_policy(self, date_str):
        return []

    def _detect_earnings(self, date_str):
        return []

    def _detect_flow(self, date_str):
        return []

if __name__ == "__main__":
    detector = CandidateDetector()
    results = detector.detect_all()
    print(json.dumps(results, indent=2, ensure_ascii=False))
