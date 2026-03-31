from urllib.parse import urlparse
from typing import List, Dict, Any
import logging

class StatementPrimaryAnchorResolver:
    """
    [IS-94A] Statement Primary Anchor Resolver
    Strengthens the link to the original source and determines trust levels.
    """
    def __init__(self):
        self.logger = logging.getLogger("StatementPrimaryAnchorResolver")

    def resolve(self, item: Dict[str, Any], domain_allowlist: List[str]) -> Dict[str, Any]:
        """
        Calculates anchoring metadata for a single item.
        """
        url = item.get("source_url", "")
        domain = self._extract_domain(url)
        
        anchor_confidence = 0.0
        trust_level = item.get("trust_level", "MEDIUM")

        if domain:
            # Rule 1: Allowlist Matching
            if any(allowed in domain for allowed in domain_allowlist):
                anchor_confidence = 1.0
                trust_level = "HARD_FACT"
            # Rule 2: Known reliable aggregators/news
            elif any(news in domain for news in ["reuters.com", "bloomberg.com", "wsj.com", "ft.com", "cnbc.com"]):
                anchor_confidence = 0.8
                trust_level = "HARD_FACT" # Tier 1 news often serves as primary for public statements
            elif any(news in domain for news in ["yonhapnews.co.kr", "kedglobal.com"]):
                anchor_confidence = 0.7
                trust_level = "MEDIUM"
            else:
                anchor_confidence = 0.5
        
        # If no link at all, it's a hint
        if not url:
            anchor_confidence = 0.0
            trust_level = "TEXT_HINT"

        item["primary_url"] = url if anchor_confidence > 0 else None
        item["primary_domain"] = domain
        item["anchor_confidence"] = anchor_confidence
        item["trust_level"] = trust_level
        
        return item

    def _extract_domain(self, url: str) -> str:
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except:
            return ""
