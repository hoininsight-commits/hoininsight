import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class OPERATOR_ACTION_ENUM:
    PICKED_FOR_CONTENT = "PICKED_FOR_CONTENT"
    SKIPPED_TODAY = "SKIPPED_TODAY"
    DEFERRED = "DEFERRED"
    REJECTED = "REJECTED"

class OperatorDecisionLog:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.log_dir = base_dir / "data" / "ops" / "operator_decisions"

    def _get_log_path(self, ymd: str) -> Path:
        return self.log_dir / f"{ymd}.json"

    def log_decision(self, ymd: str, decision: Dict[str, Any]):
        """
        Appends a decision to the daily log.
        decision schema: {topic_id, topic_title, topic_type, readiness_bucket?, operator_action, note?}
        """
        self.log_dir.mkdir(parents=True, exist_ok=True)
        path = self._get_log_path(ymd)
        
        data = {"run_date": ymd, "decisions": []}
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except:
                pass
        
        # Append logic
        entry = {
            **decision,
            "ts": datetime.utcnow().isoformat()
        }
        data["decisions"].append(entry)
        
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def load_decisions(self, ymd: str) -> Dict[str, Any]:
        """Loads all decisions for a specific date."""
        path = self._get_log_path(ymd)
        if not path.exists():
            return {"run_date": ymd, "decisions": []}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except:
            return {"run_date": ymd, "decisions": []}

    def get_latest_decisions_map(self, ymd: str) -> Dict[str, Dict[str, Any]]:
        """Returns {topic_id: latest_decision} map for the day."""
        data = self.load_decisions(ymd)
        decisions = data.get("decisions", [])
        
        # Last one wins for the same topic_id on the same day
        dec_map = {}
        for d in decisions:
            tid = d.get("topic_id")
            if tid:
                dec_map[tid] = d
        return dec_map
