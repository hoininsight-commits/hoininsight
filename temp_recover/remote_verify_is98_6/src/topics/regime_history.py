from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

def _ymd_dash() -> str:
    return datetime.now().strftime("%Y-%m-%d")

def _read_json(p: Path) -> Any:
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None

def _write_json(p: Path, data: Any) -> None:
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def update_regime_history(base_dir: Path, current_regime_summ: Dict[str, Any]) -> Dict[str, Any]:
    """
    1. Saves daily snapshot to data/regimes/regime_YYYY-MM-DD.json
    2. Updates data/regimes/regime_history.json (append-only)
    3. Calculates persistence
    """
    today_str = _ymd_dash()
    
    # 1. Save Daily Snapshot
    regime_dir = base_dir / "data" / "regimes"
    regime_dir.mkdir(parents=True, exist_ok=True)
    
    snapshot_path = regime_dir / f"regime_{today_str}.json"
    
    # Construct strictly defined snapshot structure
    # current_regime_summ comes from the card logic (enriched)
    snapshot_data = {
        "date": today_str,
        "regime": current_regime_summ.get("regime", "Unknown"),
        "basis_type": current_regime_summ.get("basis_type", "UNKNOWN"),
        "basis_id": current_regime_summ.get("basis_id", "unknown"),
        "confidence": current_regime_summ.get("confidence", 0.0),
        "supporting_meta_topics": current_regime_summ.get("supporting", []),
        "fallback_driver": current_regime_summ.get("fallback", None)
    }
    _write_json(snapshot_path, snapshot_data)
    
    # 2. Update History
    history_path = regime_dir / "regime_history.json"
    history_data = _read_json(history_path)
    
    if not history_data:
        history_data = {"latest_date": "", "history": []}
    
    # Append current if not already present for today (idempotency check)
    existing_dates = {h["date"] for h in history_data["history"]}
    if today_str not in existing_dates:
        history_data["history"].append({
            "date": today_str,
            "regime": snapshot_data["regime"]
        })
        # Sort by date
        history_data["history"].sort(key=lambda x: x["date"])
        history_data["latest_date"] = today_str
        _write_json(history_path, history_data)
        
    # 3. Calculate Persistence
    # Traverse backwards from today
    # Note: history_data["history"] is sorted by date ascending now
    hist_list = history_data["history"]
    curr_name = snapshot_data["regime"]
    
    # Identify consecutive runs ending at today
    # We iterate backwards
    streak = 0
    start_date = today_str
    
    for entry in reversed(hist_list):
        if entry["regime"] == curr_name:
            streak += 1
            start_date = entry["date"]
        else:
            break
            
    is_new = (streak == 1)
    
    return {
        "current_regime": curr_name,
        "persistence_days": streak,
        "started_at": start_date,
        "is_new_regime": is_new
    }
