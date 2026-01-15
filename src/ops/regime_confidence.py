import json
from pathlib import Path
from typing import Dict, Any
from src.ops.core_dataset import get_core_datasets

def calculate_regime_confidence(status_path: Path) -> Dict[str, Any]:
    """
    Calculates Regime Confidence based on Core Dataset collection status.
    
    Rules:
      - HIGH: All 3 Core Datasets are OK
      - MEDIUM: 2 or more OK (others SKIP/WARMUP)
      - LOW: 1 or fewer OK OR any FAIL status
    """
    core_map = get_core_datasets()
    confidence = "LOW"
    breakdown = {}
    
    if not status_path.exists():
        return {
            "regime_confidence": "LOW",
            "reason": "Status file missing",
            "core_breakdown": {}
        }

    try:
        status_data = json.loads(status_path.read_text(encoding="utf-8"))
    except Exception:
        return {
            "regime_confidence": "LOW",
            "reason": "Status file corrupt",
            "core_breakdown": {}
        }
        
    ok_count = 0
    fail_exists = False
    
    for label, ds_id in core_map.items():
        # Default to FAIL if missing from status
        s_info = status_data.get(ds_id, {"status": "FAIL"})
        st = s_info.get("status", "FAIL")
        
        breakdown[label] = st
        
        if st == "OK":
            ok_count += 1
        elif st == "FAIL":
            fail_exists = True
            
    # Evaluation Logic
    if fail_exists:
        confidence = "LOW"
    elif ok_count == 3:
        confidence = "HIGH"
    elif ok_count >= 2:
        confidence = "MEDIUM"
    else:
        confidence = "LOW" # 0 or 1 OK
        
    return {
        "regime_confidence": confidence,
        "core_breakdown": breakdown
    }
