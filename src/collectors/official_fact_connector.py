import logging
import json
import requests
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup
from typing import List, Dict, Any

logger = logging.getLogger("OfficialFactConnector")
logging.basicConfig(level=logging.INFO)

# Official Entities to Track (Korean)
OFFICIAL_ENTITIES = {
    "한국은행": {"keywords": ["한국은행", "한은", "이창용"], "grade": "HARD_FACT"},
    "기획재정부": {"keywords": ["기획재정부", "기재부", "최상목"], "grade": "HARD_FACT"},
    "금융위원회": {"keywords": ["금융위원회", "금융위"], "grade": "HARD_FACT"},
    "Fed (US)": {"keywords": ["연준", "파월", "FOMC", "Federal Reserve"], "grade": "HARD_FACT"},
    "White House": {"keywords": ["백악관", "바이든", "트럼프"], "grade": "HARD_FACT"} # Depend on Era
}

RSS_URL = "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=ko&gl=KR&ceid=KR:ko"

def collect_official_facts(base_dir: Path, ymd: str) -> List[Dict[str, Any]]:
    """
    Collects Official/Policy facts via RSS Filtering.
    Only items matching Official Entities are promoted to HARD_FACT.
    """
    facts = []
    
    try:
        resp = requests.get(RSS_URL, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.content, "xml")
            items = soup.find_all("item")
            
            for item in items:
                title = item.title.text if item.title else ""
                link = item.link.text if item.link else ""
                pub_date = item.pubDate.text if item.pubDate else ""
                
                # Check for Entity Match
                matched_entity = None
                for entity, metadata in OFFICIAL_ENTITIES.items():
                    for kw in metadata["keywords"]:
                        if kw in title:
                            matched_entity = entity
                            break
                    if matched_entity:
                        break
                        
                if matched_entity:
                    # Promote to HARD FACT
                    fact = {
                        "fact_type": "OFFICIAL_FACT",
                        "fact_text": f"[{matched_entity}] {title}",
                        "source": f"Official Proxy ({matched_entity})", # Not direct Gov Site yet, but Proxy High Trust
                        "source_ref": link[:100],
                        "source_date": pub_date,
                        "evidence_grade": "HARD_FACT",
                        "reliability_score": 85, # Slightly lower than Macro Data (90) but High
                        "independence_key": f"OFFICIAL_{matched_entity}_{hash(title)}_{ymd}",
                        "details": {
                            "entity": matched_entity,
                            "raw_title": title
                        }
                    }
                    facts.append(fact)
                    
    except Exception as e:
        logger.error(f"Error collecting official facts: {e}")
        
    # Save
    if facts:
        save_path = base_dir / f"data/facts/fact_anchors_official_{ymd.replace('-', '')}.json"
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_text(json.dumps(facts, ensure_ascii=False, indent=2), encoding='utf-8')
        logger.info(f"Saved {len(facts)} Official Facts.")
    else:
        logger.info("No Official Policy facts found in current stream.")
        
    return facts

if __name__ == "__main__":
    collect_official_facts(Path("."), datetime.now().strftime("%Y-%m-%d"))
