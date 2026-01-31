import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from src.ops.post_mortem_tracker import PostMortemTracker
from src.ops.operator_decision_log import OPERATOR_ACTION_ENUM

class PickOutcomeCorrelator:
    """
    Step 41: Correlates human editorial picks with retrospective engine outcomes.
    Purpose: Accountability & Learning.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.decision_dir = base_dir / "data" / "ops" / "operator_decisions"
        self.tracker = PostMortemTracker(base_dir)

    def run(self, run_date: str, lookback_days: int = 30) -> Dict[str, Any]:
        """
        Processes logs for [run_date - lookback, run_date] and joins with outcomes.
        """
        end_dt = datetime.strptime(run_date, "%Y-%m-%d")
        start_dt = end_dt - timedelta(days=lookback_days)
        
        # Load all history for post-mortem evaluation
        # We need a bit more buffer to see performance of picks from the start of the window
        # PostMortemTracker.evaluate_topic usually needs history up to today.
        history_start = (start_dt - timedelta(days=90)).strftime("%Y-%m-%d") # Buffer for LONG window
        history = self.tracker.load_history(history_start, run_date)
        
        rows = []
        summary = {
            "picked": 0,
            "confirmed": 0,
            "failed": 0,
            "unresolved": 0,
            "missing": 0
        }
        errors = []

        curr = start_dt
        while curr <= end_dt:
            ymd = curr.strftime("%Y-%m-%d")
            log_path = self.decision_dir / f"{ymd}.json"
            if log_path.exists():
                try:
                    data = json.loads(log_path.read_text(encoding="utf-8"))
                    decisions = data.get("decisions", [])
                    for d in decisions:
                        if d.get("operator_action") == OPERATOR_ACTION_ENUM.PICKED_FOR_CONTENT:
                            summary["picked"] += 1
                            row = self._correlate_pick(d, ymd, history)
                            rows.append(row)
                            
                            # Increment summary based on outcome
                            outcome = row["outcome"]
                            if outcome == "CONFIRMED": summary["confirmed"] += 1
                            elif outcome == "FAILED": summary["failed"] += 1
                            elif outcome == "UNRESOLVED": summary["unresolved"] += 1
                            else: summary["missing"] += 1

                except Exception as e:
                    errors.append(f"Error processing {ymd}: {str(e)}")
            curr += timedelta(days=1)

        # Sort: Most recent pick first
        rows.sort(key=lambda x: x["pick_date"], reverse=True)

        result = {
            "run_date": run_date,
            "lookback_days": lookback_days,
            "rows": rows,
            "summary": summary,
            "errors": errors
        }

        # Save to data/ops/pick_outcome_30d.json
        out_path = self.base_dir / "data" / "ops" / "pick_outcome_30d.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        
        return result

    def _correlate_pick(self, decision: Dict[str, Any], pick_date: str, history: Dict[str, Any]) -> Dict[str, Any]:
        """Strict Join: topic_id -> normalized title -> outcome."""
        topic_id = decision.get("topic_id")
        title = decision.get("topic_title", "")
        
        outcome = "MISSING"
        outcome_date = None
        
        # 1. Search in history for the actual outcome
        # PostMortemTracker.evaluate_topic is designed for card metadata.
        # Let's see if we can find the specific topic in history to get its outcome.
        
        # Find the topic in the daily_lock of the pick_date to get its impact_window
        lock_data = history.get(pick_date)
        topic_meta = None
        if lock_data:
            for c in lock_data.get("cards", []):
                # Match by ID or Title
                if (topic_id and c.get("topic_id") == topic_id) or (c.get("title", "").strip().lower() == title.strip().lower()):
                    topic_meta = c
                    break
        
        if topic_meta:
            res_outcome = self.tracker.evaluate_topic(topic_meta, pick_date, history)
            outcome = res_outcome
            # Find when it was confirmed (simplistic: check chronological history)
            # PostMortemTracker doesn't return date, let's keep it null or infer if confirmed.
        
        return {
            "pick_date": pick_date,
            "topic_id": topic_id,
            "topic_title": title,
            "impact_tag": topic_meta.get("impact_window") if topic_meta else None,
            "outcome": outcome,
            "outcome_date": None, # Future enhancement: find the exact day it flipped
            "notes": decision.get("note")
        }

if __name__ == "__main__":
    import sys
    base = Path.cwd()
    ymd = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d")
    correlator = PickOutcomeCorrelator(base)
    correlator.run(ymd)
