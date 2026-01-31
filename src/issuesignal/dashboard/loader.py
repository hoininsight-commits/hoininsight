import json
import os
from pathlib import Path
from typing import List, Dict, Any
from .models import DecisionCard, RejectLog, DashboardSummary, TimelinePoint, HoinEvidenceItem, UnifiedLinkRow, ProofPack, HardFact, TriggerQuote, SourceCluster
from datetime import datetime, timedelta

class DashboardLoader:
    """
    (IS-27) Loads data from IssueSignal file system.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def load_today_summary(self, ymd_requested: str) -> DashboardSummary:
        # (IS-48) Read SSOT index first
        index_path = self.base_dir / "data" / "issuesignal" / "packs" / "latest_index.json"
        index_data = {}
        if index_path.exists():
            try:
                with open(index_path, "r", encoding="utf-8") as f:
                    index_data = json.load(f)
            except: pass

        ymd = index_data.get("run_date_kst", ymd_requested)
        
        counts = {
            "TRUST_LOCKED": index_data.get("topics_active", 0),
            "TRIGGER": 0,
            "PRE_TRIGGER": 0,
            "HOLD": index_data.get("topics_hold", 0),
            "REJECT": index_data.get("topics_silent", 0),
            "SILENT_DROP": index_data.get("topics_silent", 0)
        }
        
        # 2. Load Decision Cards (Use pinned IDs from index if available)
        pinned_ids = index_data.get("pinned_topic_ids", [])
        cards = self._load_recent_cards()
        
        # Priority sort: Pinned first
        top_cards = []
        if pinned_ids:
            pinned_map = {c.topic_id: c for c in cards}
            for pid in pinned_ids:
                if pid in pinned_map and pinned_map[pid].status == "TRUST_LOCKED":
                    top_cards.append(pinned_map[pid])
        
        if not top_cards:
            # [IS-52] Strict Lock: If SSOT says 0 topics today, DO NOT show old cards.
            fresh_index = (index_data.get("run_date_kst") == ymd)
            if fresh_index and index_data.get("topics_active", 0) == 0:
                top_cards = []
            else:
                # Fallback only if no fresh index or index implies topics exist but pinned_ids missing
                top_cards = [c for c in cards if c.status == "TRUST_LOCKED"][:3]

        watchlist = [c for c in cards if c.status == "PRE_TRIGGER"]
        hold_queue = [c for c in cards if c.status == "HOLD"]

        # 3. Load Reject Logs
        reject_logs = self._load_reject_logs()
        
        # (IS-48) Enrich reject logs with Top Reasons from index if counts are zero
        if not reject_logs and index_data.get("top_reason_counts"):
            for entry in index_data["top_reason_counts"]:
                reject_logs.append(RejectLog(
                    timestamp=index_data.get("run_ts_kst", "-"),
                    topic_id="SUMMARY",
                    reason_code=entry["reason"],
                    fact_text=f"전체 {entry['count']}건의 토픽이 이 사유로 보류/개선 중입니다."
                ))

        # 4. Load Hoin Evidence (IS-29)
        hoin_evidence = self._load_hoin_evidence(ymd)
        
        # 5. Create Link View (IS-29)
        link_view = self._create_link_view(cards, hoin_evidence)

        return DashboardSummary(
            date=ymd,
            engine_status="SUCCESS",
            counts=counts,
            top_cards=top_cards,
            watchlist=watchlist,
            hold_queue=hold_queue,
            reject_logs=reject_logs,
            timeline=self._generate_mock_timeline(ymd),
            hoin_evidence=hoin_evidence,
            link_view=link_view
        )

    def _load_recent_cards(self) -> List[DecisionCard]:
        cards = []
        # Look in data/decision/final_decision_cards/
        card_dir = self.base_dir / "data" / "issuesignal" / "packs"
        if card_dir.exists():
            # Sort files descending to get latest first
            json_files = sorted(card_dir.glob("*.json"), reverse=True)
            for f in json_files:
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
                            signature=data.get("signature"),
                            authority_sentence=data.get("authority_sentence", "-"),
                            forced_capex=data.get("forced_capex", "-"),
                            bottleneck=data.get("bottleneck", "-"),
                            proof_packs=[ProofPack(
                                ticker=p.get("ticker", ""),
                                company_name=p.get("company_name", ""),
                                bottleneck_role=p.get("bottleneck_role", ""),
                                why_irreplaceable_now=p.get("why_irreplaceable_now", ""),
                                proof_status=p.get("proof_status", "PROOF_FAIL"),
                                hard_facts=[HardFact(**f_dict) for f_dict in p.get("hard_facts", [])]
                            ) for p in data.get("proof_packs", [])],
                            trigger_quote=TriggerQuote(**data.get("trigger_quote")) if data.get("trigger_quote") else None,
                            source_clusters=[SourceCluster(**c) for c in data.get("source_clusters", [])]
                        ))
                except Exception as e:
                    print(f"ERROR: Failed to load card {f}: {e}")
                    continue
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

    def _load_hoin_evidence(self, ymd: str) -> List[HoinEvidenceItem]:
        evidence = []
        # Location 1: data/decision/YYYY/MM/DD/final_decision_card.json
        ymd_path = ymd.replace("-", "/")
        final_card_path = self.base_dir / "data" / "decision" / ymd_path / "final_decision_card.json"
        if final_card_path.exists():
            try:
                with open(final_card_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    topics = data.get("top_topics", [])
                    for t in topics:
                        evidence.append(HoinEvidenceItem(
                            title=t.get("title", t.get("topic", "Untitled")),
                            summary=t.get("one_line_summary", t.get("rationale", "-")),
                            date=ymd,
                            source_file=str(final_card_path.relative_to(self.base_dir)),
                            bullets=[t.get("impact", "-"), t.get("action", "-")] if "impact" in t else [],
                            tickers=t.get("tickers", []),
                            topic_key=t.get("topic_id")
                        ))
            except: pass

        # Location 2: data/snapshots/memory/YYYY-MM-DD.json
        snapshot_path = self.base_dir / "data" / "snapshots" / "memory" / f"{ymd}.json"
        if snapshot_path.exists():
            try:
                with open(snapshot_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Simplified extraction from snapshot
                    for item in data.get("entities", [])[:5]:
                        evidence.append(HoinEvidenceItem(
                            title=f"Snapshot: {item.get('name')}",
                            summary=item.get("state", "-"),
                            date=ymd,
                            source_file=str(snapshot_path.relative_to(self.base_dir)),
                            bullets=[f"Score: {item.get('score', 0)}", f"Trend: {item.get('trend', '-')}"]
                        ))
            except: pass
            
        return evidence

    def _create_link_view(self, cards: List[DecisionCard], evidence: List[HoinEvidenceItem]) -> List[UnifiedLinkRow]:
        rows = []
        for card in cards:
            linked = []
            reason = None
            
            card_tickers = {t.get("symbol", "").upper() for t in card.tickers if t.get("symbol")}
            
            for ev in evidence:
                match = False
                # 1. Ticker match
                ev_tickers = {str(t).upper() for t in ev.tickers}
                if card_tickers & ev_tickers:
                    match = True
                    reason = "Ticker Overlap"
                
                # 2. Structural Hash / Topic ID match
                elif ev.topic_key and ev.topic_key == card.topic_id:
                    match = True
                    reason = "Topic ID Match"
                
                if match:
                    linked.append(ev)
            
            status = "MATCHED" if linked else "NO_HOIN_EVIDENCE"
            rows.append(UnifiedLinkRow(
                issue_card=card,
                linked_evidence=linked,
                link_status=status,
                match_reason=reason
            ))
        return rows

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
