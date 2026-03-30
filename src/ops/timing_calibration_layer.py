import json

def calibrate_timing(decision, context):
    """
    [STEP-H-CORE] Timing Calibration Layer
    Couples 'stage' and 'momentum_score' to refine the investment action.
    """
    stage = context.get("stage", "UNKNOWN")
    momentum = context.get("momentum_score", 0.5)

    # Current raw action from engine
    action = decision.get("action", {}).get("value", "WATCH")

    # Calibration Logic based on Rule 3-3
    if stage == "EMERGING":
        if momentum < 0.55:
            action = "WATCH"
        elif 0.55 <= momentum < 0.65:
            action = "PREPARE"
        else:
            action = "ENTER"

    elif stage == "EXPANSION":
        if momentum < 0.5:
            action = "HOLD"
        else:
            action = "ADD"
            
    # Update decision object
    if isinstance(decision.get("action"), dict):
        decision["action"]["value"] = action
        decision["action"]["source"] = "calibrated"
    else:
        decision["action"] = {"value": action, "source": "calibrated"}

    return decision
