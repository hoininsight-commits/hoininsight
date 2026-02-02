import requests
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import logging

class OfficialStatementCollector:
    """
    [IS-93R] Real Statement Collector
    Collects official statements from CEO blogs and Corporate newsrooms via RSS/HTML.
    """
    FEEDS = {
        "Musk": {
            "entity": "Elon Musk",
            "organization": "Tesla",
            # If Tesla IR is blocked, we use a high-trust technical news stream for Musk's specific actions/statements
            "url": "https://www.theverge.com/rss/elon-musk/index.xml", 
            "trust_level": "MEDIUM" # Aggregator is medium, official is hard_fact
        },
        "Huang": {
            "entity": "Jensen Huang",
            "organization": "NVIDIA",
            "url": "https://nvidianews.nvidia.com/releases.xml",
            "trust_level": "HARD_FACT"
        },
        "Altman": {
            "entity": "Sam Altman",
            "organization": "OpenAI",
            "url": "https://openai.com/blog/rss.xml",
            "trust_level": "HARD_FACT"
        }
    }

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.logger = logging.getLogger("OfficialStatementCollector")
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Referer": "https://www.google.com/"
        }

    def collect(self) -> List[Dict[str, Any]]:
        all_results = []
        for key, info in self.FEEDS.items():
            try:
                self.logger.info(f"Collecting statements for {key} from {info['url']}")
                response = requests.get(info['url'], headers=self.headers, timeout=15)
                if response.status_code != 200:
                    # Try one fallback for Tesla Musk if Verge is also blocked or failing
                    if key == "Musk":
                         info["url"] = "https://www.tesla.com/blog/feed"
                         response = requests.get(info['url'], headers=self.headers, timeout=15)
                
                if response.status_code != 200:
                    self.logger.warning(f"Failed to fetch {key}: HTTP {response.status_code}")
                    continue

                soup = BeautifulSoup(response.content, "xml")
                items = soup.find_all(["item", "entry"])
                if not items:
                    soup_html = BeautifulSoup(response.content, "html.parser")
                    items = soup_html.find_all(["item", "entry"]) or soup_html.find_all("item")
                
                self.logger.info(f"Found {len(items)} items for {key}")

                # Limit to 3 most recent
                for item in items[:3]:
                    title = item.find("title").text if item.find("title") else "No Title"
                    
                    description = ""
                    for tag in ["description", "summary", "content", "content:encoded"]:
                        found = item.find(tag)
                        if found:
                            description = found.text
                            break
                        
                    link = ""
                    link_tag = item.find("link")
                    if link_tag:
                        link = link_tag.get("href") if link_tag.get("href") else link_tag.text
                    
                    pub_date = ""
                    for tag in ["pubDate", "updated", "published", "dc:date"]:
                        found = item.find(tag)
                        if found:
                            pub_date = found.text
                            break
                    
                    all_results.append({
                        "source_type": "STATEMENT",
                        "person_or_org": info["entity"],
                        "organization": info["organization"],
                        "published_at": pub_date,
                        "source_url": link,
                        "content": f"{title}\n{description}",
                        "trust_level": info["trust_level"]
                    })
            except Exception as e:
                self.logger.error(f"Error collecting from {key}: {e}")
        
        return all_results
