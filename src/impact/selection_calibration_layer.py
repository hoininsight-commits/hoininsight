import json

def calibrate_selection(impact_chain):
    """
    [STEP-H-3] Selection Calibration Layer (Upgraded)
    Filters the Impact Chain to the Top 3 stocks using 'selection_score' with solver-first priority.
    """
    if not impact_chain:
        return []

    # 1. Calculate selection_score for each stock
    for stock in impact_chain:
        directness = stock.get("directness", "indirect")
        
        # New priority-weighted directness
        if directness == "solver_direct":
            direct_weight = 1.0
        elif directness == "user_direct":
            direct_weight = 0.8
        elif directness == "direct":
            direct_weight = 0.7
        else:
            direct_weight = 0.3
            
        # evidence weight: 0.1 per evidence_basis node
        evidence_basis = stock.get("evidence_basis", [])
        evidence_weight = len(evidence_basis) * 0.1
        
        stock["selection_score"] = round(direct_weight + evidence_weight, 2)

    # 2. Sort and filter to Top 3
    impact_chain = sorted(
        impact_chain,
        key=lambda x: x.get("selection_score", 0),
        reverse=True
    )[:3]

    return impact_chain

def calibrate_allocation(impact_chain, confidence):
    """
    [STEP-H-CORE] Allocation Calibration Layer
    Directly maps 'confidence.value' and 'selection_score' to stock 'weight'.
    """
    if not impact_chain:
        return []

    # Handle structured confidence or legacy float/int
    base_conf = 0.5
    if isinstance(confidence, dict):
        val = confidence.get("value", 0.5)
        if isinstance(val, dict):
            base_conf = float(val.get("value", 0.5))
        else:
            base_conf = float(val)
    elif isinstance(confidence, (int, float)):
        base_conf = float(confidence)

    for stock in impact_chain:
        # Ensure score is float
        score = float(stock.get("selection_score", 1.0))
        # Direct weight reflects conviction + relevance
        stock["weight"] = round(base_conf * score, 2)

    return impact_chain
