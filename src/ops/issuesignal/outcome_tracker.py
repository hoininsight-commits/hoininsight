import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

class OutcomeTracker:
    """
    IS-43: POST_EMISSION_OUTCOME_TRACKER
    Tracks the accuracy and outcomes of emitted/silenced signals.
    """

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.memory_path = base_dir / "data" / "ops" / "learning_memory.json"

    def track_historical_signals(self, current_date_str: str) -> Dict[str, Any]:
        """
        Scans history (T-7 to T-2) to evaluate outcomes.
        """
        current_date = datetime.strptime(current_date_str, "%Y-%m-%d")
        learning_data = self._load_memory()
        
        # In a real environment, we would fetch price/news data here.
        # For this implementation, we simulate scanning history.
        
        # Example historical scan logic
        outcomes = []
        for i in range(2, 8):
            target_date = (current_date - timedelta(days=i)).strftime("%Y-%m-%d")
            # Mock historical data retrieval
            signals = self._get_past_signals(target_date)
            for s in signals:
                outcome = self._evaluate_outcome(s)
                outcomes.append(outcome)
                self._save_to_memory(learning_data, s["topic_id"], outcome)

        return self._summarize_outcomes(outcomes)

    def _get_past_signals(self, date_str: str) -> List[Dict[str, Any]]:
        # Mock loading past gate_output.json
        return [] # Simplified for logic demonstration

    def _evaluate_outcome(self, signal: Dict[str, Any]) -> str:
        # Simplified evaluation logic
        return "정확"

    def _load_memory(self) -> Dict[str, Any]:
        if self.memory_path.exists():
            return json.loads(self.memory_path.read_text(encoding="utf-8"))
        return {"outcomes": {}, "stats": {}}

    def _save_to_memory(self, memory: Dict[str, Any], signal_id: str, outcome: str):
        memory["outcomes"][signal_id] = {
            "outcome": outcome,
            "recorded_at": datetime.now().isoformat()
        }
        # Update stats
        memory["stats"][outcome] = memory["stats"].get(outcome, 0) + 1
        
        self.memory_path.parent.mkdir(parents=True, exist_ok=True)
        self.memory_path.write_text(json.dumps(memory, indent=2, ensure_ascii=False), encoding="utf-8")

    def _summarize_outcomes(self, outcomes: List[str]) -> Dict[str, Any]:
        summary = {}
        for o in outcomes:
            summary[o] = summary.get(o, 0) + 1
        return summary
