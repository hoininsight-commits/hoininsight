import json
import yaml
import hashlib
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

class CatalystEventCollector:
    """
    IS-95-2: Catalyst Event Sensing Layer
    Collects and classifies corporate/regulatory events using deterministic rules.
    """

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.registry_path = self.project_root / "registry/sources/catalyst_source_registry_v1.yml"
        self.output_path = self.project_root / "data/ops/catalyst_events.json"
        
        # Load registry
        with open(self.registry_path, "r", encoding="utf-8") as f:
            self.registry = yaml.safe_load(f)
            
        self.entity_patterns = self.registry.get("entity_patterns", {})

    def collect(self) -> List[Dict[str, Any]]:
        """
        Main collection entry point.
        In a real environment, this would fetch from RSS/APIs.
        For IS-95-2 implementation, we implement the processing logic.
        """
        raw_items = []
        
        # Simulation/Mock of external fetching (since network might be restricted)
        # This allows testing the deterministic classification logic.
        raw_items.extend(self._simulate_fetching())
        
        processed_events = []
        for item in raw_items:
            event = self._process_item(item)
            if event:
                processed_events.append(event)
                
        # Deduplication
        deduped = self._deduplicate(processed_events)
        
        # Save output
        self._save(deduped)
        
        return deduped

    def _process_item(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Classifies and enriches a raw item based on registry rules."""
        content = item.get("title", "") + " " + item.get("summary", "")
        content = content.lower()
        
        best_match = None
        for rule in self.registry.get("rules", []):
            if any(kw.lower() in content for kw in rule.get("keywords", [])):
                best_match = rule
                break
                
        if not best_match and item.get("tag_mapping"):
            # Fallback to source-level mapping
            best_match = {"catalyst_type": item["tag_mapping"], "confidence": "B"}
            
        if not best_match:
            return None

        # Extract entities
        entities = self._extract_entities(content)
        
        # Generate ID
        event_id = hashlib.sha256(f"{item.get('title')}{item.get('date')}".encode()).hexdigest()[:16]
        
        return {
            "event_id": event_id,
            "tag": best_match["catalyst_type"],
            "title": item.get("title"),
            "entities": entities,
            "source": {
                "id": item.get("source_id", "UNKNOWN"),
                "url": item.get("link", "")
            },
            "timestamp": item.get("date", datetime.now().isoformat()),
            "confidence": best_match.get("confidence", "B"),
            "why_now_hint": self._determine_why_now(content),
            "links": [item.get("link", "")]
        }

    def _extract_entities(self, content: str) -> List[str]:
        entities = set()
        
        # Ticker match: 1-5 uppercase letters, ensuring they are not common words
        potential_tickers = re.findall(r"\b[A-Z]{1,5}\b", content.upper())
        noise = {"THE", "AND", "FOR", "USA", "FDA", "FCC", "FAA", "SEC", "CEO", "CFO", "CTO", "LLC", "INC", "CORP", "AGREE", "ON", "WITH", "FROM", "WILL", "NEW", "YEAR", "TERM"}
        for t in potential_tickers:
            if t not in noise:
                entities.add(t)
                
        # KR Code match
        codes = re.findall(r"\b\d{6}\b", content)
        entities.update(codes)
        
        # Named Entity (Basic Whitelist/Heuristic)
        # We look for Capitalized Words that are not at the start of a sentence or are clearly nouns.
        # For simplicity in this deterministic layer, we look for matches in a predefined list or title-case sequences.
        named_patterns = re.findall(r"\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b", content)
        for n in named_patterns:
            if len(n) > 3 and n.upper() not in noise and n not in ["Merger", "Acquisition", "Rumor", "Report", "Exclusive", "Sources", "Agreement", "Update"]:
                entities.add(n)
                
        return sorted(list(entities))

    def _determine_why_now(self, content: str) -> str:
        if any(kw in content for kw in ["earnings", "scheduled", "deadline", "auction"]):
            return "Schedule-driven"
        if any(kw in content for kw in ["unexpected", "sudden", "emergency", "break"]):
            return "State-driven"
        return "Hybrid-driven"

    def _deduplicate(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen_ids = set()
        unique_events = []
        for e in events:
            if e["event_id"] not in seen_ids:
                unique_events.append(e)
                seen_ids.add(e["event_id"])
        return unique_events

    def _save(self, events: List[Dict[str, Any]]):
        output = {
            "asof_date": datetime.now().strftime("%Y-%m-%d"),
            "events": events
        }
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        print(f"[OK] Catalyst events saved to {self.output_path}")

    def _simulate_fetching(self) -> List[Dict[str, Any]]:
        """Mocks fetching for deterministic testing of the processing layer."""
        return [
            {
                "source_id": "sec_8k_rss",
                "title": "NVIDIA Corp (NVDA) 8-K Entry into a Material Definitive Agreement",
                "summary": "NVIDIA entered into an agreement with xAI for server supply.",
                "link": "https://www.sec.gov/Archives/edgar/data/1045810/...",
                "date": datetime.now().isoformat(),
                "tag_mapping": "US_SEC_FILING"
            },
            {
                "source_id": "rumor_node",
                "title": "Exclusive: SpaceX and xAI in merger talks, sources say",
                "summary": "SpaceX is reportedly considering a takeover of xAI assets.",
                "link": "https://reputable-news.com/rumor/spacex-xai",
                "date": datetime.now().isoformat()
            },
            {
                "source_id": "krx_disclosure",
                "title": "삼성전자(005930) 주요사항보고서(유상증자 결정)",
                "summary": "제3자 배정 유상증자 결정 공시",
                "link": "https://kind.krx.co.kr/...",
                "date": datetime.now().isoformat()
            }
        ]

def run_catalyst_collector(root_dir: str = "."):
    collector = CatalystEventCollector(root_dir)
    return collector.collect()

if __name__ == "__main__":
    run_catalyst_collector()
