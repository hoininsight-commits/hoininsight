import json
from pathlib import Path
from typing import Any, Dict
from src.ops.regime_confidence import calculate_regime_confidence

def evaluate_content_gate(base_dir: Path) -> Dict[str, Any]:
    """
    Evaluates whether content generation (Phase 30) should proceed 
    based on Regime Confidence (Ops Upgrade v1.1).

    Gate Logic:
      - HIGH   -> allow=True,  mode="NORMAL"
      - MEDIUM -> allow=True,  mode="CAUTIOUS"
      - LOW    -> allow=False, mode="SKIP" (reason required)
    """
    status_path = base_dir / "data" / "dashboard" / "collection_status.json"
    
    # Calculate Confidence
    conf_res = calculate_regime_confidence(status_path)
    conf_level = conf_res.get("regime_confidence", "LOW")
    core_bd = conf_res.get("core_breakdown", {})
    
    # Default: LOW/SKIP
    result = {
        "allow_content": False,
        "content_mode": "SKIP",
        "reason": f"Regime Confidence is {conf_level}. Core Dataset status: {core_bd}"
    }

    if conf_level == "HIGH":
        result["allow_content"] = True
        result["content_mode"] = "NORMAL"
        result["reason"] = "Confidence HIGH. All Core Datasets operational."
        
    elif conf_level == "MEDIUM":
        result["allow_content"] = True
        result["content_mode"] = "CAUTIOUS"
        result["reason"] = "Confidence MEDIUM. Some non-critical datasets may be missing."
        
    elif conf_level == "LOW":
        # Explicit logic for LOW
        result["allow_content"] = False
        result["content_mode"] = "SKIP"
        result["reason"] = f"Regime Confidence is LOW. Core Dataset status: {core_bd}"
        
    return result
