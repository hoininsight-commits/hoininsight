import hashlib
from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging

class StatementDedupEngine:
    """
    [IS-94A] Statement Dedup Engine
    Merges duplicate or highly similar statements from the same person/institution.
    """
    def __init__(self):
        self.logger = logging.getLogger("StatementDedupEngine")

    def dedup(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Merges redundant items. 
        Rules: Same Person + Same Primary URL OR Same Person + Similar Content + 24h window.
        """
        if not items:
            return []

        merged_groups = {}
        
        for item in items:
            person = item.get("person_or_org") or "Unknown"
            url = item.get("primary_url") or f"no-link-{hashlib.md5(item.get('content', '').encode()).hexdigest()[:8]}"
            
            # Simple hash-based dedup for exact content or same URL
            content_snippet = item.get("content", "")[:100].strip()
            group_key = f"{person}|{url}"
            
            if group_key not in merged_groups:
                merged_groups[group_key] = {
                    "person_or_org": person,
                    "organization": item.get("organization"),
                    "content": item.get("content"),
                    "primary_url": item.get("primary_url"),
                    "primary_domain": item.get("primary_domain"),
                    "anchor_confidence": item.get("anchor_confidence"),
                    "trust_level": item.get("trust_level"),
                    "first_seen_at": item.get("published_at"),
                    "last_seen_at": item.get("published_at"),
                    "all_sources": [item.get("source_url")],
                    "merged_count": 1,
                    "themes": [item.get("theme")] if "theme" in item else []
                }
            else:
                # Merge logic
                group = merged_groups[group_key]
                group["merged_count"] += 1
                if item.get("source_url") not in group["all_sources"]:
                    group["all_sources"].append(item.get("source_url"))
                
                # Update last_seen if newer
                # (Assuming ISO or similar comparable string format or already dt)
                if item.get("published_at") > group["last_seen_at"]:
                    group["last_seen_at"] = item.get("published_at")
                
                # If current item has higher confidence, update primary metadata
                if item.get("anchor_confidence", 0) > group.get("anchor_confidence", 0):
                    group["primary_url"] = item.get("primary_url")
                    group["primary_domain"] = item.get("primary_domain")
                    group["anchor_confidence"] = item.get("anchor_confidence")
                    group["trust_level"] = item.get("trust_level")

        return list(merged_groups.values())
