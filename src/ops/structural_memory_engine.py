import json
import hashlib
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

class StructuralMemoryEngine:
    """
    Step 85: Saves the daily structural state as an immutable memory snapshot.
    """
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.memory_dir = base_dir / "data" / "snapshots" / "memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
    def save_snapshot(self, 
                      date: str, 
                      top_topic: Dict[str, Any], 
                      entities: List[Dict[str, Any]]) -> Path:
        """
        Creates and saves a snapshot.
        If file exists, it OVERWRITES (assuming re-run on same day updates the view).
        """
        
        # 1. Structure the Snapshot
        top_signal = top_topic.get("top_signal", {})
        snapshot = {
            "date": date,
            "meta": {
                "generated_at": datetime.now().isoformat() + "Z",
                "version": "v1.0"
            },
            "top_signal": {
                "title": top_signal.get("title", ""),
                "trigger": top_signal.get("trigger", ""),
                "intensity": top_signal.get("intensity", ""),
                "rhythm": top_signal.get("rhythm", ""),
                "pressure_type": top_signal.get("pressure_type", "")
            },
            "entities": [
                {
                    "name": e.get("name"),
                    "role": e.get("role"),
                    "state": e.get("state"),
                    "constraints": e.get("constraints", [])
                }
                for e in entities
            ]
        }
        
        # 2. Add Integrity Hash
        content_str = json.dumps(snapshot, sort_keys=True)
        snapshot["memory_hash"] = hashlib.sha256(content_str.encode()).hexdigest()
        
        # 3. Save
        file_path = self.memory_dir / f"{date}.json"
        file_path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False), encoding="utf-8")
        
        return file_path

    def load_snapshot(self, date: str) -> Dict[str, Any]:
        """
        Loads a snapshot for a specific date. Returns None if not found.
        """
        file_path = self.memory_dir / f"{date}.json"
        if not file_path.exists():
            return None
            
        try:
            return json.loads(file_path.read_text(encoding="utf-8"))
        except Exception:
            return None
