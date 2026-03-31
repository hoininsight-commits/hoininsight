import json
import os
from pathlib import Path
from datetime import datetime

def build_operator_view(project_root: Path):
    """
    STEP-L: Operator Cognitive Layer v1.0
    Transforms technical engine brief into a human-centric UI contract.
    Updated to handle rich STEP-K-4 structure.
    """
    brief_path = project_root / "docs" / "data" / "ops" / "today_operator_brief.json"
    ui_out_path = project_root / "docs" / "data" / "ui" / "ui_operator_view.json"
    
    # Load SSOT
    if not brief_path.exists():
        print(f"[STEP-L] ⚠️ SSOT missing at {brief_path}.")
        return None
        
    brief = json.loads(brief_path.read_text(encoding="utf-8"))

    # Extract Data from Rich Structure
    ui_today = brief.get("ui_today", {})
    inv_dec = brief.get("investment_decision", {})
    
    today_topic = brief.get("core_theme", ui_today.get("title", "N/A"))
    why_now = ui_today.get("why_now", brief.get("narrative", {}).get("explanation", "시장 상황 분석 완료."))
    
    # Decisions (Nested in investment_decision)
    action = inv_dec.get("action", {}).get("value", ui_today.get("action", "WATCH"))
    timing = inv_dec.get("timing", {}).get("value", "N/A")
    risk = inv_dec.get("risk", {}).get("value", "LOW")
    allocation = inv_dec.get("allocation", {}).get("value", 0)
    
    # Confidence (Nested object in recalibrated versions)
    conf_obj = inv_dec.get("confidence", {})
    if isinstance(conf_obj, dict):
        confidence = conf_obj.get("value", {}).get("final_confidence", ui_today.get("confidence_pct", 0) / 100)
    else:
        confidence = conf_obj / 100 if conf_obj > 1 else conf_obj

    # Stocks (Structural Impact Chain)
    top_stocks_raw = brief.get("impact_map", {}).get("structural_impact_chain", [])
    top_stocks = []
    for s in top_stocks_raw[:3]:
        top_stocks.append({
            "name": s.get("name", s.get("ticker", "N/A")),
            "reason": s.get("impact_reason", s.get("rationale", "핵심 수혜 종목"))
        })

    # Load History (Placeholder or from existing logs)
    history = []
    history_path = project_root / "data" / "ops" / "ps_history.json"
    if history_path.exists():
        try:
            raw_history = json.loads(history_path.read_text(encoding="utf-8"))
            for h in raw_history[:7]:
                history.append({
                    "date": h.get("date", "N/A"),
                    "topic": h.get("core_theme", h.get("title", "N/A")),
                    "result": h.get("decision", {}).get("action", "HOLD")
                })
        except: pass

    # Load Active Topics
    active_topics = []
    active_path = project_root / "data" / "ops" / "issuesignal_today.json"
    if active_path.exists():
        try:
            raw_active = json.loads(active_path.read_text(encoding="utf-8"))
            for card in raw_active.get("cards", []):
                active_topics.append(card.get("title", "N/A"))
        except: pass

    # Build UI Contract
    ui_data = {
        "today_topic": today_topic,
        "why_now": why_now,
        "action": action,
        "timing": timing,
        "confidence": float(confidence),
        "risk": risk,
        "allocation": float(allocation),
        "top_stocks": top_stocks,
        "history": history,
        "active_topics": active_topics,
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Save UI Contract
    ui_out_path.parent.mkdir(parents=True, exist_ok=True)
    ui_out_path.write_text(json.dumps(ui_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[STEP-L] ✅ Final UI View contract generated at {ui_out_path}")
    return ui_data

if __name__ == "__main__":
    root = Path(__file__).parent.parent.parent
    build_operator_view(root)
