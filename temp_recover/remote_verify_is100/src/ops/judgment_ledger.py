import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

def load_last_operator_judgment(base_dir: Path, target_ymd: str) -> Optional[Dict[str, Any]]:
    """
    Load the latest entry from data/judgment_logs/YYYY/MM/DD/operator_judgment_log.jsonl
    Returns the last line parsed as dict, or None.
    """
    y, m, d = target_ymd.split("-")
    log_path = base_dir / "data" / "judgment_logs" / y / m / d / "operator_judgment_log.jsonl"
    
    if not log_path.exists():
        return None
        
    try:
        lines = log_path.read_text(encoding="utf-8").strip().split("\n")
        if lines:
            last_line = lines[-1]
            return json.loads(last_line)
    except Exception as e:
        logger.warning(f"Failed to load operator log: {e}")
    
    return None

def classify_judgment(op_entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Derive ledger_tag and ledger_reason based on operator entry.
    """
    engine_dec = op_entry.get("engine_decision", "NO_TOPIC")
    op_act = op_entry.get("operator_action", "HOLD")
    
    # Defaults
    tag = "INSUFFICIENT_PRESSURE"
    reason = "Held due to insufficient confirmation pressure."
    
    # Rules
    if engine_dec == "NO_TOPIC":
        tag = "NO_TOPIC_VALID_STATE"
        reason = "No topic is a valid state today."
    elif op_act == "REJECT":
        tag = "HUMAN_CONFIDENCE_DROP"
        reason = "Rejected by operator due to low confidence."
    elif op_act == "HOLD":
        if engine_dec != "NO_TOPIC":
            tag = "INSUFFICIENT_PRESSURE"
            reason = "Held due to insufficient confirmation pressure."
    
    return {
        "ledger_tag": tag,
        "ledger_reason": reason
    }

def append_ledger_entry(entry: Dict[str, Any], base_dir: Path) -> Path:
    y, m, d = entry["date"].split("-")
    ledger_dir = base_dir / "data" / "judgment_ledger" / y / m / d
    ledger_dir.mkdir(parents=True, exist_ok=True)
    
    out_path = ledger_dir / "judgment_ledger.jsonl"
    
    with open(out_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        
    return out_path

def run_step98_judgment_ledger(base_dir: Path = Path(".")) -> Dict[str, Any]:
    try:
        from src.utils.target_date import get_target_ymd
        run_ymd = get_target_ymd()
    except ImportError:
        run_ymd = datetime.now().strftime("%Y-%m-%d")

    # 1. Load Step 97 input
    op_entry = load_last_operator_judgment(base_dir, run_ymd)
    
    if not op_entry:
        logger.warning("Step 98: No Step 97 log found. Skipping ledger write.")
        # We return success so pipeline doesn't crash, but status=skipped
        return {"status": "skipped", "reason": "no_step97_log"}

    # 2. Classify
    classification = classify_judgment(op_entry)
    
    # 3. Build Entry
    now_dt = datetime.now()
    ledger_entry = {
        "date": op_entry.get("date", run_ymd),  # Keep alignment with op log date
        "time": now_dt.strftime("%H:%M"),       # Current local time of processing
        "engine_state": "STEP_96_LOCKED",
        "topic_id": op_entry.get("topic_id", "NO_TOPIC"),
        "engine_decision": op_entry.get("engine_decision", "NO_TOPIC"),
        "operator_action": op_entry.get("operator_action", "HOLD"),
        "ledger_tag": classification["ledger_tag"],
        "ledger_reason": classification["ledger_reason"],
        "evidence_refs": [],
        "continuity_flag": True
    }
    
    # Add evidence ref if possible
    y, m, d = ledger_entry["date"].split("-")
    decision_path = base_dir / "data" / "decision" / y / m / d / "final_decision_card.json"
    if decision_path.exists():
        ledger_entry["evidence_refs"].append(str(decision_path))

    # 4. Write
    out_path = append_ledger_entry(ledger_entry, base_dir)
    
    return {
        "status": "success",
        "entry": ledger_entry,
        "path": str(out_path)
    }
