"""
Labor Market US Collector (IS-95-x)
Collects labor market data focusing on AI-driven shifts:
- Unemployment by education level
- Youth unemployment (22-25 target, proxy 20-24)
- Wage premiums for trades/struction
"""

from fredapi import Fred
from pathlib import Path
from datetime import datetime
import pandas as pd
import os
import json
from dotenv import load_dotenv

load_dotenv()

class LaborMarketUSCollector:
    """Labor Market US Data Collector (AI Shift Focused)"""
    
    # FRED Series Mapping
    SERIES_MAP = {
        # Education Gap
        'LNS14027660': {'category': 'education', 'name': 'unemp_bachelors', 'desc': 'Unemployment Rate - Bachelors or Higher'},
        'LNS14027659': {'category': 'education', 'name': 'unemp_associate', 'desc': 'Unemployment Rate - Associates Degree'},
        'LNS14027662': {'category': 'education', 'name': 'unemp_highschool', 'desc': 'Unemployment Rate - High School Grads'},
        
        # Youth Cohort (Proxy 20-24 as 22-25 not standard monthly)
        'LNS14000036': {'category': 'youth', 'name': 'unemp_20_24', 'desc': 'Unemployment Rate - 20-24 yrs'},
        'LNS12000036': {'category': 'youth', 'name': 'emp_pop_20_24', 'desc': 'Employment-Population Ratio - 20-24 yrs'},
        
        # Wage Premium (Blue vs White Collar proxies)
        'CES2000000003': {'category': 'wages', 'name': 'wage_construction', 'desc': 'Avg Hrly Earnings - Construction'},
        'CES0500000003': {'category': 'wages', 'name': 'wage_total_private', 'desc': 'Avg Hrly Earnings - Total Private'},
        'CES6054150003': {'category': 'wages', 'name': 'wage_computer_systems', 'desc': 'Avg Hrly Earnings - Computer Systems Design'},
    }
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get('FRED_API_KEY')
        if not self.api_key:
            # Soft fail if no key, but warn
            print("[LABOR_US] Warning: FRED_API_KEY not found. Collection will fail.")
        
        self.fred = Fred(api_key=self.api_key) if self.api_key else None
        self.base_dir = Path(__file__).parent.parent.parent
        self.stats = {'success': 0, 'failed': 0, 'total': len(self.SERIES_MAP)}

    def collect_series(self, series_id):
        if not self.fred: return False
        
        try:
            data = self.fred.get_series(series_id)
            if data is None or len(data) == 0:
                print(f"[LABOR_US] ⚠️  {series_id}: No data")
                return False
                
            info = self.SERIES_MAP.get(series_id, {})
            category = info.get('category', 'other')
            name = info.get('name', series_id.lower())
            
            # Save Raw
            raw_dir = self.base_dir / "data" / "collect" / "labor_market_us" / "raw" / category
            raw_dir.mkdir(parents=True, exist_ok=True)
            
            # Save by date partition
            date_dir = raw_dir / datetime.now().strftime("%Y/%m/%d")
            date_dir.mkdir(parents=True, exist_ok=True)
            
            df = pd.DataFrame({'date': data.index, 'value': data.values})
            df.to_csv(date_dir / f"{name}.csv", index=False)
            
            # Save Curated (Latest)
            curated_dir = self.base_dir / "data" / "collect" / "labor_market_us" / "curated"
            curated_dir.mkdir(parents=True, exist_ok=True)
            df.to_json(curated_dir / f"{name}.json", orient='records', date_format='iso')
            
            print(f"[LABOR_US] ✓ {name}: {len(data)} records")
            self.stats['success'] += 1
            return True
        except Exception as e:
            print(f"[LABOR_US] ✗ {series_id}: {str(e)[:50]}")
            self.stats['failed'] += 1
            return False

    def collect_all(self):
        print(f"\n[LABOR_US] Starting collection...")
        for sid in self.SERIES_MAP:
            self.collect_series(sid)
        
        # Summary Report
        report_dir = self.base_dir / "data" / "collect" / "labor_market_us" / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        report = {
            "timestamp": datetime.now().isoformat(),
            "stats": self.stats
        }
        with open(report_dir / "last_run.json", "w") as f:
            json.dump(report, f, indent=2)

if __name__ == "__main__":
    c = LaborMarketUSCollector()
    c.collect_all()
