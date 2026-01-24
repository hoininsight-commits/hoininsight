"""
Auto-generated collector for: pension_fund_flow
Source: 금융감독원 전자공시
Method: DART API
Generated: 2026-01-18T05:06:06.788352
Status: CANDIDATE
Proposal ID: EVO-20260118-50129
"""

from pathlib import Path
import json
from datetime import datetime

def collect():
    """
    Collect pension_fund_flow from 금융감독원 전자공시
    
    Implementation:
    1. Fetch data from DART (금융감독원 전자공시시스템)
    2. Parse pension fund (국민연금, 사학연금 등) trading data
    3. Save to data/raw/institutional_flow/pension_fund_flow/YYYY/MM/DD/
    
    Reference:
    - Proposal: EVO-20260118-50129
    - Evidence: 연기금의 국내 주식 비중 확대 검토 소식은 시장의 강력한 지지선을 제공
    """
    import requests
    
    base_dir = Path(__file__).parent.parent.parent.parent
    output_dir = base_dir / "data" / "raw" / "institutional_flow" / "pension_fund_flow"
    
    # Get current date
    now = datetime.utcnow()
    date_path = output_dir / now.strftime("%Y/%m/%d")
    date_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # KRX 기관투자자 매매동향 데이터 사용 (연기금 포함)
        krx_url = "http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd"
        krx_params = {
            "bld": "dbms/MDC/STAT/standard/MDCSTAT02303",  # 기관투자자 매매동향
            "locale": "ko_KR",
            "mktId": "ALL",
            "trdDd": now.strftime("%Y%m%d"),
            "inqCondTpCd": "2"  # 투자자별
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "http://data.krx.co.kr"
        }
        
        print(f"[pension_fund_flow] Fetching data from KRX...")
        response = requests.get(krx_url, params=krx_params, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # Save raw JSON
            raw_path = date_path / "raw_data.json"
            raw_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
            
            # Filter pension fund data if available
            if 'OutBlock_1' in data and data['OutBlock_1']:
                # 연기금 관련 데이터 필터링
                pension_data = [
                    row for row in data['OutBlock_1']
                    if '연기금' in row.get('INVST_NM', '') or '국민연금' in row.get('INVST_NM', '')
                ]
                
                filtered_path = date_path / "pension_fund_flow.json"
                filtered_path.write_text(json.dumps(pension_data, ensure_ascii=False, indent=2), encoding='utf-8')
                
                print(f"[pension_fund_flow] ✓ Data saved: {filtered_path}")
                print(f"[pension_fund_flow] Found {len(pension_data)} pension fund records")
                status = "SUCCESS"
            else:
                print(f"[pension_fund_flow] ⚠ No data available")
                status = "NO_DATA"
        else:
            print(f"[pension_fund_flow] ✗ HTTP {response.status_code}")
            status = "HTTP_ERROR"
            
    except Exception as e:
        print(f"[pension_fund_flow] ✗ Error: {e}")
        status = "ERROR"
    
    # Save metadata
    metadata = {
        "collected_at": now.isoformat(),
        "source": "금융감독원 전자공시 / KRX",
        "status": status,
        "proposal_id": "EVO-20260118-50129",
        "note": "KRX 기관투자자 데이터 활용"
    }
    
    metadata_path = date_path / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
    
    return metadata

if __name__ == "__main__":
    result = collect()
    print(f"Collection result: {result}")
