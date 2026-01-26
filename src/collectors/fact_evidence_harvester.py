from __future__ import annotations
import json
import uuid
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

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
        Main harvesting loop.
        In production, this would crawl RSS feeds/news APIs.
        For this step, we emulate collection from passive sources.
        """
        ymd = target_date or datetime.utcnow().strftime("%Y-%m-%d")
        facts = []
        
        # 1. Emulate RSS/News Headlines collection
        facts.extend(self._harvest_headlines(ymd))
        
        # 2. Emulate Institutional Releases
        facts.extend(self._harvest_institutional(ymd))
        
        # 3. Emulate Capital Flow text summaries
        facts.extend(self._harvest_flows(ymd))
        
        if facts:
            self._save_facts(facts, ymd)
            
        return facts

    def _harvest_headlines(self, ymd: str) -> List[Dict[str, Any]]:
        # Mocking reality: news titles from known publishers
        mock_data = [
            {
                "text": "Nvidia confirms new AI chip delivery schedule for H2 2026",
                "source": "TechNews RSS",
                "type": "TECH",
                "entities": ["Nvidia", "AI", "Semiconductors"]
            },
            {
                "text": "Goldman Sachs reports 15% increase in institutional crypto flow",
                "source": "FinanceDaily RSS",
                "type": "FLOW",
                "entities": ["Goldman Sachs", "Crypto", "Institutional"]
            }
        ]
        return [self._format_fact(d, ymd) for d in mock_data]

    def _harvest_institutional(self, ymd: str) -> List[Dict[str, Any]]:
        mock_data = [
            {
                "text": "ECB policy document: Focus shifts to long-term inflation stability over short-term cuts",
                "source": "ECB Official",
                "type": "POLICY",
                "entities": ["ECB", "Eurozone", "Inflation"]
            }
        ]
        return [self._format_fact(d, ymd) for d in mock_data]

    def _harvest_flows(self, ymd: str) -> List[Dict[str, Any]]:
        # For MISSION: verbatim or lightly cleaned textual summaries
        return []

    def _format_fact(self, data: Dict[str, Any], ymd: str) -> Dict[str, Any]:
        return {
            "fact_id": f"fact_{uuid.uuid4().hex[:8]}",
            "fact_type": data["type"],
            "fact_text": data["text"],
            "source": data["source"],
            "published_at": ymd,
            "entities": data["entities"],
            "confidence": "RAW"
        }

    def _save_facts(self, facts: List[Dict[str, Any]], ymd: str):
        filename = f"fact_anchors_{ymd.replace('-', '')}.json"
        out_path = self.output_root / filename
        
        # Load existing if any (to avoid overwriting if run multiple times)
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
        print(f"[Harvester] Harvested {len(new_facts)} new facts. Total for {ymd}: {len(combined)}")

if __name__ == "__main__":
    harvest = FactEvidenceHarvester(Path("."))
    harvest.harvest()
