"""
Auto-generated collector for: value_up_participants
Source: 금융위원회 공시
Method: 공개자료
Generated: 2026-01-18T05:06:06.789398
Status: CANDIDATE
Proposal ID: EVO-20260118-95759
"""

from pathlib import Path
import json
from datetime import datetime

def collect():
    """
    Collect value_up_participants from 금융위원회 공시
    
    Implementation:
    1. Fetch 밸류업 프로그램 참여 기업 리스트
    2. Parse company list and participation details
    3. Save to data/raw/policy/value_up_participants/YYYY/MM/DD/
    
    Reference:
    - Proposal: EVO-20260118-95759
    - Evidence: 다섯 번째로 확인해야 할 건 밸류업 참여 기업이야
    """
    import requests
    from bs4 import BeautifulSoup
    
    base_dir = Path(__file__).parent.parent.parent.parent
    output_dir = base_dir / "data" / "raw" / "policy" / "value_up_participants"
    
    # Get current date
    now = datetime.now()
    date_path = output_dir / now.strftime("%Y/%m/%d")
    date_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # 금융위원회 밸류업 프로그램 공식 페이지
        # Note: 실제 URL은 금융위원회 공식 발표 후 업데이트 필요
        url = "https://www.fsc.go.kr"  # 금융위원회 메인
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        print(f"[value_up_participants] Fetching data from 금융위원회...")
        
        # Fallback: KRX 상장사 정보 활용
        # 밸류업 참여 기업은 공시를 통해 확인 가능
        krx_url = "http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd"
        krx_params = {
            "bld": "dbms/comm/finder/finder_stkisu",  # 상장종목 검색
            "locale": "ko_KR",
            "mktsel": "ALL"
        }
        
        response = requests.get(krx_url, params=krx_params, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # Save raw JSON
            raw_path = date_path / "raw_data.json"
            raw_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
            
            # 밸류업 참여 기업 리스트 (수동 업데이트 필요)
            # TODO: 금융위원회 공식 발표 후 자동 수집 로직 추가
            value_up_companies = {
                "last_updated": now.isoformat(),
                "source": "금융위원회 공시",
                "companies": [
                    # 예시 데이터 (실제 발표 후 업데이트 필요)
                    {"name": "삼성전자", "code": "005930", "announced_date": "2024-01-01"},
                    {"name": "SK하이닉스", "code": "000660", "announced_date": "2024-01-01"},
                    # ... 추가 기업
                ],
                "note": "금융위원회 공식 발표 대기 중 - 수동 업데이트 필요"
            }
            
            companies_path = date_path / "value_up_participants.json"
            companies_path.write_text(json.dumps(value_up_companies, ensure_ascii=False, indent=2), encoding='utf-8')
            
            print(f"[value_up_participants] ✓ Data saved: {companies_path}")
            print(f"[value_up_participants] ⚠ Manual update required for official list")
            status = "PARTIAL_SUCCESS"
        else:
            print(f"[value_up_participants] ✗ HTTP {response.status_code}")
            status = "HTTP_ERROR"
            
    except Exception as e:
        print(f"[value_up_participants] ✗ Error: {e}")
        status = "ERROR"
    
    # Save metadata
    metadata = {
        "collected_at": now.isoformat(),
        "source": "금융위원회 공시",
        "status": status,
        "proposal_id": "EVO-20260118-95759",
        "note": "금융위원회 공식 발표 후 자동 수집 로직 업데이트 필요"
    }
    
    metadata_path = date_path / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
    
    return metadata

if __name__ == "__main__":
    result = collect()
    print(f"Collection result: {result}")
