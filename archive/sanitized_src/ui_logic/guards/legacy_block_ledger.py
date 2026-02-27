import json
import os
from datetime import datetime
from pathlib import Path
from src.ui_logic.guards.warning_mode import get_hard_mode

LEDGER_PATH = "data_outputs/ops/legacy_block_ledger.json"

def log_gate_decision(module_name: str, caller: str, allowed: bool, reason: str):
    """Records a gate decision to the ledger."""
    project_root = Path(os.getcwd())
    data_path = project_root / LEDGER_PATH
    data_path.parent.mkdir(parents=True, exist_ok=True)

    ledger = {"date": datetime.now().strftime("%Y-%m-%d"), "hard_mode": get_hard_mode(), "blocked": [], "allowed": []}
    
    if data_path.exists():
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                ledger = json.load(f)
        except Exception:
            pass

    entry = {
        "module": module_name,
        "caller": caller or "unknown",
        "reason": reason,
        "ts": datetime.now().isoformat()
    }

    if allowed:
        ledger["allowed"].append(entry)
        if len(ledger["allowed"]) > 100: ledger["allowed"].pop(0)
    else:
        ledger["blocked"].append(entry)
        if len(ledger["blocked"]) > 100: ledger["blocked"].pop(0)

    ledger["hard_mode"] = get_hard_mode()

    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(ledger, f, indent=2, ensure_ascii=False)
