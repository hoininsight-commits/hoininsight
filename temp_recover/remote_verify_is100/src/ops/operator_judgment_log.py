import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any

# Configure logger just for this module if needed, or rely on root.
# For now, we print to stderr in engine, so logging.error is fine or print.
logger = logging.getLogger(__name__)

def load_final_decision_card(base_dir: Path, target_ymd: str) -> Optional[Dict[str, Any]]:
    """
    Load the final_decision_card.json for the given date.
    path: data/decision/YYYY/MM/DD/final_decision_card.json
    """
    try:
        y, m, d = target_ymd.split("-")
        card_path = base_dir / "data" / "decision" / y / m / d / "final_decision_card.json"
        
        if card_path.exists():
            content = card_path.read_text(encoding="utf-8")
            return json.loads(content)
        return None
    except Exception as e:
        logger.warning(f"Failed to load final_decision_card for {target_ymd}: {e}")
        return None

def build_operator_log_entry(final_card: Optional[Dict[str, Any]], now_dt: datetime) -> Dict[str, Any]:
    """
    Build the log entry dictionary based on the final decision card and defaults.
    """
    # Defaults
    entry = {
        "date": now_dt.strftime("%Y-%m-%d"),
        "time": now_dt.strftime("%H:%M"),
        "engine_state": "STEP_96_LOCKED",
        "topic_id": "NO_TOPIC",
        "engine_decision": "NO_TOPIC",
        "why_now_summary": "",
        "operator_action": "HOLD",  # Default safety
        "operator_comment": "",
        "continuity_flag": True
    }

    if final_card:
        # Extract fields from final_decision_card
        # Structure varies, but usually has title, decision, etc.
        # We try to infer best map.
        
        # 1. Topic ID
        # Sometimes in 'topic' dict or top level
        t_id = final_card.get("topic_id") 
        if not t_id and "topic" in final_card:
            t_id = final_card["topic"].get("id") or final_card["topic"].get("topic_id")
        
        if t_id:
            entry["topic_id"] = t_id

        # 2. Engine Decision
        # If we have a card, usually it implies a decision was made.
        # We check specific fields like "decision_type" or "status"
        # Since this is "Final Decision Card", if it exists, topic was at least proposed.
        # Logic:
        # If "is_locked": true -> LOCK
        # Else -> PASS (Topic exists but not locked)
        
        is_locked = final_card.get("is_locked", False)
        # Check inside 'decision' object if present
        if "decision" in final_card and isinstance(final_card["decision"], dict):
             is_locked = final_card["decision"].get("is_locked", is_locked)
        
        if is_locked:
            entry["engine_decision"] = "LOCK"
        elif t_id:
             entry["engine_decision"] = "PASS" # Topic present, not locked
        else:
             entry["engine_decision"] = "NO_TOPIC" # Card exists but maybe empty?

        # 3. Why Now Summary
        # Look for "why_now", "rationale", "summary"
        summary = final_card.get("why_now_rationale") or final_card.get("rationale") or final_card.get("summary")
        if not summary and "topic" in final_card:
            summary = final_card["topic"].get("why_now")
        
        entry["why_now_summary"] = str(summary)[:200] if summary else "" # Cap length slightly

    return entry

def append_log(entry: Dict[str, Any], base_dir: Path) -> Path:
    """
    Append the entry to data/judgment_logs/YYYY/MM/DD/operator_judgment_log.jsonl
    """
    y, m, d = entry["date"].split("-")
    log_dir = base_dir / "data" / "judgment_logs" / y / m / d
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_path = log_dir / "operator_judgment_log.jsonl"
    
    # Append mode
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        
    return log_path

def run_step97_operator_judgment_log(base_dir: Path = Path(".")) -> Dict[str, Any]:
    """
    Main entry point for Step 97.
    """
    try:
        from src.utils.target_date import get_target_ymd
        run_ymd = get_target_ymd()
    except ImportError:
         run_ymd = datetime.now().strftime("%Y-%m-%d")

    # Use current system time for the log entry time
    now_dt = datetime.now()
    
    # Load inputs
    final_card = load_final_decision_card(base_dir, run_ymd)
    
    # Build entry
    entry = build_operator_log_entry(final_card, now_dt)
    
    # Write
    log_path = append_log(entry, base_dir)
    
    return {
        "status": "success",
        "entry": entry,
        "path": str(log_path)
    }
