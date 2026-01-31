import logging
import json
import requests
import time
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup
from typing import List, Dict, Any

logger = logging.getLogger("CorporateActionConnector")
logging.basicConfig(level=logging.INFO)

# SEC RSS Feed for 8-K (Current events)
# Note: SEC requires strict User-Agent.
SEC_8K_URL = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&CIK=&type=8-K&output=atom"
USER_AGENT = "HoinInsightBot/1.0 (hoin.insight.bot@gmail.com)"

# Filter for Strong Action Signals
TARGET_ITEMS = [
    {"keyword": "Item 1.01", "type": "AGREEMENT", "desc": "주요 계약 체결 (Material Agreement)"},
    {"keyword": "Item 1.02", "type": "TERMINATION", "desc": "주요 계약 종료"},
    {"keyword": "Item 2.01", "type": "ACQUISITION", "desc": "자산 취득/매각 완료"},
    {"keyword": "Item 2.03", "type": "FINANCIAL_OBLIGATION", "desc": "직접 금융 의무 발생 (차입/채권)"},
    # "Item 7.01" (Reg FD) often contains slides but not "Hard Action" per se.
    # "Item 8.01" (Other) is too generic.
]

def collect_corporate_facts(base_dir: Path, ymd: str) -> List[Dict[str, Any]]:
    """
    Collects Corporate Action Hard Facts via SEC 8-K RSS.
    Returns list of facts with 'evidence_grade': 'HARD_FACT' based on Filings.
    """
    facts = []
    
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/atom+xml,application/xml"
    }
    
    try:
        # SEC RSS Fetch
        resp = requests.get(SEC_8K_URL, headers=headers, timeout=15)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.content, "xml")
            entries = soup.find_all("entry")
            
            for entry in entries:
                title = entry.title.text if entry.title else ""
                link = entry.link["href"] if entry.link else ""
                summary = entry.summary.text if entry.summary else ""
                updated = entry.updated.text if entry.updated else ""
                
                # Title format in SEC RSS: "8-K - Company Name (CIK) (Filer)"
                # Summary usually contains the "Item X.XX" details.
                
                # Check for Target Items in Summary
                action_type = None
                desc_ko = ""
                
                for target in TARGET_ITEMS:
                    if target["keyword"] in summary:
                        action_type = target["type"]
                        desc_ko = target["desc"]
                        break
                
                if action_type:
                    # Clean Company Name from Title
                    # Format: "8-K - APPLE INC (0000320193) (Filer)"
                    company_name = title.replace("8-K - ", "").split("(")[0].strip()
                    
                    fact = {
                        "fact_type": "CORPORATE_ACTION",
                        "fact_text": f"[{company_name}] {desc_ko}",
                        "source": "SEC 8-K (Official)",
                        "source_ref": link,
                        "source_date": updated[:10], # YYYY-MM-DD
                        "evidence_grade": "HARD_FACT",
                        "reliability_score": 95, # Very High (Legal Filing)
                        "independence_key": f"CORP_{company_name}_{action_type}_{ymd}",
                        "details": {
                            "company": company_name,
                            "action_type": action_type,
                            "raw_summary": summary[:200]
                        }
                    }
                    facts.append(fact)
                    
    except Exception as e:
        logger.error(f"Error fetching SEC RSS: {e}")

    # Deduplicate
    unique_facts = {f["independence_key"]: f for f in facts}.values()
    final_facts = list(unique_facts)

    # Save
    if final_facts:
        save_path = base_dir / f"data/facts/fact_anchors_corporate_{ymd.replace('-', '')}.json"
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_text(json.dumps(final_facts, ensure_ascii=False, indent=2), encoding='utf-8')
        logger.info(f"Saved {len(final_facts)} Corporate Facts.")
    else:
        logger.info("No Significant Corporate Actions (8-K Items 1.01/2.01) found specifically.")
        
    return final_facts

if __name__ == "__main__":
    collect_corporate_facts(Path("."), datetime.now().strftime("%Y-%m-%d"))
