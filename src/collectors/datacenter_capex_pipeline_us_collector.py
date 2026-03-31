"""
Datacenter Capex Pipeline US Collector (IS-95-x)
Collects indicators for Datacenter Construction and Capex.
Uses FRED Construction Spending data as proxy.
"""

from fredapi import Fred
from pathlib import Path
from datetime import datetime
import pandas as pd
import os
import json
from dotenv import load_dotenv

load_dotenv()

class DatacenterCapexPipelineUSCollector:
    
    SERIES_MAP = {
        # Private Construction: Office (often includes data centers in broad cat)
        'TLPIND027': {'name': 'const_spending_office', 'desc': 'Private Construction Spending: Office'},
        # Manufacturers' New Orders: Computers etc.
        'A33SNO': {'name': 'orders_tech_hardware', 'desc': 'New Orders: Computers and Electronic Products'},
        # Producer Price Index: Data Processing, Hosting, Related Services
        'PCU518518': {'name': 'ppi_data_processing', 'desc': 'PPI: Data Processing & Hosting'},
        # Industrial Production: Computers
        'IPG334111S': {'name': 'ip_computers', 'desc': 'Industrial Production: Computers'},
    }
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get('FRED_API_KEY')
        self.fred = Fred(api_key=self.api_key) if self.api_key else None
        self.base_dir = Path(__file__).parent.parent.parent
        self.stats = {'success': 0, 'failed': 0}

    def collect_series(self, series_id):
        if not self.fred: return False
        try:
            data = self.fred.get_series(series_id)
            if data is None: return False
            
            info = self.SERIES_MAP.get(series_id, {})
            name = info.get('name', series_id)
            
            output_dir = self.base_dir / "data" / "collect" / "datacenter_capex_pipeline_us" / "raw"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            df = pd.DataFrame({'date': data.index, 'value': data.values})
            df.to_json(output_dir / f"{name}.json", orient='records', date_format='iso')
            
            print(f"[DC_CAPEX] ✓ {name}")
            self.stats['success'] += 1
            return True
        except Exception as e:
            print(f"[DC_CAPEX] ✗ {series_id}: {e}")
            self.stats['failed'] += 1
            return False

    def collect_all(self):
        print(f"\n[DC_CAPEX] Starting collection...")
        for sid in self.SERIES_MAP:
            self.collect_series(sid)
            
if __name__ == "__main__":
    c = DatacenterCapexPipelineUSCollector()
    c.collect_all()
