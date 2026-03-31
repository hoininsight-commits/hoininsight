import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

class NarrativeMemoryStore:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.history_path = base_dir / "data" / "memory" / "narrative_history.json"
        self.patterns_path = base_dir / "data" / "memory" / "narrative_patterns.json"
        self._ensure_files()

    def _ensure_files(self):
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.history_path.exists():
            self.history_path.write_text(json.dumps([], indent=2), encoding="utf-8")
        if not self.patterns_path.exists():
            self.patterns_path.write_text(json.dumps({}, indent=2), encoding="utf-8")

    def load_history(self) -> List[Dict]:
        try:
            return json.loads(self.history_path.read_text(encoding="utf-8"))
        except:
            return []

    def save_history(self, history: List[Dict]):
        self.history_path.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")

    def load_patterns(self) -> Dict:
        try:
            return json.loads(self.patterns_path.read_text(encoding="utf-8"))
        except:
            return {}

    def save_patterns(self, patterns: Dict):
        self.patterns_path.write_text(json.dumps(patterns, indent=2, ensure_ascii=False), encoding="utf-8")
