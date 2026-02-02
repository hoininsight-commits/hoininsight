import json
from pathlib import Path
from typing import List, Dict, Any

class StatementCollector:
    """
    [IS-93] Data Supply for Statement/Document Layer
    Loads narrative materials from data/raw/statements/
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.data_dir = base_dir / "data" / "raw" / "statements"
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def collect(self) -> List[Dict[str, Any]]:
        # [IS-93R] Real data is now supplied by OfficialStatementCollector and PolicyDocumentCollector
        # This loader now only reads from data/raw/statements/ if any external data was pre-cached.
        results = []
        
        # 1. Load from files if they exist
        for f in self.data_dir.glob("*.json"):
            try:
                results.extend(json.loads(f.read_text(encoding="utf-8")))
            except:
                pass
                
        return results
