from typing import Any, Dict

def select_content_preset(regime_text: str, confidence: str, has_meta_topic: bool = False) -> Dict[str, str]:
    """
    Selects the Content Preset (BRIEF/STANDARD/DEEP) based on Confidence and Regime.
    
    Rules:
    1) Confidence=HIGH
       - Default: STANDARD
       - Upgrade to DEEP if Regime contains Risk/Crisis keywords.
    2) Confidence=MEDIUM
       - Default: BRIEF
       - Upgrade to STANDARD if Regime contains Structural Shift keywords AND Meta Topic exists.
    3) Confidence=LOW
       - (Usually SKIP, but if called returns BRIEF or SKIP) -> Returns BRIEF (safe fallback)
       
    Returns:
       dict: {"preset": "...", "reason": "..."}
    """
    regime_upper = regime_text.upper()
    
    # 1. Keywords
    joined_risk_keywords = ["RISK-OFF", "CRISIS", "STRESS", "LIQUIDITY", "RECESSION", "VOLATILITY"]
    joined_struct_keywords = ["ROTATION", "DISINFLATION", "SOFT LANDING", "POLICY SHIFT"]
    
    # Check matches
    is_risk = any(k in regime_upper for k in joined_risk_keywords)
    is_struct = any(k in regime_upper for k in joined_struct_keywords)
    
    preset = "STANDARD" # Default fallback
    reason = "Default"
    
    if confidence == "HIGH":
        if is_risk:
            preset = "DEEP"
            reason = "HIGH Confidence + Risk/Crisis Regime detected"
        else:
            preset = "STANDARD"
            reason = "HIGH Confidence (Risk factors not dominant)"
            
    elif confidence == "MEDIUM":
        if is_struct and has_meta_topic:
            preset = "STANDARD"
            reason = "MEDIUM Confidence + Structural Shift with Meta Topic"
        else:
            preset = "BRIEF"
            reason = "MEDIUM Confidence (Default)"
            
    elif confidence == "LOW":
        preset = "BRIEF" # Should be skipped by Gate, but fallback
        reason = "LOW Confidence (Fallback)"
        
    return {
        "preset": preset,
        "reason": reason
    }
