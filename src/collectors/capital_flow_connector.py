import logging
import json
from datetime import datetime
from pathlib import Path
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger("CapitalFlowConnector")
logging.basicConfig(level=logging.INFO)

# Keywords mapping to Sectors
FLOW_KEYWORDS = {
    "반도체": "Semiconductors",
    "에너지": "Energy",
    "채권": "Bonds",
    "금값": "Gold/Defense",
    "방산": "Defense",
    "달러": "Currency",
    "ETF": "Market Flow"
}

DIRECTION_KEYWORDS = {
    "INFLOW": ["매수", "유입", "급등", "상승", "몰려", "사자"],
    "OUTFLOW": ["매도", "유출", "급락", "하락", "이탈", "팔자"]
}

def collect_capital_flows(base_dir: Path, ymd: str):
    """
    Collects capitalization flow evidence via RSS Semantic Analysis.
    (Fallback since direct Exchange API (yfinance) is blocked in this env)
    """
    evidence_list = []
    
    # Reuse valid RSS source from RealIngress
    rss_url = "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=ko&gl=KR&ceid=KR:ko"
    
    try:
        resp = requests.get(rss_url, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.content, "xml")
            items = soup.find_all("item")
            
            for item in items: # Check all items
                title = item.title.text if item.title else ""
                link = item.link.text if item.link else ""
                
                # 1. Detect Sector
                target_sector = None
                for k, v in FLOW_KEYWORDS.items():
                    if k in title:
                        target_sector = v
                        break
                
                if not target_sector:
                    continue
                    
                # 2. Detect Direction
                direction = "FLAT"
                for d_key, keywords in DIRECTION_KEYWORDS.items():
                    for kw in keywords:
                        if kw in title:
                            direction = d_key
                            break
                    if direction != "FLAT":
                        break
                        
                if direction != "FLAT":
                    evidence = {
                        "fact_type": "CAPITAL_FLOW",
                        "fact_text": f"[자금흐름포착] {target_sector} {direction}: {title}",
                        "source": "RSS Finance (Real-time)",
                        "source_ref": "Google_News_KR_Biz",
                        "source_date": str(datetime.now().date()),
                        "evidence_grade": "TEXT_HINT", # [IS-57B] Explicitly Low Reliability
                        "reliability_score": 40,       # RSS Text Analysis is not Hard Fact
                        "independence_key": f"FLOW_RSS_{hash(title)}_{ymd}",
                        "flow_metadata": {
                            "ticker": "RSS_SIGNAL",
                            "sector": target_sector,
                            "change_pct": 0.0, # N/A for text signal
                            "volume_ratio": 0.0,
                            "direction": direction
                        }
                    }
                    evidence_list.append(evidence)

    except Exception as e:
        logger.error(f"Error collecting RSS flows: {e}")
        
    # Save Facts
    if evidence_list:
        save_path = base_dir / f"data/facts/fact_anchors_flow_{ymd.replace('-','')}.json"
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_text(json.dumps(evidence_list, ensure_ascii=False, indent=2), encoding='utf-8')
        logger.info(f"Saved {len(evidence_list)} flow evidence items.")
    else:
        logger.info("No explicit capital flow signals found in current news.")
        
    return evidence_list

if __name__ == "__main__":
    collect_capital_flows(Path("."), datetime.now().strftime("%Y-%m-%d"))
