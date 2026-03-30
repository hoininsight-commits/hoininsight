import json
from pathlib import Path
from datetime import datetime

def map_action_to_parameters(action):
    """Maps high-level calibration actions to specific engine parameters and deltas."""
    mapping = {
        "EXPAND_SOLVER_POOL": {
            "param": "solver_pool_size",
            "delta": 2
        },
        "REWEIGHT_SOLVER_PRIORITY": {
            "param": "solver_weight",
            "delta": 0.1
        },
        "BOOST_DEMAND_SIGNALS": {
            "param": "demand_weight",
            "delta": 0.1
        },
        "ADJUST_TIMING_THRESHOLD": {
            "param": "timing_threshold",
            "delta": -0.05
        }
    }
    return mapping.get(action)

def is_approved(action_item, approval_state):
    """Checks if a proposed action has been explicitly approved by the operator."""
    approved_list = approval_state.get("approved", [])
    for app in approved_list:
        if app.get("action") == action_item.get("action") and \
           app.get("target") == action_item.get("target") and \
           app.get("approved") is True:
            return True
    return False

def update_engine_param(project_root, target, param, delta):
    """Loads, updates, and saves engine parameters in the central config."""
    param_path = project_root / "data" / "ops" / "engine_parameters.json"
    
    if not param_path.exists():
        params = {}
    else:
        with open(param_path, "r", encoding="utf-8") as f:
            params = json.load(f)

    if target not in params:
        params[target] = {}

    # Load current or default
    current_value = params[target].get(param, 0)
    
    # Apply delta
    new_value = round(current_value + delta, 2)
    
    params[target][param] = new_value
    
    with open(param_path, "w", encoding="utf-8") as f:
        json.dump(params, f, indent=2, ensure_ascii=False)

    return {
        "before": current_value,
        "after": new_value
    }

def apply_calibration(project_root, plan, approval):
    """Main entry point to execute approved calibration proposals."""
    applied = []
    
    # proposals is a dict sorted by context (CONSTRAINT, EXPANSION)
    proposals = plan.get("proposals", {})
    if not proposals:
        # Fallback for older plan structures if any
        proposals = plan.get("plans", {})

    for ctx, actions in proposals.items():
        for act in actions:
            if not is_approved(act, approval):
                # print(f"[Calibration] ⏩ Skipping unapproved action: {act['action']} for {act['target']}")
                continue

            mapping = map_action_to_parameters(act["action"])
            if not mapping:
                print(f"[Calibration] ⚠️ No parameter mapping found for action: {act['action']}")
                continue

            print(f"[Calibration] ✅ Applying action: {act['action']} ({mapping['param']} +{mapping['delta']})")
            
            result = update_engine_param(
                project_root=project_root,
                target=act["target"],
                param=mapping["param"],
                delta=mapping["delta"]
            )

            applied.append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "context": ctx,
                "action": act["action"],
                "target": act["target"],
                "param": mapping["param"],
                "delta": mapping["delta"],
                "before": result["before"],
                "after": result["after"],
                "status": "APPLIED"
            })

    return applied
