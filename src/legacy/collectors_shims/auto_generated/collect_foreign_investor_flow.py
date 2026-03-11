"""
Auto-generated collector for: foreign_investor_flow
Source: KRX 정보데이터시스템
Method: CSV
Generated: 2026-01-18T05:06:06.789398
Status: CANDIDATE
Proposal ID: EVO-20260118-26886
"""

from pathlib import Path
import json
from datetime import datetime

def collect():
    """
    Collect foreign_investor_flow from KRX 정보데이터시스템
    
    Implementation:
    1. Fetch data from KRX using public data portal
    2. Parse CSV data for foreign/institutional investor net buying
    3. Save to data/raw/market_flow/foreign_investor_flow/YYYY/MM/DD/
    
    Reference:
    - Proposal: EVO-20260118-26886
    - Evidence: 두 번째로 확인해야 할 건 외국인 수급 방향이야
    """
    import requests
    import csv
    from io import StringIO
    
    base_dir = Path(__file__).parent.parent.parent.parent
    output_dir = base_dir / "data" / "raw" / "market_flow" / "foreign_investor_flow"
    
    # Get current date
    now = datetime.now()
    date_path = output_dir / now.strftime("%Y/%m/%d")
    date_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # KRX 공개 데이터 포털 URL (투자자별 매매동향)
        # Note: 실제 운영 시 KRX API 키 필요할 수 있음
        url = "http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd"
        
        # Request parameters for foreign investor trading data
        params = {
            "bld": "dbms/MDC/STAT/standard/MDCSTAT02203",
            "locale": "ko_KR",
            "mktId": "ALL",  # ALL, STK (KOSPI), KSQ (KOSDAQ)
            "trdDd": now.strftime("%Y%m%d"),
            "share": "1",
            "money": "1"
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "http://data.krx.co.kr"
        }
        
        print(f"[foreign_investor_flow] Fetching data from KRX...")
        response = requests.get(url, params=params, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # Save raw JSON
            raw_path = date_path / "raw_data.json"
            raw_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
            
            # Parse and save as CSV
            if 'OutBlock_1' in data:
                csv_path = date_path / "investor_flow.csv"
                with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
                    if data['OutBlock_1']:
                        writer = csv.DictWriter(f, fieldnames=data['OutBlock_1'][0].keys())
                        writer.writeheader()
                        writer.writerows(data['OutBlock_1'])
                
                print(f"[foreign_investor_flow] ✓ Data saved: {csv_path}")
                status = "SUCCESS"
            else:
                print(f"[foreign_investor_flow] ⚠ No data available for today")
                status = "NO_DATA"
        else:
            print(f"[foreign_investor_flow] ✗ HTTP {response.status_code}")
            status = "HTTP_ERROR"
            
    except Exception as e:
        print(f"[foreign_investor_flow] ✗ Error: {e}")
        status = "ERROR"
    
    # Save metadata
    metadata = {
        "collected_at": now.isoformat(),
        "source": "KRX 정보데이터시스템",
        "status": status,
        "proposal_id": "EVO-20260118-26886",
        "url": url if 'url' in locals() else None
    }
    
    metadata_path = date_path / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
    
    return metadata

if __name__ == "__main__":
    result = collect()
    print(f"Collection result: {result}")
