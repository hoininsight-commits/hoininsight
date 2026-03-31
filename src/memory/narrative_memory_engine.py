import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from src.memory.narrative_memory_store import NarrativeMemoryStore

class NarrativeMemoryEngine:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.store = NarrativeMemoryStore(base_dir)
        self.logger = logging.getLogger("NarrativeMemory")
        # Integration: Ontology Resolver
        from src.ontology.ontology_store import OntologyStore
        from src.ontology.ontology_resolver import OntologyResolver
        self.ontology_resolver = OntologyResolver(OntologyStore(base_dir))

    def record_today_topics(self, date_str: str):
        """Extract topics from today's decision card and record to history."""
        decision_path = self.base_dir / "data" / "decision" / date_str.replace("-", "/") / "final_decision_card.json"
        
        if not decision_path.exists():
            self.logger.warning(f"No decision card found for {date_str} at {decision_path}")
            return

        try:
            data = json.loads(decision_path.read_text(encoding="utf-8"))
            topics = data.get("top_topics", [])
            if not isinstance(topics, list):
                topics = [topics] if topics else []

            history = self.store.load_history()
            
            for t in topics:
                if not t: continue
                
                title = t.get("title")
                # Resolve Ontology
                ontology = self.ontology_resolver.resolve(title)

                entry = {
                    "date": date_str,
                    "topic_id": t.get("topic_id"),
                    "title": title,
                    "category": t.get("category", "General"),
                    "theme": ontology.get("theme"),
                    "sector": ontology.get("sector"),
                    "macro": ontology.get("macro"),
                    "dataset_id": t.get("dataset_id"),
                    "intensity": t.get("intensity") or t.get("score"),
                    "captured_at": datetime.now().isoformat()
                }
                
                # Check for duplicates on same date
                is_duplicate = any(h["date"] == entry["date"] and h["title"] == entry["title"] for h in history)
                if not is_duplicate:
                    history.append(entry)
                    self.logger.info(f"Recorded memory entry with ontology: {entry['title']} -> {entry['theme']}")

            self.store.save_history(history)
            
        except Exception as e:
            self.logger.error(f"Failed to record topics: {e}")

if __name__ == "__main__":
    import os
    logging.basicConfig(level=logging.INFO)
    engine = NarrativeMemoryEngine(Path("."))
    today = datetime.now().strftime("%Y-%m-%d")
    engine.record_today_topics(today)
