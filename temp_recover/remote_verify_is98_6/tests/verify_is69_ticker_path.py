import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.issuesignal.ticker_path_extractor import TickerPathExtractor

def test_ticker_path_logic():
    actor_info = {
        "actor_type": "자본주체",
        "actor_name_ko": "미국 장기채",
        "actor_tag": "병목"
    }
    
    corporate_facts = [
        {
            "fact_text": "[애플] 독점 공급 계약 체결",
            "evidence_grade": "HARD_FACT",
            "details": {
                "company": "애플",
                "ticker": "AAPL",
                "action_type": "AGREEMENT",
                "raw_summary": "Exclusive supply agreement for next-gen sensors."
            }
        },
        {
            "fact_text": "[테슬라] 단순 뉴스",
            "evidence_grade": "TEXT_HINT",
            "details": {
                "company": "테슬라",
                "ticker": "TSLA",
                "action_type": "NEWS",
                "raw_summary": "Tesla mentions AI future."
            }
        }
    ]
    
    result = TickerPathExtractor.extract(actor_info, corporate_facts)
    
    print(f"Global Bottleneck: {result['global_bottleneck_ko']}")
    print(f"Total Tickers: {len(result['ticker_results'])}")
    
    for r in result['ticker_results']:
        print(f"--- Ticker: {r['company_name_ko']} ({r['ticker']}) ---")
        print(f"Confidence: {r['confidence']}")
        print(f"Exposure: {r['exposure']}")
        print(f"Link: {r['bottleneck_link_ko']}")
        
    # Assertions
    assert len(result['ticker_results']) == 1
    assert result['ticker_results'][0]['company_name_ko'] == "애플"
    assert result['ticker_results'][0]['confidence'] >= 90 # 60 + 15(aligned) + 15(exclusive)
    assert result['ticker_results'][0]['exposure'] == "공개"

if __name__ == "__main__":
    test_ticker_path_logic()
    print("\n[VERIFY] IS-69 Ticker Path Unit Test Passed!")
