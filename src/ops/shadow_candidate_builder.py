import json
import os
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple

class ShadowCandidateBuilder:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def _find_first_seen_date(self, topic_id: str, current_ymd: str, lookback_days: int = 60) -> str:
        """
        Looks back in history to find the first date this topic_id appeared as a candidate.
        Returns first_seen_date. Defaults to current_ymd if not found in history.
        """
        curr_dt = datetime.strptime(current_ymd, "%Y-%m-%d")
        first_seen = current_ymd
        
        # Lookback from yesterday
        for i in range(1, lookback_days + 1):
            target_dt = curr_dt - timedelta(days=i)
            target_ymd = target_dt.strftime("%Y-%m-%d")
            
            gate_dir = self.base_dir / "data" / "topics" / "gate" / target_ymd.replace("-", "/")
            hist_file = gate_dir / "topic_gate_candidates.json"
            
            if hist_file.exists():
                try:
                    h_data = json.loads(hist_file.read_text(encoding="utf-8"))
                    h_candidates = h_data.get("candidates", [])
                    if any(c.get("topic_id") == topic_id for c in h_candidates):
                        first_seen = target_ymd
                    else:
                        # If not found yesterday, but found earlier, it might be a gap.
                        # But rule says "first seen", so we continue searching back.
                        pass
                except:
                    pass
        return first_seen

    def _build_aging_summary(self, shadow_pool: List[Dict[str, Any]]) -> Dict[str, int]:
        summary = {"FRESH": 0, "STALE": 0, "DECAYING": 0, "EXPIRED": 0}
        for c in shadow_pool:
            state = c.get("aging", {}).get("aging_state")
            if state in summary:
                summary[state] += 1
        return summary

    def _build_global_signal_watchlist(self, shadow_pool: List[Dict[str, Any]]) -> Dict[str, int]:
        """Step 37: Aggregates watch signals for global awareness."""
        summary = {
            "NUMERIC_EVIDENCE_APPEAR": 0,
            "SUPPORTING_ANOMALY_DETECTED": 0,
            "POLICY_EVENT_TRIGGERED": 0,
            "EARNINGS_RELEASE": 0,
            "ONCHAIN_CONFIRMATION": 0,
            "MACRO_THRESHOLD_CROSSED": 0
        }
        for c in shadow_pool:
            signals = c.get("watch_signals", [])
            for s in signals:
                if s in summary:
                    summary[s] += 1
        return summary

    def _determine_impact_window(self, topic: Dict[str, Any], tags: List[str]) -> str:
        tags = tags or []
        risk_one = topic.get("risk_one", "")
        reasons = topic.get("key_reasons", [])
        combined_text = (risk_one + " " + " ".join(reasons)).lower()
        
        schedule_keywords = ["d-day", "today", "tomorrow", "scheduled", "timeline", "확정", "발표일"]
        if any(k in combined_text for k in schedule_keywords):
            return "IMMEDIATE"
            
        if any("TIME-SENSITIVE" in t for t in tags):
            return "NEAR"
            
        if any("TRENDING NOW" in t for t in tags):
             return "MID"
             
        if any("STRUCTURAL" in t for t in tags):
             return "LONG"
             
        return "MID"

    def _check_fact_driven(self, topic: Dict) -> bool:
        if topic.get("is_fact_driven") or topic.get("metadata", {}).get("is_fact_driven"):
            return True
        tags = topic.get("tags", [])
        if any(isinstance(tag, str) and tag.startswith("FACT_") for tag in tags):
            return True
        return False

    def build(self, ymd: str) -> Dict[str, Any]:
        gate_dir = self.base_dir / "data" / "topics" / "gate" / ymd.replace("-", "/")
        candidates_file = gate_dir / "topic_gate_candidates.json"
        
        if not candidates_file.exists():
            return {"run_date": ymd, "count": 0, "candidates": []}

        try:
            data = json.loads(candidates_file.read_text(encoding="utf-8"))
            all_topics = data.get("candidates", [])
        except:
            return {"run_date": ymd, "count": 0, "candidates": []}

        shadow_pool = []
        for t in all_topics:
            tid = t.get("topic_id")
            if not tid: continue

            # Load quality info
            quality_file = gate_dir / f"script_v1_{tid}.md.quality.json"
            if not quality_file.exists():
                continue

            try:
                q_data = json.loads(quality_file.read_text(encoding="utf-8"))
                quality_status = q_data.get("quality_status", "DROP")
                failure_codes = q_data.get("failure_codes", [])
            except:
                continue

            # Eligibility Rule 34-1
            if quality_status not in ["HOLD", "DROP"]:
                continue

            # Condition 1: Fact Driven / Structural / Non-Immediate
            is_fact = self._check_fact_driven(t)
            is_structural = any("STRUCTURAL" in tag for tag in t.get("tags", []))
            impact_window = self._determine_impact_window(t, t.get("tags", []))
            
            eligible_feature = is_fact or is_structural or impact_window != "IMMEDIATE"
            if not eligible_feature:
                continue

            # Condition 2: Not rejected for critical naming/placeholder issues
            if "TITLE_MISMATCH" in failure_codes:
                continue
            
            # If rejected ONLY for PLACEHOLDER_EVIDENCE, excluded? 
            # Prompt: "NOT rejected for: PLACEHOLDER_EVIDENCE only"
            # This means if codes == ["PLACEHOLDER_EVIDENCE"], skip.
            if failure_codes == ["PLACEHOLDER_EVIDENCE"]:
                continue

            # Load trigger map logic
            from src.ops.trigger_map import TriggerMapBuilder
            from src.ops.shadow_aging import ShadowAgingCalculator
            from src.ops.signal_watchlist import SignalWatchlistBuilder
            
            trigger_builder = TriggerMapBuilder()
            aging_calc = ShadowAgingCalculator()
            watchlist_builder = SignalWatchlistBuilder()
            
            # Find first_seen_date (Lookback history)
            first_seen_date = self._find_first_seen_date(tid, ymd)

            # Prepare context for trigger map
            shadow_context = {
                "lane": "FACT" if is_fact else "ANOMALY",
                "impact_window": impact_window,
                "failure_codes": failure_codes
            }
            trigger_map = trigger_builder.build_trigger_map(shadow_context)
            aging_meta = aging_calc.calculate_aging(first_seen_date, ymd)

            # Prepare candidate for watchlist builder
            shadow_cand_data = {
                "topic_id": tid,
                "lane": shadow_context["lane"],
                "impact_window": impact_window,
                "trigger_map": trigger_map,
                "aging": aging_meta
            }
            watchlist_data = watchlist_builder.build_watchlist(shadow_cand_data)

            shadow_pool.append({
                "topic_id": tid,
                "title": t.get("title", "Untitled"),
                "lane": shadow_context["lane"],
                "quality_status": quality_status,
                "why_not_speak": q_data.get("reason", "Quality standards not met"),
                "impact_window": impact_window,
                "trigger_map": trigger_map,
                "aging": aging_meta,
                "first_seen_date": first_seen_date,
                "watch_signals": watchlist_data.get("watch_signals", [])
            })

        # Step 38: Signal Arrival Matching
        from src.ops.signal_arrival_matcher import SignalArrivalMatcher
        matcher = SignalArrivalMatcher(self.base_dir)
        arrival_data = matcher.detect_arrivals(ymd)
        shadow_pool = matcher.match_to_shadows(shadow_pool, arrival_data["arrived_signals"])

        result = {
            "run_date": ymd,
            "count": len(shadow_pool),
            "candidates": shadow_pool,
            "aging_summary": self._build_aging_summary(shadow_pool),
            "global_watchlist": self._build_global_signal_watchlist(shadow_pool),
            "signal_arrival": arrival_data
        }

        output_path = self.base_dir / "data" / "ops" / "shadow_candidates.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        
        return result

if __name__ == "__main__":
    import sys
    ymd = sys.argv[1] if len(sys.argv) > 1 else datetime.utcnow().strftime("%Y-%m-%d")
    builder = ShadowCandidateBuilder(Path("."))
    builder.build(ymd)
