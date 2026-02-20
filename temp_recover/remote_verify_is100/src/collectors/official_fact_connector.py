import logging
import json
import requests
from pathlib import Path
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from .primary_source_resolver import resolve_primary_source

logger = logging.getLogger("OfficialFactConnector")
logging.basicConfig(level=logging.INFO)

# Direct Official RSS Feeds (Primary Sources)
DIRECT_FEEDS = {
    "BOK": "https://www.bok.or.kr/portal/bbs/B0000232/rss.do?menuNo=200653", # Press Releases
    "Fed": "https://www.federalreserve.gov/feeds/press_all.xml"
}

# Fallback Entities (Google News)
OFFICIAL_ENTITIES_FALLBACK = {
    "한국은행": ["한국은행", "한은", "이창용"],
    "기획재정부": ["기획재정부", "기재부", "최상목"],
    "금융위원회": ["금융위원회", "금융위"],
    "Fed (US)": ["연준", "파월", "FOMC", "Federal Reserve"],
    "White House": ["백악관", "바이든", "트럼프"]
}

RSS_URL = "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=ko&gl=KR&ceid=KR:ko"

def parse_direct_feed(source_name: str, url: str) -> List[Dict[str, Any]]:
    facts = []
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.content, "xml")
            items = soup.find_all("item")
            
            for item in items: # Check latest items
                title = item.title.text if item.title else ""
                link = item.link.text if item.link else ""
                pub_date = item.pubDate.text if item.pubDate else ""
                
                # BOK dates are often clean, Fed requires parsing. 
                # For MVP, string is fine.
                
                # Resolve
                resolution = resolve_primary_source(link, title)
                
                # Direct Feed implies Hard Fact usually, but we verify via domain for safety
                # If domain matches trusted, it's HARD_FACT.
                
                fact = {
                    "fact_type": "OFFICIAL_FACT",
                    "fact_text": f"[{source_name}] {title}",
                    "source": f"Official Direct ({source_name})",
                    "source_ref": link[:150],
                    "source_date": pub_date,
                    "evidence_grade": resolution["evidence_grade"], # Should be HARD_FACT
                    "reliability_score": 90 if resolution["evidence_grade"] == "HARD_FACT" else 70,
                    "independence_key": f"OFFICIAL_{source_name}_{hash(title)}_{datetime.now().strftime('%Y%m%d')}",
                    "details": {
                        "entity": source_name,
                        "raw_title": title,
                        "grade_reason": resolution["grade_reason_ko"]
                    }
                }
                facts.append(fact)
    except Exception as e:
        logger.warning(f"Direct Feed {source_name} failed: {e}")
    return facts

def collect_official_facts(base_dir: Path, ymd: str) -> List[Dict[str, Any]]:
    """
    Collects Official facts via Direct RSS + Google News Fallback.
    Promotes to HARD_FACT only if PrimarySourceResolver agrees.
    """
    facts = []
    
    # 1. Direct Feeds
    for src, url in DIRECT_FEEDS.items():
        direct_facts = parse_direct_feed(src, url)
        facts.extend(direct_facts)
        
    # 2. Google News Fallback (Secondary)
    try:
        resp = requests.get(RSS_URL, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.content, "xml")
            items = soup.find_all("item")
            
            for item in items:
                title = item.title.text if item.title else ""
                link = item.link.text if item.link else ""
                pub_date = item.pubDate.text if item.pubDate else ""
                
                matched_entity = None
                for entity, keywords in OFFICIAL_ENTITIES_FALLBACK.items():
                    for kw in keywords:
                        if kw in title:
                            matched_entity = entity
                            break
                    if matched_entity:
                        break
                        
                if matched_entity:
                    resolution = resolve_primary_source(link, title)
                    # If Google News links to .go.kr, it becomes HARD_FACT.
                    # If links to yna.co.kr, it becomes MEDIUM.
                    
                    fact = {
                        "fact_type": "OFFICIAL_FACT",
                        "fact_text": f"[{matched_entity}] {title}",
                        "source": f"News Filter ({matched_entity})", 
                        "source_ref": link[:150],
                        "source_date": pub_date,
                        "evidence_grade": resolution["evidence_grade"],
                        "reliability_score": 85 if resolution["evidence_grade"] == "HARD_FACT" else 50,
                        "independence_key": f"OFFICIAL_NEWS_{matched_entity}_{hash(title)}_{ymd}",
                        "details": {
                            "entity": matched_entity,
                            "raw_title": title,
                            "grade_reason": resolution["grade_reason_ko"]
                        }
                    }
                    facts.append(fact)
                    
    except Exception as e:
        logger.error(f"Error collecting official facts fallback: {e}")
        
    # Deduplicate by title hash
    unique_facts = {f["independence_key"]: f for f in facts}.values()
    final_facts = list(unique_facts)

    # Save
    if final_facts:
        save_path = base_dir / f"data/facts/fact_anchors_official_{ymd.replace('-', '')}.json"
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_text(json.dumps(final_facts, ensure_ascii=False, indent=2), encoding='utf-8')
        logger.info(f"Saved {len(final_facts)} Official Facts.")
    else:
        logger.info("No Official Policy facts found.")
        
    return final_facts

if __name__ == "__main__":
    collect_official_facts(Path("."), datetime.now().strftime("%Y-%m-%d"))
