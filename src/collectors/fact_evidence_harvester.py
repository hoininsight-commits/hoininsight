from __future__ import annotations
import json
import uuid
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# [IS-55] Import Real Ingress Connector
from src.collectors.real_ingress_connector import collect_rss_headlines, collect_official_releases, collect_market_proxy

class FactEvidenceHarvester:
    """
    Lightweight fact-harvesting layer.
    Collects minimal factual anchors for early topic creation.
    No judgment, no scoring.
    """
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.output_root = base_dir / "data" / "facts"
        self.output_root.mkdir(parents=True, exist_ok=True)
        
    def harvest(self, target_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Main harvesting loop using Real Ingress Connectors.
        """
        ymd = target_date or datetime.utcnow().strftime("%Y-%m-%d")
        facts = []
        
        # 1. RSS/News Headlines (Real)
        rss_data = collect_rss_headlines(self.base_dir, ymd)
        facts.extend(self._process_rss(rss_data, ymd))
        
        # 2. Institutional Releases (Real)
        official_data = collect_official_releases(self.base_dir, ymd)
        facts.extend(self._process_official(official_data, ymd))
        
        # 3. Market Proxy (Sync)
        # We ensure the raw data exists, even if we don't converting it all to text anchors yet.
        collect_market_proxy(self.base_dir, ymd)
        
        if facts:
            self._save_facts(facts, ymd)
        
        print(f"[Harvester] Completed harvest for {ymd}. Found {len(facts)} facts.")
        return facts

    def _process_rss(self, raw_items: List[Dict], ymd: str) -> List[Dict[str, Any]]:
        """Convert RSS raw items to Fact format."""
        processed = []
        for item in raw_items:
            # Basic parsing using title as text
            processed.append({
                "text": item.get("title", ""),
                "source": item.get("source_name", "RSS"),
                "type": "NEWS",
                "entities": [], # Entity extraction removed to keep it lightweight/raw
                "url": item.get("link", "")
            })
        return [self._format_fact(d, ymd) for d in processed]

    def _process_official(self, raw_items: List[Dict], ymd: str) -> List[Dict[str, Any]]:
        """Convert Official raw items to Fact format."""
        processed = []
        for item in raw_items:
            processed.append({
                "text": item.get("title", ""),
                "source": item.get("source", "OFFICIAL"),
                "type": "POLICY",
                "entities": [],
                "url": item.get("link", "")
            })
        return [self._format_fact(d, ymd) for d in processed]

    def _format_fact(self, data: Dict[str, Any], ymd: str) -> Dict[str, Any]:
        return {
            "fact_id": f"fact_{uuid.uuid4().hex[:8]}",
            "fact_type": data["fact_type"] if "fact_type" in data else data.get("type", "UNKNOWN"),
            "fact_text": data["text"],
            "source": data["source"],
            "url": data.get("url", ""),
            "published_at": ymd,
            "entities": data.get("entities", []),
            "confidence": "RAW"
        }

    def _save_facts(self, facts: List[Dict[str, Any]], ymd: str):
        # Format: YYYYMMDD
        ymd_compact = ymd.replace("-", "")
        filename = f"fact_anchors_{ymd_compact}.json"
        
        # Ensure directory (year/month/day structure optional, but current code uses flat or flat-ish)
        # Checking existing structure usage: data/facts/fact_anchors_YYYYMMDD.json
        out_path = self.output_root / filename
        
        # Load existing if any
        existing = []
        if out_path.exists():
            try:
                existing = json.loads(out_path.read_text(encoding="utf-8"))
            except: pass
            
        # Deduplicate by text
        seen_texts = {f["fact_text"] for f in existing}
        new_facts = [f for f in facts if f["fact_text"] not in seen_texts]
        
        combined = existing + new_facts
        
        out_path.write_text(json.dumps(combined, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[Harvester] Saved {len(combined)} facts to {filename}")

if __name__ == "__main__":
    harvest = FactEvidenceHarvester(Path("."))
    harvest.harvest()
