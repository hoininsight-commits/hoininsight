from typing import Dict, Any, Optional
from .ontology_store import OntologyStore

class OntologyResolver:
    def __init__(self, store: OntologyStore):
        self.store = store
        self.ontology = self.store.load_ontology()

    def resolve(self, topic: str) -> Dict[str, str]:
        """
        Resolves a topic string to its ontology components.
        If no exact match, performs basic keyword matching or returns default.
        """
        # 1. Exact Match
        if topic in self.ontology:
            return self.ontology[topic]

        # 2. Simple Keyword Match (Partial)
        for key, mapping in self.ontology.items():
            if key.lower() in topic.lower() or topic.lower() in key.lower():
                return mapping

        # 3. Default Fallback
        return {
            "theme": "General Interest",
            "sector": "Diverse",
            "macro": "Market Neutral"
        }
