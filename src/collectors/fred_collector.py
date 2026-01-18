"""
FRED Data Collector
Collects economic data from Federal Reserve Economic Data (FRED)
"""

from fredapi import Fred
from pathlib import Path
from datetime import datetime
import pandas as pd
import os
import json

class FREDCollector:
    """FRED 데이터 통합 수집기"""
    
    # 수집할 시리즈 정의
    SERIES_MAP = {
        # 금리 (Interest Rates)
        'FEDFUNDS': {'category': 'rates', 'name': 'fed_funds_rate', 'desc': 'Fed Funds Rate'},
        'DGS2': {'category': 'rates', 'name': 'us_2y_yield', 'desc': '2Y Treasury Yield'},
        'DGS5': {'category': 'rates', 'name': 'us_5y_yield', 'desc': '5Y Treasury Yield'},
        'DGS10': {'category': 'rates', 'name': 'us_10y_yield', 'desc': '10Y Treasury Yield'},
        'DGS30': {'category': 'rates', 'name': 'us_30y_yield', 'desc': '30Y Treasury Yield'},
        
        # 물가 (Inflation)
        'CPIAUCSL': {'category': 'inflation', 'name': 'cpi', 'desc': 'Consumer Price Index'},
        'CPILFESL': {'category': 'inflation', 'name': 'core_cpi', 'desc': 'Core CPI (ex Food & Energy)'},
        'PCE': {'category': 'inflation', 'name': 'pce', 'desc': 'Personal Consumption Expenditures'},
        'PCEPILFE': {'category': 'inflation', 'name': 'core_pce', 'desc': 'Core PCE'},
        'PPIACO': {'category': 'inflation', 'name': 'ppi', 'desc': 'Producer Price Index'},
        
        # 고용 (Employment)
        'UNRATE': {'category': 'employment', 'name': 'unemployment_rate', 'desc': 'Unemployment Rate'},
        'PAYEMS': {'category': 'employment', 'name': 'nonfarm_payrolls', 'desc': 'Nonfarm Payrolls'},
        'CIVPART': {'category': 'employment', 'name': 'labor_participation', 'desc': 'Labor Force Participation'},
        
        # 통화량 (Money Supply)
        'M1SL': {'category': 'money_supply', 'name': 'm1', 'desc': 'M1 Money Stock'},
        'M2SL': {'category': 'money_supply', 'name': 'm2', 'desc': 'M2 Money Stock'},
        
        # 신용/스프레드 (Credit & Spreads)
        'BAMLH0A0HYM2': {'category': 'credit', 'name': 'hy_spread', 'desc': 'High Yield Spread'},
        'BAMLC0A4CBBB': {'category': 'credit', 'name': 'ig_spread', 'desc': 'Investment Grade Spread'},
        'STLFSI2': {'category': 'credit', 'name': 'financial_stress', 'desc': 'Financial Stress Index'},
        
        # 기타 거시지표
        'GDP': {'category': 'macro', 'name': 'gdp', 'desc': 'Real GDP'},
        'UMCSENT': {'category': 'macro', 'name': 'consumer_sentiment', 'desc': 'Consumer Sentiment'},
    }
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get('FRED_API_KEY')
        if not self.api_key:
            raise ValueError("FRED API key not found. Set FRED_API_KEY environment variable.")
        
        self.fred = Fred(api_key=self.api_key)
        self.base_dir = Path(__file__).parent.parent.parent
        self.stats = {
            'success': 0,
            'failed': 0,
            'total': len(self.SERIES_MAP)
        }
    
    def collect_series(self, series_id, save_raw=True, save_curated=True):
        """단일 시리즈 수집"""
        try:
            # 데이터 가져오기
            data = self.fred.get_series(series_id)
            
            if data is None or len(data) == 0:
                print(f"[FRED] ⚠️  {series_id}: No data returned")
                return False
            
            # 메타데이터
            info = self.SERIES_MAP.get(series_id, {})
            category = info.get('category', 'other')
            name = info.get('name', series_id.lower())
            desc = info.get('desc', series_id)
            
            # Raw 데이터 저장
            if save_raw:
                raw_dir = self.base_dir / "data" / "raw" / "fred" / category
                raw_dir.mkdir(parents=True, exist_ok=True)
                
                # 날짜별 디렉토리
                date_dir = raw_dir / datetime.now().strftime("%Y/%m/%d")
                date_dir.mkdir(parents=True, exist_ok=True)
                
                raw_file = date_dir / f"{name}.csv"
                df_raw = pd.DataFrame({
                    'date': data.index,
                    'value': data.values
                })
                df_raw.to_csv(raw_file, index=False)
            
            # Curated 데이터 저장 (최신 버전)
            if save_curated:
                curated_dir = self.base_dir / "data" / "curated" / "fred" / category
                curated_dir.mkdir(parents=True, exist_ok=True)
                
                curated_file = curated_dir / f"{name}.csv"
                df_curated = pd.DataFrame({
                    'date': data.index,
                    'value': data.values
                })
                df_curated.to_csv(curated_file, index=False)
            
            print(f"[FRED] ✓ {series_id:20s} ({desc:30s}): {len(data):5d} records, latest: {data.iloc[-1]:.2f}")
            self.stats['success'] += 1
            return True
            
        except Exception as e:
            print(f"[FRED] ✗ {series_id:20s}: {str(e)[:50]}")
            self.stats['failed'] += 1
            return False
    
    def collect_all(self):
        """모든 시리즈 수집"""
        print(f"\n{'='*80}")
        print(f"[FRED] Starting collection of {len(self.SERIES_MAP)} series...")
        print(f"{'='*80}\n")
        
        for series_id in self.SERIES_MAP.keys():
            self.collect_series(series_id)
        
        print(f"\n{'='*80}")
        print(f"[FRED] Collection Complete!")
        print(f"  ✓ Success: {self.stats['success']}/{self.stats['total']}")
        print(f"  ✗ Failed:  {self.stats['failed']}/{self.stats['total']}")
        print(f"{'='*80}\n")
        
        # 수집 리포트 저장
        self.save_report()
    
    def save_report(self):
        """수집 리포트 저장"""
        report_dir = self.base_dir / "data" / "reports" / datetime.now().strftime("%Y/%m/%d")
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report = {
            "collected_at": datetime.now().isoformat(),
            "source": "FRED",
            "stats": self.stats,
            "series_count": len(self.SERIES_MAP),
            "api_key_status": "valid" if self.api_key else "missing"
        }
        
        report_file = report_dir / "fred_collection_report.json"
        report_file.write_text(json.dumps(report, indent=2), encoding='utf-8')
        print(f"[FRED] Report saved: {report_file}")

def main():
    """메인 실행 함수"""
    try:
        collector = FREDCollector()
        collector.collect_all()
    except ValueError as e:
        print(f"[FRED] Error: {e}")
        print("[FRED] Please set FRED_API_KEY environment variable")
        print("[FRED] Get your free API key: https://fredaccount.stlouisfed.org/apikeys")
        return 1
    except Exception as e:
        print(f"[FRED] Unexpected error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
