"""
ECOS (한국은행 경제통계시스템) Data Collector
Collects Korean economic data from Bank of Korea Economic Statistics System
"""

import requests
from pathlib import Path
from datetime import datetime
import pandas as pd
import os
import json
import time

class ECOSCollector:
    """한국은행 ECOS 데이터 수집기"""
    
    # 수집할 통계 시리즈 정의
    SERIES_MAP = {
        # 금리
        '722Y001': {
            'category': 'rates',
            'name': 'korea_base_rate',
            'desc': '한국 기준금리',
            'stat_code': '722Y001',
            'item_code1': '0101000'
        },
        
        # 물가
        '901Y009': {
            'category': 'inflation', 
            'name': 'korea_cpi',
            'desc': '소비자물가지수',
            'stat_code': '901Y009',
            'item_code1': '0'
        },
        '404Y014': {
            'category': 'inflation',
            'name': 'korea_ppi', 
            'desc': '생산자물가지수',
            'stat_code': '404Y014',
            'item_code1': '*'
        },
        
        # 고용
        '901Y044': {
            'category': 'employment',
            'name': 'korea_unemployment',
            'desc': '실업률',
            'stat_code': '901Y044',
            'item_code1': 'A'
        },
        
        # GDP
        '200Y001': {
            'category': 'macro',
            'name': 'korea_gdp',
            'desc': '국내총생산(GDP)',
            'stat_code': '200Y001',
            'item_code1': '10101'
        },
        
        # 통화량
        '101Y002': {
            'category': 'money_supply',
            'name': 'korea_m1',
            'desc': 'M1 통화량',
            'stat_code': '101Y002',
            'item_code1': 'BBHA00'
        },
        '101Y003': {
            'category': 'money_supply',
            'name': 'korea_m2',
            'desc': 'M2 통화량',
            'stat_code': '101Y003',
            'item_code1': 'BBHA00'
        },
        
        # 환율
        '731Y001': {
            'category': 'fx',
            'name': 'korea_usdkrw',
            'desc': '원/달러 환율',
            'stat_code': '731Y001',
            'item_code1': '0000001'
        },
        
        # 무역
        '403Y003': {
            'category': 'trade',
            'name': 'korea_exports',
            'desc': '수출액',
            'stat_code': '403Y003',
            'item_code1': 'A'
        },
        '403Y004': {
            'category': 'trade',
            'name': 'korea_imports',
            'desc': '수입액',
            'stat_code': '403Y004',
            'item_code1': 'A'
        },
    }
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get('ECOS_API_KEY')
        if not self.api_key:
            raise ValueError("ECOS API key not found. Set ECOS_API_KEY environment variable.")
        
        self.base_url = "https://ecos.bok.or.kr/api/StatisticSearch"
        self.base_dir = Path(__file__).parent.parent.parent
        self.stats = {
            'success': 0,
            'failed': 0,
            'total': len(self.SERIES_MAP)
        }
    
    def collect_series(self, series_key, start_date=None, end_date=None):
        """단일 시리즈 수집"""
        if start_date is None:
            # 최근 5년 데이터 (월별 데이터는 YYYYMM 형식)
            start_date = (datetime.now().replace(year=datetime.now().year - 5)).strftime('%Y%m')
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m')
        
        series_info = self.SERIES_MAP.get(series_key)
        if not series_info:
            print(f"[ECOS] ✗ Unknown series: {series_key}")
            return False
        
        try:
            # API 요청 URL 구성
            url = f"{self.base_url}/{self.api_key}/json/kr/1/100000/{series_info['stat_code']}/M/{start_date}/{end_date}/{series_info['item_code1']}"
            
            # 요청
            response = requests.get(url, timeout=30)
            
            if response.status_code != 200:
                print(f"[ECOS] ✗ {series_key}: HTTP {response.status_code}")
                self.stats['failed'] += 1
                return False
            
            data = response.json()
            
            # 데이터 확인
            if 'StatisticSearch' not in data:
                print(f"[ECOS] ✗ {series_key}: No data in response")
                self.stats['failed'] += 1
                return False
            
            rows = data['StatisticSearch'].get('row', [])
            if not rows:
                print(f"[ECOS] ⚠️  {series_key}: No data rows")
                self.stats['failed'] += 1
                return False
            
            # DataFrame 변환
            df = pd.DataFrame(rows)
            
            # 필요한 컬럼만 추출
            if 'TIME' in df.columns and 'DATA_VALUE' in df.columns:
                df_clean = pd.DataFrame({
                    'date': pd.to_datetime(df['TIME'], format='%Y%m'),
                    'value': pd.to_numeric(df['DATA_VALUE'], errors='coerce')
                })
            else:
                print(f"[ECOS] ✗ {series_key}: Missing required columns")
                self.stats['failed'] += 1
                return False
            
            # Raw 데이터 저장
            category = series_info['category']
            name = series_info['name']
            
            raw_dir = self.base_dir / "data" / "raw" / "ecos" / category
            raw_dir.mkdir(parents=True, exist_ok=True)
            
            date_dir = raw_dir / datetime.now().strftime("%Y/%m/%d")
            date_dir.mkdir(parents=True, exist_ok=True)
            
            raw_file = date_dir / f"{name}.csv"
            df_clean.to_csv(raw_file, index=False)
            
            # Curated 데이터 저장
            curated_dir = self.base_dir / "data" / "curated" / "ecos" / category
            curated_dir.mkdir(parents=True, exist_ok=True)
            
            curated_file = curated_dir / f"{name}.csv"
            df_clean.to_csv(curated_file, index=False)
            
            latest_value = df_clean['value'].iloc[-1]
            print(f"[ECOS] ✓ {series_key:10s} ({series_info['desc']:20s}): {len(df_clean):5d} records, latest: {latest_value:.2f}")
            
            self.stats['success'] += 1
            return True
            
        except Exception as e:
            print(f"[ECOS] ✗ {series_key}: {str(e)[:50]}")
            self.stats['failed'] += 1
            return False
    
    def collect_all(self):
        """모든 시리즈 수집"""
        print(f"\n{'='*80}")
        print(f"[ECOS] Starting collection of {len(self.SERIES_MAP)} series...")
        print(f"{'='*80}\n")
        
        for series_key in self.SERIES_MAP.keys():
            self.collect_series(series_key)
            time.sleep(0.1)  # API 요청 간격
        
        print(f"\n{'='*80}")
        print(f"[ECOS] Collection Complete!")
        print(f"  ✓ Success: {self.stats['success']}/{self.stats['total']}")
        print(f"  ✗ Failed:  {self.stats['failed']}/{self.stats['total']}")
        print(f"{'='*80}\n")
        
        self.save_report()
    
    def save_report(self):
        """수집 리포트 저장"""
        report_dir = self.base_dir / "data" / "reports" / datetime.now().strftime("%Y/%m/%d")
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report = {
            "collected_at": datetime.now().isoformat(),
            "source": "ECOS (Bank of Korea)",
            "stats": self.stats,
            "series_count": len(self.SERIES_MAP),
            "api_key_status": "valid" if self.api_key else "missing"
        }
        
        report_file = report_dir / "ecos_collection_report.json"
        report_file.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"[ECOS] Report saved: {report_file}")

def main():
    """메인 실행 함수"""
    try:
        collector = ECOSCollector()
        collector.collect_all()
    except ValueError as e:
        print(f"[ECOS] Error: {e}")
        print("[ECOS] Please set ECOS_API_KEY environment variable")
        print("[ECOS] Get your free API key: https://ecos.bok.or.kr/api/")
        return 1
    except Exception as e:
        print(f"[ECOS] Unexpected error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
