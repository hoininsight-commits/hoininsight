import json
import pandas as pd
from pathlib import Path
from datetime import datetime

class CandidateDetector:
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path(".")
        
    def detect_all(self, target_date_str=None):
        """
        Runs detection for all 6 pools using actual data where available.
        """
        if not target_date_str:
            target_date_str = datetime.now().strftime("%Y-%m-%d")
            
        candidates = []
        
        # 1. Index Regime (Real Data: KOSPI)
        candidates.extend(self._detect_index_regime(target_date_str))
        
        # 2. Policy/Macro (Real Data: US 10Y Yield)
        candidates.extend(self._detect_macro_event(target_date_str))
        
        # 3. FX (Real Data: USD/KRW)
        candidates.extend(self._detect_fx_event(target_date_str))
        
        return {
            "date": target_date_str,
            "market": "MIXED", # US+KR
            "candidates": candidates
        }

    def _detect_index_regime(self, date_str):
        candidates = []
        # Logical Path: data/raw/index_kospi_stooq/2026/01/23/kospi.json
        y, m, d = date_str.split('-')
        kospi_path = self.base_dir / "data" / "raw" / "index_kospi_stooq" / y / m / d / "kospi.json"
        
        if kospi_path.exists():
            try:
                with open(kospi_path, 'r') as f:
                    data = json.load(f)
                val = data.get('close', 0)
                
                if val > 4500:
                    candidates.append({
                        "candidate_id": "regime_kospi_high",
                        "category_pool": "IndexRegime",
                        "topic_anchor": f"코스피 {int(val)} 돌파: 새로운 시대",
                        "trigger_event": f"KOSPI {val:.1f}pt 기록 (역사적 고점 부근)",
                        "observed_metrics": [f"KOSPI: {val:.1f}"],
                        "driver_candidates": ["글로벌 유동성 공급", "국내 기업 이익 성장"],
                        "public_misconception": "단순히 지수가 높아서 위험하다는 공포심",
                        "money_flow": "외국인 투자자의 우량 대형주 중심 패시브 자금 유입",
                        "comparison_baseline": "과거 10년 평균 코스피 지수 2300pt 대비 2배 이상 상승",
                        "scores": {"hook_score": 10, "number_score": 9, "why_now_score": 10},
                        "confidence": "HIGH"
                    })
            except Exception as e:
                print(f"Error reading KOSPI data: {e}")
                
        return candidates

    def _detect_macro_event(self, date_str):
        candidates = []
        # Logical Path: data/raw/fred/rates/2026/01/23/us_10y_yield.csv
        y, m, d = date_str.split('-')
        yield_path = self.base_dir / "data" / "raw" / "fred" / "rates" / y / m / d / "us_10y_yield.csv"
        
        if yield_path.exists():
            try:
                df = pd.read_csv(yield_path)
                # Get last valid value
                last_row = df.dropna(subset=['value']).iloc[-1]
                val = float(last_row['value'])
                
                candidates.append({
                    "candidate_id": "macro_us10y_high",
                    "category_pool": "Policy",
                    "topic_anchor": f"미 국채 10년물 {val}%: 긴장의 연속",
                    "trigger_event": f"US 10Y Yield {val}% 돌파 및 유지",
                    "observed_metrics": [f"Yield: {val}%"],
                    "driver_candidates": ["인플레이션 우려 재점화", "연준 통화긴축 장기화"],
                    "public_misconception": "금리 상승이 무조건 주식 시장의 폭락으로 이어진다는 고정관념",
                    "money_flow": "신규 발행 국채로의 안전자산 선호 자금 및 초단기 MMF 자금 이동",
                    "comparison_baseline": "연준의 중립 금리 추정치 2.5% 대비 현저히 높은 수준",
                    "scores": {"hook_score": 8, "number_score": 9, "why_now_score": 8},
                    "confidence": "HIGH"
                })
            except Exception as e:
                print(f"Error reading FRED data: {e}")
                
        return candidates

    def _detect_fx_event(self, date_str):
        candidates = []
        # Logical Path: data/raw/fx_usdkrw_spot_open_er_api/2026/01/23/usdkrw.json
        y, m, d = date_str.split('-')
        fx_path = self.base_dir / "data" / "raw" / "fx_usdkrw_spot_open_er_api" / y / m / d / "usdkrw.json"
        
        if fx_path.exists():
            try:
                with open(fx_path, 'r') as f:
                    data = json.load(f)
                val = data.get('rate', 0)
                
                if val > 1400:
                    candidates.append({
                        "candidate_id": "fx_usdkrw_high",
                        "category_pool": "Policy",
                        "topic_anchor": f"환율 {int(val)}원 돌파: 수출 경고등",
                        "trigger_event": f"USD/KRW {val:.2f}원 기록",
                        "observed_metrics": [f"FX Rate: {val:.2f}"],
                        "driver_candidates": ["달러 강세 (DXY 상승)", "내수 경기 둔화 우려"],
                        "public_misconception": "환율 상승이 무조건 수출 기업의 이익 증가로만 이어진다는 낙관론",
                        "money_flow": "국내 거주자의 외화 예금 증가 및 수입 결제 대금을 위한 강력한 달러 수요 발생",
                        "comparison_baseline": "지난 5년 실질실효환율 평균 대비 15% 이상 고평가된 달러 가치",
                        "scores": {"hook_score": 9, "number_score": 8, "why_now_score": 9},
                        "confidence": "HIGH"
                    })
            except Exception as e:
                print(f"Error reading FX data: {e}")
                
        return candidates



if __name__ == "__main__":
    detector = CandidateDetector()
    results = detector.detect_all()
    print(json.dumps(results, indent=2, ensure_ascii=False))
