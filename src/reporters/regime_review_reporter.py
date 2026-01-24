from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

def _ymd_iso() -> str:
    return datetime.utcnow().isoformat()

def _read_json(p: Path) -> Any:
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None

def _write_json(p: Path, data: Any) -> None:
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

@dataclass
class RegimeStat:
    regime: str
    total_occurrences: int
    average_persistence_days: float
    max_persistence_days: int

def generate_regime_retrospective(base_dir: Path) -> Dict[str, Any]:
    history_path = base_dir / "data" / "regimes" / "regime_history.json"
    history_data = _read_json(history_path)
    
    if not history_data or "history" not in history_data:
        # Return empty structure if no history
        return {"generated_at": _ymd_iso(), "summary": []}

    hist_entries = history_data.get("history", [])
    if not hist_entries:
        return {"generated_at": _ymd_iso(), "summary": []}

    # Calculate streaks
    # Format: list of (regime_name, duration)
    streaks: List[Any] = []
    
    current_regime = None
    current_streak = 0
    
    # History is sorted by date ascending
    for entry in hist_entries:
        r_name = entry.get("regime", "Unknown")
        if r_name != current_regime:
            if current_regime is not None:
                streaks.append((current_regime, current_streak))
            current_regime = r_name
            current_streak = 1
        else:
            current_streak += 1
            
    # Append the final ongoing streak
    if current_regime is not None:
        streaks.append((current_regime, current_streak))
        
    # Aggregate stats per regime
    stats_map: Dict[str, Dict[str, Any]] = {} 
    # { "regime_name": {"counts": [], "occurrences": 0} }

    for r_name, duration in streaks:
        if r_name not in stats_map:
            stats_map[r_name] = {"durations": []}
        stats_map[r_name]["durations"].append(duration)

    summary_list = []
    for r_name, data in stats_map.items():
        durations = data["durations"]
        total_occurrences = len(durations)
        max_persistence = max(durations) if durations else 0
        avg_persistence = sum(durations) / total_occurrences if total_occurrences > 0 else 0.0
        
        summary_list.append({
            "regime": r_name,
            "total_occurrences": total_occurrences,
            "average_persistence_days": float(round(avg_persistence, 2)),
            "max_persistence_days": max_persistence
        })
        
    retrospective_payload = {
        "generated_at": _ymd_iso(),
        "summary": summary_list
    }
    
    # Save to file
    out_dir = base_dir / "data" / "regime_reviews"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "regime_retrospective_v1.json"
    _write_json(out_path, retrospective_payload)
    
    return retrospective_payload

def get_historical_context_lines(base_dir: Path, current_regime: str) -> List[str]:
    # Ensure updated stats
    retro_data = generate_regime_retrospective(base_dir)
    summary = retro_data.get("summary", [])
    
    lines = []
    target_stat = next((s for s in summary if s["regime"] == current_regime), None)
    
    if target_stat:
        lines.append("Historical context:")
        lines.append(f"- {current_regime} appeared {target_stat['total_occurrences']} times historically")
        lines.append(f"- Average persistence: {target_stat['average_persistence_days']} days (max {target_stat['max_persistence_days']} days)")
        
    return lines
