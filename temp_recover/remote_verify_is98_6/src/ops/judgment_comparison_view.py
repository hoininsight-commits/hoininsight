import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

def load_json_file(path: Path) -> Optional[Dict[str, Any]]:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning(f"Error reading {path}: {e}")
    return None

def load_latest_jsonl_line(path: Path) -> Optional[Dict[str, Any]]:
    if path.exists():
        try:
            lines = path.read_text(encoding="utf-8").strip().split("\n")
            if lines:
                return json.loads(lines[-1])
        except Exception as e:
            logger.warning(f"Error reading log file {path}: {e}")
    return None

def run_step99_judgment_comparison_view(base_dir: Path = Path(".")) -> Dict[str, Any]:
    try:
        from src.utils.target_date import get_target_ymd
        run_ymd = get_target_ymd()
    except ImportError:
        run_ymd = datetime.now().strftime("%Y-%m-%d")

    y, m, d = run_ymd.split("-")
    
    # Paths
    log_path = base_dir / "data" / "judgment_logs" / y / m / d / "operator_judgment_log.jsonl"
    ledger_path = base_dir / "data" / "judgment_ledger" / y / m / d / "judgment_ledger.jsonl"
    card_path = base_dir / "data" / "decision" / y / m / d / "final_decision_card.json"
    
    # Load Inputs
    op_log = load_latest_jsonl_line(log_path)
    ledger = load_latest_jsonl_line(ledger_path)
    final_card = load_json_file(card_path)
    
    source_refs = []
    if op_log: source_refs.append(str(log_path))
    if ledger: source_refs.append(str(ledger_path))
    if final_card: source_refs.append(str(card_path))
    
    # If minimal inputs missing, can't reliably compare, but let's try gracefully
    # If op_log is missing, we can't really do Step 99 properly as we need operator action.
    if not op_log:
         return {"status": "skipped", "reason": "missing_step97_log"}

    # Extract Key Fields
    engine_decision = op_log.get("engine_decision", "NO_TOPIC")
    operator_action = op_log.get("operator_action", "HOLD")
    topic_id = op_log.get("topic_id", "NO_TOPIC")
    
    # Engine Side Details
    # Infer summary/basis from final_decision_card if available
    engine_why_now = op_log.get("why_now_summary", "")
    engine_basis = []
    if final_card:
         # Try to extract structural basis if present
         if "structural_basis" in final_card:
             engine_basis.append(str(final_card["structural_basis"]))
    
    # Human Side Details from Ledger (preferred) or Log
    operator_reason = ""
    operator_tag = "UNKNOWN"
    
    if ledger:
        operator_reason = ledger.get("ledger_reason", "")
        operator_tag = ledger.get("ledger_tag", "UNKNOWN")
    else:
        operator_reason = op_log.get("operator_comment", "")
    
    # Deterministic Mapping
    alignment_status = "DIVERGED"
    divergence_reason = ""
    divergence_type = "NONE"

    # Rules
    if engine_decision == "NO_TOPIC" and operator_action == "HOLD":
        alignment_status = "ALIGNED"
        divergence_type = "NO_TOPIC_ALIGNMENT" 
        # Wait, requirement says: NO_TOPIC_ALIGNMENT is under divergence_type enum? 
        # Prompt says: "divergence_type (one of): ... NO_TOPIC_ALIGNMENT"
        # Prompt also says: "If ALIGNED... divergence_range (empty if ALIGNED...)"
        # But specifically under "Alignment: ... -> divergence_type = NO_TOPIC_ALIGNMENT"
        # This is a bit contradictory. "divergence_reason (empty if ALIGNED)".
        # Let's interpret: divergence_type CAN be set even if ALIGNED to denote they aligned ON "no topic".
        pass

    elif engine_decision == "LOCK" and operator_action == "PROCEED":
        alignment_status = "ALIGNED"
        divergence_type = "NONE"

    else:
        # Diverged
        alignment_status = "DIVERGED"
        if engine_decision == "LOCK" and operator_action != "PROCEED":
             # Tag mapping
             if operator_tag == "HUMAN_CONFIDENCE_DROP":
                 divergence_type = "CONFIDENCE_GAP"
             elif operator_tag == "INSUFFICIENT_PRESSURE":
                 divergence_type = "TIME_MISMATCH"
             elif operator_tag == "NARRATIVE_SATURATION":
                 divergence_type = "NARRATIVE_SATURATION"
             else:
                 divergence_type = "CONFIDENCE_GAP" # Fallback/Default mapping

             divergence_reason = f"Engine locked but Human {operator_action} ({operator_tag})"

        elif engine_decision != "LOCK" and operator_action == "PROCEED":
             divergence_type = "TIME_MISMATCH"
             divergence_reason = "Engine did not lock but Human Proceeded"
    
    # Construct View
    view = {
        "date": run_ymd,
        "engine_state": "STEP_96_LOCKED",
        "topic_id": topic_id,
        "engine_side": {
            "engine_decision": engine_decision,
            "engine_why_now": engine_why_now,
            "engine_basis": engine_basis
        },
        "human_side": {
            "operator_action": operator_action,
            "operator_reason": operator_reason,
            "operator_tag": operator_tag
        },
        "delta_interpretation": {
            "alignment_status": alignment_status,
            "divergence_reason": divergence_reason,
            "divergence_type": divergence_type
        },
        "continuity_flag": True,
        "source_refs": source_refs
    }

    # Write Output
    out_dir = base_dir / "data" / "judgment_comparison" / y / m / d
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "judgment_comparison_view.json"
    
    out_path.write_text(json.dumps(view, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "status": "success",
        "path": str(out_path),
        "view": view
    }
