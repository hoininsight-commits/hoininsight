import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional

FAMILY_MAP = {
    "earnings": "S1",
    "policy": "S2",
    "regulation": "S2",
    "geopolitics": "S2",
    "macro_release": "S2",
    "flow": "S3",
    "contract": "S4",
    "capital": "S5"
}

class EventCoverageBuilder:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.output_path = base_dir / "data" / "dashboard" / "event_coverage_today.json"

    def _get_events_file(self, ymd: str) -> Path:
        y, m, d = ymd.split("-")
        return self.base_dir / "data" / "events" / y / m / d / "events.json"

    def build(self, run_ymd: str, history_days: int = 14) -> Dict[str, Any]:
        run_dt = datetime.strptime(run_ymd, "%Y-%m-%d")
        
        coverage = {
            "run_date": run_ymd,
            "run_ts": datetime.utcnow().isoformat() + "Z",
            "by_gate_family": {
                "S1": {"events": 0},
                "S2": {"events": 0},
                "S3": {"events": 0},
                "S4": {"events": 0},
                "S5": {"events": 0}
            },
            "by_source": [],
            "global_flags": []
        }

        # 1. Scan Today's Events
        today_file = self._get_events_file(run_ymd)
        today_events = []
        source_counts = {} # source_id -> count
        source_types = {}  # source_id -> type
        
        if today_file.exists():
            try:
                data = json.loads(today_file.read_text(encoding="utf-8"))
                today_events = data.get("events", [])
                for e in today_events:
                    etype = e.get("event_type", "other")
                    fam = FAMILY_MAP.get(etype)
                    if fam:
                        coverage["by_gate_family"][fam]["events"] += 1
                        
                    sid = e.get("source", {}).get("publisher", "unknown")
                    source_counts[sid] = source_counts.get(sid, 0) + 1
                    if sid not in source_types:
                        source_types[sid] = "other" 
            except Exception:
                pass

        # 2. Scan History for Last Seen
        all_sources_history = {} # source_id -> {last_date, last_count}
        
        for i in range(history_days):
            target_dt = run_dt - timedelta(days=i)
            target_ymd = target_dt.strftime("%Y-%m-%d")
            h_file = self._get_events_file(target_ymd)
            
            if h_file.exists():
                try:
                    h_data = json.loads(h_file.read_text(encoding="utf-8"))
                    h_events = h_data.get("events", [])
                    
                    today_h_counts = {}
                    for e in h_events:
                        sid = e.get("source", {}).get("publisher", "unknown")
                        today_h_counts[sid] = today_h_counts.get(sid, 0) + 1
                    
                    for sid, count in today_h_counts.items():
                        if sid not in all_sources_history:
                            all_sources_history[sid] = {
                                "last_seen_date": target_ymd,
                                "last_seen_count": count
                            }
                except Exception:
                    pass

        # 3. Assemble by_source
        for sid, hist in all_sources_history.items():
            coverage["by_source"].append({
                "source_id": sid,
                "source_type": source_types.get(sid, "other"),
                "events_today": source_counts.get(sid, 0),
                "last_seen_date": hist["last_seen_date"],
                "last_seen_count": hist["last_seen_count"],
                "root_hint": "Check fetcher log" if source_counts.get(sid, 0) == 0 else "OK"
            })

        # 4. Global Flags
        if not today_events:
            coverage["global_flags"].append("NO_EVENTS_ALL")
        else:
            for fam in ["S1", "S2", "S3", "S4", "S5"]:
                if coverage["by_gate_family"][fam]["events"] == 0:
                    coverage["global_flags"].append(f"{fam}_EMPTY")
        
        stale_threshold = run_dt - timedelta(days=7)
        has_stale = False
        for s in coverage["by_source"]:
            if s["last_seen_date"]:
                ls_dt = datetime.strptime(s["last_seen_date"], "%Y-%m-%d")
                if ls_dt < stale_threshold:
                    has_stale = True
                    break
        if has_stale:
            coverage["global_flags"].append("SOURCES_STALE")

        coverage["by_source"].sort(key=lambda x: x["source_id"])
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.output_path.write_text(json.dumps(coverage, indent=2, ensure_ascii=False), encoding="utf-8")
        return coverage

if __name__ == "__main__":
    import sys
    base = Path.cwd()
    ymd = sys.argv[1] if len(sys.argv) > 1 else datetime.utcnow().strftime("%Y-%m-%d")
    builder = EventCoverageBuilder(base)
    builder.build(ymd)
    print(f"Coverage report generated: {builder.output_path}")
