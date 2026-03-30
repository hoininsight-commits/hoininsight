import json

def calibrate_selection(impact_chain, project_root=None):
    """
    [STEP-H-3] Selection Calibration Layer (Upgraded)
    Filters the Impact Chain to the Top 3 stocks using 'selection_score' with solver-first priority.
    """
    if not impact_chain:
        return []

    # Load dynamic params
    solver_weight = 1.0
    demand_weight = 0.7
    if project_root:
        from pathlib import Path
        param_path = Path(project_root) / "data" / "ops" / "engine_parameters.json"
        if param_path.exists():
            try:
                with open(param_path, "r", encoding="utf-8") as f:
                    params = json.load(f).get("SelectionCalibrationLayer", {})
                    solver_weight = params.get("solver_weight", 1.0)
                    demand_weight = params.get("demand_weight", 0.7)
            except: pass

    # 1. Calculate selection_score for each stock
    for stock in impact_chain:
        directness = stock.get("directness", "indirect")
        
        # New priority-weighted directness
        if directness == "solver_direct":
            direct_weight = solver_weight
        elif directness == "user_direct":
            direct_weight = 0.8
        elif directness == "direct":
            direct_weight = demand_weight
        else:
            direct_weight = 0.3
            
        # evidence weight: 0.1 per evidence_basis node
        evidence_basis = stock.get("evidence_basis", [])
        evidence_weight = len(evidence_basis) * 0.1
        
        stock["selection_score"] = round(direct_weight + evidence_weight, 2)

    # 2. Sort and filter to Top 3
    # Composite Sort: 1) Directness Order (0=solver_direct, 1=direct, 2=indirect) 2) selection_score (descending)
    order_map = {
        "solver_direct": 0,
        "direct": 1,
        "user_direct": 1, # Treat user_direct with same priority as direct for order
        "indirect": 2
    }
    
    impact_chain = sorted(
        impact_chain,
        key=lambda x: (order_map.get(x.get("directness"), 9), -x.get("selection_score", 0))
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
