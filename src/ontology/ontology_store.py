import json
from pathlib import Path
from typing import Dict, Any

class OntologyStore:
    def __init__(self, project_root: Path):
        self.ontology_path = project_root / "data" / "ontology" / "topic_ontology.json"
        self.resolved_path = project_root / "data" / "ontology" / "topic_resolved.json"
        self.ontology_path.parent.mkdir(parents=True, exist_ok=True)

    def load_ontology(self) -> Dict[str, Any]:
        if not self.ontology_path.exists():
            return {}
        try:
            return json.loads(self.ontology_path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[OntologyStore] Error loading ontology: {e}")
            return {}

    def save_resolved(self, data: Any):
        try:
            self.resolved_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception as e:
            print(f"[OntologyStore] Error saving resolved data: {e}")

    def load_resolved(self) -> Any:
        if not self.resolved_path.exists():
            return []
        try:
            return json.loads(self.resolved_path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[OntologyStore] Error loading resolved data: {e}")
            return []
