import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

class StatementRosterManager:
    """
    [IS-94A] Statement Roster Manager
    Handles Tier 0/1/2 roster logic for statement collection.
    """
    def __init__(self, roster_path: Path):
        self.roster_path = roster_path
        self.data = self._load_roster()
        
    def _load_roster(self) -> Dict[str, Any]:
        if not self.roster_path.exists():
            return {"version": "1.0", "roster": []}
        try:
            with open(self.roster_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading roster: {e}")
            return {"version": "1.0", "roster": []}

    def get_active_roster(self) -> List[Dict[str, Any]]:
        """
        Returns roster items that are currently active (tier0/1 or non-expired tier2).
        """
        active = []
        today = datetime.now().strftime("%Y-%m-%d")
        for item in self.data.get("roster", []):
            tier = item.get("tier")
            if tier in ["tier0", "tier1"]:
                active.append(item)
            elif tier == "tier2":
                expire_date = item.get("expire_date")
                if expire_date and expire_date >= today:
                    active.append(item)
        return active

    def get_sources_for_collection(self) -> List[Dict[str, Any]]:
        """
        Flattened list of sources from active roster items.
        """
        sources = []
        for item in self.get_active_roster():
            for src in item.get("official_sources", []):
                source_info = src.copy()
                source_info["id"] = item["id"]
                source_info["name"] = item["name"]
                source_info["organization"] = item.get("organization") or item["name"]
                source_info["domain_allowlist"] = item.get("domain_allowlist", [])
                source_info["priority"] = item.get("priority", 3)
                source_info["tier"] = item.get("tier")
                sources.append(source_info)
        return sources

    def get_item_by_id(self, roster_id: str) -> Optional[Dict[str, Any]]:
        for item in self.data.get("roster", []):
            if item.get("id") == roster_id:
                return item
        return None
