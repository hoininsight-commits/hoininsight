import requests
import json
import logging
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path

# Setup Logger
logger = logging.getLogger("RealIngress")
logging.basicConfig(level=logging.INFO)

# 1. RSS Headline Collector
RSS_SOURCES = {
    "Google_News_KR_Economy": "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=ko&gl=KR&ceid=KR:ko",
    "MK_News": "https://www.mk.co.kr/rss/30000001/" 
}

def collect_rss_headlines(base_dir: Path, ymd: str):
    """Collects headlines from real RSS sources."""
    results = []
    
    for name, url in RSS_SOURCES.items():
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.content, "xml")
                items = soup.find_all("item")
                for item in items[:20]: # Top 20 per source
                    title = item.title.text if item.title else "No Title"
                    link = item.link.text if item.link else "No Link"
                    pub_date = item.pubDate.text if item.pubDate else ""
                    
                    results.append({
                        "source_name": name,
                        "title": title,
                        "link": link,
                        "published_at": pub_date,
                        "collected_at": datetime.now().isoformat()
                    })
            else:
                logger.warning(f"Failed to fetch {name}: {resp.status_code}")
        except Exception as e:
            logger.error(f"Error collecting RSS {name}: {e}")
            
    # Save Raw
    save_path = base_dir / f"data/raw/rss/{ymd}.json"
    save_path.parent.mkdir(parents=True, exist_ok=True)
    save_path.write_text(json.dumps({"headlines": results}, ensure_ascii=False, indent=2), encoding='utf-8')
    
    logger.info(f"Collected {len(results)} RSS headlines.")
    return results

# 2. Official Release Collector (Stub for real gov sites or using generic RSS)
def collect_official_releases(base_dir: Path, ymd: str):
    """Collects official releases (Placeholder for specific Gov/BOK targets)."""
    # For MVP IS-55, we can reuse Google News 'Government' section or similar if specific URL unknown
    # Or just return empty list gracefully as per spec
    results = []
    
    save_path = base_dir / f"data/raw/official/{ymd}.json"
    save_path.parent.mkdir(parents=True, exist_ok=True)
    save_path.write_text(json.dumps({"releases": results}, ensure_ascii=False, indent=2), encoding='utf-8')
    
    return results

# 3. Market Proxy Collector (Read-only from HoinEngine)
def collect_market_proxy(base_dir: Path, ymd: str):
    """Reads latest market data from HoinEngine output."""
    market_path = base_dir / "data/market/latest_market.json"
    data = {}
    
    if market_path.exists():
        try:
            data = json.loads(market_path.read_text(encoding='utf-8'))
        except: pass
        
    save_path = base_dir / f"data/raw/market_proxy/{ymd}.json"
    save_path.parent.mkdir(parents=True, exist_ok=True)
    save_path.write_text(json.dumps({"market_data": data}, ensure_ascii=False, indent=2), encoding='utf-8')
    
    return data
