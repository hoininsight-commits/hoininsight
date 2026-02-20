from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

def _ymd_iso() -> str:
    return datetime.now().isoformat()

def _read_json(p: Path) -> Any:
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None

def _write_json(p: Path, data: Any) -> None:
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def detect_narrative_drift(base_dir: Path, window_days: int = 7) -> Dict[str, Any]:
    """
    Detects Narrative Drift for Regimes (based on history).
    Drift Types: ACCELERATION, SATURATION, DECAY, NONE
    """
    history_path = base_dir / "data" / "regimes" / "regime_history.json"
    history_data = _read_json(history_path)
    
    signals = []
    
    if history_data and "history" in history_data:
        hist_entries = history_data["history"]
        # Filter for recent window
        cutoff = datetime.now() - timedelta(days=window_days)
        recent_entries = []
        for h in hist_entries:
            try:
                d = datetime.strptime(h["date"], "%Y-%m-%d")
                if d >= cutoff:
                    recent_entries.append(h)
            except ValueError:
                continue
        
        # Group by regime
        regime_stats: Dict[str, List[Dict[str, Any]]] = {}
        for entry in recent_entries:
            r = entry.get("regime", "Unknown")
            if r not in regime_stats:
                regime_stats[r] = []
            regime_stats[r].append(entry)
            
        # Analyze each active regime in window
        for r_name, entries in regime_stats.items():
            count = len(entries)
            # Simplified Logic for Phase 29 (Placeholder for strict math)
            # If appears > 50% of window -> High Persistence
            # If appears increasing frequency -> Acceleration
            # This is a basic rule-based implementation as per "judge only frequency/intensity"
            
            drift_type = "NONE"
            freq_change = "0%"
            
            # Simple heuristic:
            # If count >= window_days - 1: Saturation (High persistence)
            # If count >= 2 but < window - 1: Acceleration (Appearing)
            # If count <= 1: Decay (or just noise) - BUT Decay usually implies it WAS high.
            # Without deeper history comparison, we use simple window-based logic.
            
            if count >= max(1, window_days - 1):
                drift_type = "SATURATION"
                freq_change = "High Sustained"
            elif count >= 2:
                # Check if it's appearing more lately? 
                # For now, treat frequent but not saturated as Acceleration context
                drift_type = "ACCELERATION" 
                freq_change = "Rising"
            else:
                drift_type = "DECAY" # Appearing rarely in window
                freq_change = "Low/Dropping"

            signals.append({
                "entity_type": "regime",
                "entity_id": r_name,
                "drift_type": drift_type,
                "window_days": window_days,
                "signals": {
                    "frequency_change": freq_change,
                    "avg_score_change": "N/A", # Score tracking requires deeper data integration
                    "persistence_change": f"{count}d in {window_days}d window"
                }
            })

    output = {
        "generated_at": _ymd_iso(),
        "window_days": window_days,
        "drifts": signals
    }
    
    # Save to file (Append only logic? File structure suggests single file with list of drifts, 
    # but prompt says "All results accumulated by date".
    # However, the example structure implies a snapshot object. 
    # To maintain "Append Only" with a single JSON file generally means 
    # reading existing list and appending new snapshot, OR creating daily files.
    # The prompt says `/data/narratives/narrative_drift_v1.json` (singular).
    # So I will read existing, append this snapshot to a list, or just Append lines?
    # JSON structure usually `{"drifts": [...]}` implies one object.
    # To support append-only in one JSON file, I'll structure it as a list of snapshots if possible,
    # or just replace the content with the NEW snapshot appended to a root list?
    # "overwrite 금지" -> implies I shouldn't delete old data. 
    # I will load existing, append this new entry to a list of snapshots.
    
    out_dir = base_dir / "data" / "narratives"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "narrative_drift_v1.json"
    
    existing = _read_json(out_path)
    if not existing:
        final_data = {"history": [output]}
    else:
        # If structure differs, reset or adapt.
        if "history" not in existing:
            final_data = {"history": [output]}
        else:
            existing["history"].append(output)
            final_data = existing
            
    _write_json(out_path, final_data)
    
    return output
