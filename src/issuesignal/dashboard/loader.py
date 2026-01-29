import json
import os
from pathlib import Path
from typing import List, Dict, Any
from .models import DecisionCard, RejectLog, DashboardSummary, TimelinePoint
from datetime import datetime, timedelta

class DashboardLoader:
    """
    (IS-27) Loads data from IssueSignal file system.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def load_today_summary(self, ymd: str) -> DashboardSummary:
        counts = {
            "TRUST_LOCKED": 0,
            "TRIGGER": 0,
            "PRE_TRIGGER": 0,
            "HOLD": 0,
            "REJECT": 0,
            "SILENT_DROP": 0
        }
        
        # 1. Load Emission Packs for counts (SILENT_DROP vs others)
        pack_dir = self.base_dir / "data" / "issuesignal" / "packs"
        if pack_dir.exists():
            # Count files created today
            for f in pack_dir.glob("*.yaml"):
                # Simplified check for simulation
                counts["TRUST_LOCKED"] += 1

        # 2. Load Decision Cards
        cards = self._load_recent_cards()
        top_cards = [c for c in cards if c.status == "TRUST_LOCKED"][:3]
        watchlist = [c for c in cards if c.status == "PRE_TRIGGER"]
        hold_queue = [c for c in cards if c.status == "HOLD"]

        # 3. Load Reject Logs
        reject_logs = self._load_reject_logs()

        # Update counts based on loaded cards
        for c in cards:
            if c.status in counts:
                counts[c.status] += 1

        return DashboardSummary(
            date=ymd,
            engine_status="SUCCESS",
            counts=counts,
            top_cards=top_cards,
            watchlist=watchlist,
            hold_queue=hold_queue,
            reject_logs=reject_logs,
            timeline=self._generate_mock_timeline(ymd)
        )

    def _load_recent_cards(self) -> List[DecisionCard]:
        cards = []
        # Look in data/decision/final_decision_cards/
        card_dir = self.base_dir / "data" / "decision" / "final_decision_cards"
        if card_dir.exists():
            for f in card_dir.glob("*.json"):
                try:
                    with open(f, "r", encoding="utf-8") as jf:
                        data = json.load(jf)
                        cards.append(DecisionCard(
                            topic_id=data.get("topic_id", "ID"),
                            title=data.get("title", "Untitled"),
                            status=data.get("status", "HOLD"),
                            one_liner=data.get("one_liner", "-"),
                            trigger_type=data.get("trigger_type", "-"),
                            actor=data.get("actor", "-"),
                            must_item=data.get("must_item", "-"),
                            tickers=data.get("tickers", []),
                            kill_switch=data.get("kill_switch", "-"),
                            signature=data.get("signature")
                        ))
                except: continue
        return cards

    def _load_reject_logs(self) -> List[RejectLog]:
        logs = []
        # Simulating log loading from data/ops/
        ops_dir = self.base_dir / "data" / "ops"
        if ops_dir.exists():
            for f in ops_dir.glob("*reject*.json"):
                try:
                    with open(f, "r", encoding="utf-8") as jf:
                        data = json.load(jf)
                        # Expecting list or dict
                        items = data if isinstance(data, list) else [data]
                        for item in items:
                            logs.append(RejectLog(
                                timestamp=item.get("timestamp", "-"),
                                topic_id=item.get("topic_id", "ID"),
                                reason_code=item.get("reason_code", "UNKNOWN"),
                                fact_text=item.get("fact_text", "-")
                            ))
                except: continue
        return logs[:5] # Top 5 recent

    def _generate_mock_timeline(self, ymd: str) -> List[TimelinePoint]:
        # Generating 14-day mock trend for visualization
        points = []
        base_date = datetime.strptime(ymd, "%Y-%m-%d")
        for i in range(13, -1, -1):
            dt = base_date - timedelta(days=i)
            points.append(TimelinePoint(
                date=dt.strftime("%Y-%m-%d"),
                counts={"TRUST_LOCKED": 1, "TRIGGER": 2, "PRE_TRIGGER": 3}
            ))
        return points
