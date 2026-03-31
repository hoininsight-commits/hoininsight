import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from .ontology_store import OntologyStore
from .ontology_resolver import OntologyResolver

class TopicOntologyEngine:
    def __init__(self, project_root: Optional[Path] = None):
        self.root = project_root or Path(".").resolve()
        self.store = OntologyStore(self.root)
        self.resolver = OntologyResolver(self.store)

    def run_daily_resolution(self) -> List[Dict[str, Any]]:
        """
        Reads today's topics and resolves them.
        """
        print("[TopicOntologyEngine] Starting daily resolution...")
        
        # 1. Load today's topics from decision card
        # Logic similar to Memory Engine
        from datetime import datetime, timezone, timedelta
        kst_now = datetime.now(timezone.utc) + timedelta(hours=9)
        ymd = kst_now.strftime("%Y/%m/%d")
        decision_file = self.root / "data" / "decision" / ymd / "final_decision_card.json"
        
        resolved_topics = []
        
        if not decision_file.exists():
            print(f"[TopicOntologyEngine] No decision card found for {ymd}")
            return []

        try:
            card = json.loads(decision_file.read_text(encoding="utf-8"))
            topics = card.get("top_topics", [])
            for t in topics:
                title = t.get("title", "")
                if title:
                    ontology = self.resolver.resolve(title)
                    resolved_topics.append({
                        "topic": title,
                        "theme": ontology.get("theme"),
                        "sector": ontology.get("sector"),
                        "macro": ontology.get("macro"),
                        "resolved_at": datetime.now().isoformat()
                    })
            
            # Save resolved results
            self.store.save_resolved(resolved_topics)
            print(f"[TopicOntologyEngine] Resolved {len(resolved_topics)} topics.")
            
        except Exception as e:
            print(f"[TopicOntologyEngine] Error during resolution: {e}")

        return resolved_topics

if __name__ == "__main__":
    from typing import Optional
    engine = TopicOntologyEngine()
    engine.run_daily_resolution()
