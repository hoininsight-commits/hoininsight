import requests
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import logging

class PolicyDocumentCollector:
    """
    [IS-93R] Real Policy Document Collector
    Collects official documents from FTC, DOJ, and government newsrooms.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.logger = logging.getLogger("PolicyDocumentCollector")
        # For SEC, specific headers are required
        self.sec_headers = {
            "User-Agent": "HOIN Insight bot@hoin.engine",
            "Accept-Encoding": "gzip, deflate",
            "Host": "www.sec.gov"
        }
        self.default_headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9"
        }

    def collect_from_roster(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        all_results = []
        for info in sources:
            if info.get("kind") not in ["RSS", "WEB"]:
                continue
            key = info.get("id")
            try:
                self.logger.info(f"Collecting documents for {key} from {info['url']}")
                headers = self.sec_headers if "sec.gov" in info['url'] else self.default_headers
                
                response = requests.get(info['url'], headers=headers, timeout=15)
                if response.status_code != 200:
                    self.logger.warning(f"Failed to fetch {key}: HTTP {response.status_code}")
                    continue

                # Check for captcha in content
                if "shield.justice.gov" in response.text or "I am not a robot" in response.text:
                    self.logger.warning(f"Skipping {key}: Captcha detected.")
                    continue

                soup = BeautifulSoup(response.content, "xml")
                # Try both RSS and Atom tags
                items = soup.find_all(["item", "entry"])
                if not items:
                     soup_html = BeautifulSoup(response.content, "html.parser")
                     items = soup_html.find_all(["item", "entry"])

                self.logger.info(f"Found {len(items)} items for {key}")
                
                for item in items[:5]:
                    title = item.find("title").text if item.find("title") else "No Title"
                    
                    description = ""
                    for tag in ["description", "summary", "content"]:
                        found = item.find(tag)
                        if found:
                            description = found.text
                            break
                        
                    link = ""
                    link_tag = item.find("link")
                    if link_tag:
                        link = link_tag.get("href") if link_tag.get("href") else link_tag.text

                    pub_date = ""
                    for tag in ["pubDate", "updated", "published"]:
                        found = item.find(tag)
                        if found:
                            pub_date = found.text
                            break
                    
                    all_results.append({
                        "source_type": "DOCUMENT",
                        "person_or_org": info["organization"],
                        "organization": info["organization"],
                        "published_at": pub_date,
                        "source_url": link,
                        "content": f"{title}\n{description}",
                        "trust_level": info["trust_level"]
                    })
            except Exception as e:
                self.logger.error(f"Error collecting from {key}: {e}")
        
        return all_results
