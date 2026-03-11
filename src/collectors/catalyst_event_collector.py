import os
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

class CatalystEventCollector:
    """
    IS-96-5b: Deterministic Catalyst Event Collector
    Supports manual seeds and keyword-based entity extraction.
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.mapping_file = self.project_root / "registry/mappings/catalyst_entities.yml"
        self.manual_seed_file = self.project_root / "data/ops/manual_catalyst_events.yml"
        self.output_file = self.project_root / "data/ops/catalyst_events.json"
        
        # Load mappings
        self.mappings = self._load_mappings()

    def _load_mappings(self) -> Dict[str, str]:
        if not self.mapping_file.exists():
            return {}
        with open(self.mapping_file, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def collect(self) -> List[Dict[str, Any]]:
        events = []
        
        # 1. Load Manual Seeds
        if self.manual_seed_file.exists():
            with open(self.manual_seed_file, "r", encoding="utf-8") as f:
                manual_events = yaml.safe_load(f) or []
                for me in manual_events:
                    events.append(self._standardize_event(me))
        
        # 2. Add logic for other sources here if needed (RSS, etc.)
        
        # Deduplicate and Save
        seen_ids = set()
        unique_events = []
        for e in events:
            if e["event_id"] not in seen_ids:
                unique_events.append(e)
                seen_ids.add(e["event_id"])
                
        self._save_events(unique_events)
        return unique_events

    def _standardize_event(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        title = raw.get("title", "")
        entities = self._extract_entities(title, raw.get("entities", []))
        
        return {
            "event_id": raw.get("event_id", f"evt_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hash(title) % 10000}"),
            "as_of_date": raw.get("as_of_date", datetime.now().strftime("%Y-%m-%d")),
            "source_id": raw.get("source_id", "manual"),
            "source_tier": raw.get("source_tier", "tier2"),
            "title": title,
            "url": raw.get("url", ""),
            "entities": entities,
            "event_type": raw.get("event_type", "other"),
            "trust_score": raw.get("trust_score", 0.5),
            "tag": raw.get("tag", "GENERAL_CATALYST"), # Compatibility with IS-95-2
            "confidence": self._map_to_abc(raw.get("trust_score", 0.5))
        }

    def _extract_entities(self, title: str, provided_entities: List[str]) -> List[str]:
        found = set(provided_entities)
        title_low = str(title).lower()
        for keyword, entity in self.mappings.items():
            if str(keyword).lower() in title_low:
                found.add(str(entity))
        return sorted(list(found))

    def _map_to_abc(self, score: float) -> str:
        if score >= 0.8: return "A"
        if score >= 0.5: return "B"
        return "C"

    def _save_events(self, events: List[Dict[str, Any]]):
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_file, "w", encoding="utf-8") as f:
            json.dump(events, f, ensure_ascii=False, indent=2)
        print(f"[OK] Saved {len(events)} catalyst events to {self.output_file}")

if __name__ == "__main__":
    collector = CatalystEventCollector()
    collector.collect()
