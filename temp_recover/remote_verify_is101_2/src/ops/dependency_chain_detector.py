import re
from typing import List, Dict, Any, Optional

class DependencyChainDetector:
    """
    IS-32: DEPENDENCY_CHAIN_DETECTOR
    Classifies whether SourceEvidence is ORIGINAL or DERIVED based on 
    attribution phrases and publisher metadata.
    """

    DERIVED_PATTERNS = [
        (r"(?i)according to (Reuters|Bloomberg|AP|AFP|Yonhap|Reuters|CNBC|WSJ|FT)", "DERIVED_FROM_MEDIA"),
        (r"(?i)(Reuters|Bloomberg|AP|AFP|연합뉴스|뉴시스|머니투데이|이데일리|로이터)에 따르면", "DERIVED_FROM_MEDIA"),
        (r"(?i)reported by (Reuters|Bloomberg|AP)", "DERIVED_FROM_MEDIA"),
        (r"(?i)(press release|보도자료)", "DERIVED_FROM_OFFICIAL"),
        (r"(?i)(statement said|official statement)", "DERIVED_FROM_OFFICIAL"),
        (r"(?i)transcript of", "DERIVED_FROM_OFFICIAL"),
        (r"(?i)citing (.*?)\.com", "DERIVED_FROM_WEB"),
    ]

    SYNDICATION_HOSTS = {
        "finance.yahoo.com": "YAHOO_FINANCE",
        "msn.com": "MSN",
        "news.google.com": "GOOGLE_NEWS"
    }

    def __init__(self):
        pass

    def detect(self, source: Dict[str, Any]) -> Dict[str, Any]:
        """
        Input: Source dict with 'normalized_url', 'raw_content', etc.
        Output: source dict with 'origin_cluster_id', 'dependency_label', 'derived_from'.
        """
        content = (source.get("raw_content") or source.get("title") or "").strip()
        url = source.get("normalized_url") or ""
        
        # 0. Initialize
        detected_label = "UNKNOWN"
        derived_from = None
        
        # 1. Host-based Detection
        host = self._get_host(url)
        if host in self.SYNDICATION_HOSTS:
            detected_label = "DERIVED"
            derived_from = self.SYNDICATION_HOSTS[host]
            source["origin_confidence"] = 90
        
        # 2. Content-based Attribution Detection
        if detected_label == "UNKNOWN":
            for pattern, label in self.DERIVED_PATTERNS:
                match = re.search(pattern, content)
                if match:
                    detected_label = "DERIVED"
                    # If it's a media attribution, extract the name, otherwise use the label
                    if label == "DERIVED_FROM_MEDIA":
                        derived_from = match.group(1) if len(match.groups()) > 0 else "UNKNOWN_MEDIA"
                    else:
                        derived_from = label
                    break
        
        # 3. Handle Special Case: Official sources naming themselves "Press Release"
        stype = source.get("source_type", "").upper()
        if detected_label == "DERIVED" and derived_from == "DERIVED_FROM_OFFICIAL":
            if stype.startswith("OFFICIAL") or stype in ["REGULATORY", "FILING"]:
                detected_label = "ORIGINAL"
                derived_from = None

        if detected_label == "DERIVED":
            source["dependency_label"] = "DERIVED"
            source["derived_from"] = source.get("derived_from") or derived_from
            source["origin_confidence"] = source.get("origin_confidence") or 80
        else:
            # Default to ORIGINAL if from official source type
            if stype.startswith("OFFICIAL") or stype in ["REGULATORY", "FILING"]:
                source["dependency_label"] = "ORIGINAL"
                source["origin_confidence"] = 95
            else:
                source["dependency_label"] = "UNKNOWN"
                source["origin_confidence"] = 50

        # Cluster ID Assignment (Will be finalized by DiversityEnforcer)
        # For individual detection, we use the fingerprint as a base
        source["origin_cluster_id"] = source.get("canonical_fingerprint") or "UNKNOWN_CLUSTER"
        
        return source

    def _get_host(self, url: str) -> str:
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except:
            return ""
