import json
import os
import traceback
from datetime import datetime
from pathlib import Path
from src.ui_logic.guards.warning_mode import get_warn_mode, get_hard_mode
from src.ui_logic.guards.legacy_hard_gate import is_allowed
from src.ui_logic.guards.legacy_block_ledger import log_gate_decision

USAGE_DATA_PATH = "data_outputs/ops/legacy_usage.json"

def hit_legacy(module_name: str):
    """
    Records a hit to a legacy module.
    Warns or fails based on configuration.
    """
    # 1. Gate Intelligence (REF-008)
    allowed, gate_reason = is_allowed(module_name)
    
    # 2. Trace caller
    stack = traceback.format_stack()
    caller = "unknown"
    if len(stack) > 3:
        caller = stack[-3].strip().split('\n')[0]

    # 3. Log Decision
    log_gate_decision(module_name, caller, allowed, gate_reason)

    # 4. Enforce Hard Mode if not allowed
    if get_hard_mode() and not allowed:
        raise RuntimeError(f"[REF-008][CRITICAL] Legacy access blocked: {module_name} (Reason: {gate_reason})")
    
    if not get_warn_mode():
        return

    print(f"\n[⚠️  LEGACY WARNING] Module '{module_name}' is deprecated. Please migrate to src.ui_logic.")

    # Record usage
    project_root = Path(os.getcwd())
    data_path = project_root / USAGE_DATA_PATH
    data_path.parent.mkdir(parents=True, exist_ok=True)

    usage = {"date": datetime.now().strftime("%Y-%m-%d"), "total_hits": 0, "modules": {}, "top_callers": []}
    
    if data_path.exists():
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                usage = json.load(f)
        except Exception:
            pass

    usage["total_hits"] += 1
    usage["modules"][module_name] = usage["modules"].get(module_name, 0) + 1
    
    if caller not in usage["top_callers"]:
        usage["top_callers"].append(caller)
        if len(usage["top_callers"]) > 10:
            usage["top_callers"].pop(0)

    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(usage, f, indent=2, ensure_ascii=False)
