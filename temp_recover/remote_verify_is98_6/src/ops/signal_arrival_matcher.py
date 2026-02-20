import json
from pathlib import Path
from typing import Dict, List, Any
from src.ops.signal_watchlist import WATCH_SIGNAL_ENUM

class SignalArrivalMatcher:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def detect_arrivals(self, ymd: str) -> Dict[str, Any]:
        """
        Detects which signals arrived today based on artifact presence.
        """
        ymd_path = ymd.replace("-", "/")
        
        # Define artifact source paths
        sources = {
            WATCH_SIGNAL_ENUM.NUMERIC_EVIDENCE_APPEAR: [
                self.base_dir / "data" / "reports" / ymd_path / "daily_snapshot.json"
            ],
            WATCH_SIGNAL_ENUM.SUPPORTING_ANOMALY_DETECTED: [
                self.base_dir / "data" / "structural" / ymd_path / "anomalies.json" # Hypothetical path
            ],
            WATCH_SIGNAL_ENUM.POLICY_EVENT_TRIGGERED: [
                self.base_dir / "data" / "events" / ymd_path / "events.json"
            ],
            WATCH_SIGNAL_ENUM.EARNINGS_RELEASE: [
                self.base_dir / "data" / "events" / ymd_path / "events.json"
            ],
            WATCH_SIGNAL_ENUM.ONCHAIN_CONFIRMATION: [
                self.base_dir / "data" / "metrics" / ymd_path / "onchain.json" # Hypothetical path
            ],
            WATCH_SIGNAL_ENUM.MACRO_THRESHOLD_CROSSED: [
                self.base_dir / "data" / "reports" / ymd_path / "macro_alerts.json" # Hypothetical path
            ]
        }

        arrived_signals = []
        signal_sources = {}

        for signal, paths in sources.items():
            for p in paths:
                if p.exists():
                    # Special check for EARNINGS_RELEASE inside events.json
                    if signal == WATCH_SIGNAL_ENUM.EARNINGS_RELEASE:
                        try:
                            ev_data = json.loads(p.read_text(encoding="utf-8"))
                            if any("earnings" in str(ev).lower() for ev in ev_data):
                                arrived_signals.append(signal)
                                signal_sources.setdefault(signal, []).append(str(p))
                        except:
                            pass
                    else:
                        if signal not in arrived_signals:
                            arrived_signals.append(signal)
                        signal_sources.setdefault(signal, []).append(str(p))

        return {
            "arrived_signals": list(set(arrived_signals)),
            "signal_sources": signal_sources
        }

    def match_to_shadows(self, shadow_pool: List[Dict[str, Any]], arrived_signals: List[str]) -> List[Dict[str, Any]]:
        """
        Attaches match status to each shadow candidate.
        """
        for c in shadow_pool:
            watch_signals = c.get("watch_signals", [])
            matched = [s for s in watch_signals if s in arrived_signals]
            unmatched = [s for s in watch_signals if s not in arrived_signals]
            
            c["signal_status"] = {
                "matched_signals": matched,
                "unmatched_signals": unmatched
            }
        return shadow_pool
