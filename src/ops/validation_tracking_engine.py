import json
from pathlib import Path
from datetime import datetime

def build_tracking_entry(run_data, audit_data, confidence_data):
    """
    [STEP-H-TRACK] Build a flat tracking entry for a single run.
    """
    # Extract confidence value safely (supporting both structured and legacy)
    conf_value = confidence_data
    if isinstance(confidence_data, dict):
        conf_value = confidence_data.get("value", 0.5)
        if isinstance(conf_value, dict):
            conf_value = conf_value.get("value", 0.5)
    
    return {
        "date": run_data.get("date", datetime.now().strftime("%Y-%m-%d")),
        "core_theme": run_data.get("core_theme", "Unknown"),
        "action": run_data.get("decision", {}).get("action", {}).get("value", "WATCH"),
        "confidence": round(float(conf_value), 2),
        "hit_ratio": round(float(run_data.get("evaluation", {}).get("hit_ratio", 0.0)), 2),
        "outcome_alignment": round(float(audit_data.get("outcome_alignment", 0.0)), 2),
        "failure_type": run_data.get("evaluation", {}).get("failure_type", "NONE")
    }

def append_tracking(entry, path):
    """
    Append an entry to the tracking JSON file.
    """
    path = Path(path)
    data = []
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"[Tracking] Warning: Failed to load {path}: {e}")
            data = []
            
    # Avoid duplicate for same date/theme if needed, but per-run accumulation is preferred
    data.append(entry)
    
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[Tracking] Entry appended to {path}")
    return data

def build_timeseries(tracking_data):
    """
    Generate a time-series summary from tracking data.
    """
    return {
        "dates": [x["date"] for x in tracking_data],
        "alignment": [x["outcome_alignment"] for x in tracking_data],
        "hit_ratio": [x["hit_ratio"] for x in tracking_data],
        "confidence": [x["confidence"] for x in tracking_data]
    }

def save_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[Tracking] Saved to {path}")

if __name__ == "__main__":
    # Internal test/CLI if needed
    pass
