from datetime import datetime
from pathlib import Path
import json

class IssuePool:
    """
    (IS-2) Manages the collection of global signals.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.pool_dir = base_dir / "data" / "issuesignal" / "pool"
        self.pool_dir.mkdir(parents=True, exist_ok=True)

    def add_issue(self, signal: dict):
        signal_id = f"RAW-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        file_path = self.pool_dir / f"{signal_id}.json"
        
        payload = {
            "id": signal_id,
            "captured_at": datetime.utcnow().isoformat(),
            "source": signal.get("source", "UNKNOWN"),
            "content": signal.get("content", ""),
            "metadata": signal.get("metadata", {})
        }
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        return signal_id

    def list_pending(self):
        return list(self.pool_dir.glob("*.json"))
