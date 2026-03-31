import json
import os
from pathlib import Path
from datetime import datetime

def build_operator_view(project_root: Path):
    """
    STEP-L: Operator Cognitive Layer v1.0
    Transforms technical engine brief into a human-centric UI contract.
    """
    brief_path = project_root / "docs" / "data" / "ops" / "today_operator_brief.json"
    ui_out_path = project_root / "docs" / "data" / "ui" / "ui_operator_view.json"
    
    # Load SSOT
    if not brief_path.exists():
        print(f"[STEP-L] ⚠️ SSOT missing at {brief_path}. Creating fallback/sample.")
        # Ensure directory exists
        brief_path.parent.mkdir(parents=True, exist_ok=True)
        sample_brief = {
            "core_theme": "AI 전력 인프라 병목과 구조적 기회",
            "causality": {
                "summary": "AI 데이터센터 급증으로 인한 전력 공급 부족이 반도체 생산 및 운영의 핵심 병목으로 부상하며 인프라 수요 폭증"
            },
            "decision": {
                "action": "ADD",
                "timing": "NOW",
                "confidence": {"value": 0.88},
                "risk": "MEDIUM",
                "allocation": 0.25
            },
            "impact": {
                "top_stocks": [
                    {"name": "VRT", "reason": "AI 데이터센터용 냉각 및 전력 관리 글로벌 1위 인프라 제공"},
                    {"name": "VST", "reason": "탄소중립 시대 원자력 기반의 안정적인 전력 생산 핵심 주체"},
                    {"name": "MSFT", "reason": "AI 수요 폭증의 직접적인 수혜자이자 전력 인프라 대규모 선제 투자"}
                ]
            }
        }
        brief_path.write_text(json.dumps(sample_brief, indent=2, ensure_ascii=False), encoding="utf-8")
        brief = sample_brief
    else:
        brief = json.loads(brief_path.read_text(encoding="utf-8"))

    # Load History (Placeholder or from existing logs)
    history = []
    history_path = project_root / "data" / "ops" / "ps_history.json"
    if history_path.exists():
        try:
            raw_history = json.loads(history_path.read_text(encoding="utf-8"))
            # Take last 7 days from history and map to simple format
            for h in raw_history[:7]:
                history.append({
                    "date": h.get("date", "N/A"),
                    "topic": h.get("core_theme", h.get("title", "N/A")),
                    "result": h.get("decision", {}).get("action", "HOLD")
                })
        except:
            pass

    # Load Active Topics (Placeholder or from existing logs)
    active_topics = []
    active_path = project_root / "data" / "ops" / "issuesignal_today.json"
    if active_path.exists():
        try:
            raw_active = json.loads(active_path.read_text(encoding="utf-8"))
            for card in raw_active.get("cards", []):
                active_topics.append(card.get("title", "N/A"))
        except:
            pass

    # Build UI Contract
    ui_data = {
        "today_topic": brief.get("core_theme", "N/A"),
        "why_now": brief.get("causality", {}).get("summary", "N/A"),
        "action": brief.get("decision", {}).get("action", "N/A"),
        "timing": brief.get("decision", {}).get("timing", "N/A"),
        "confidence": brief.get("decision", {}).get("confidence", {}).get("value", 0),
        "risk": brief.get("decision", {}).get("risk", "N/A"),
        "allocation": brief.get("decision", {}).get("allocation", 0),
        "top_stocks": brief.get("impact", {}).get("top_stocks", []),
        "history": history,
        "active_topics": active_topics,
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Save UI Contract
    ui_out_path.parent.mkdir(parents=True, exist_ok=True)
    ui_out_path.write_text(json.dumps(ui_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[STEP-L] ✅ UI View contract generated at {ui_out_path}")
    return ui_data

if __name__ == "__main__":
    # For testing standalone
    root = Path(__file__).parent.parent.parent
    build_operator_view(root)
