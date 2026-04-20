# src/decision/weight_adjuster.py
import json
from pathlib import Path

# 기본 가중치
DEFAULT_WEIGHTS = {
    "flow": 0.35,
    "price": 0.25,
    "event": 0.25,
    "consistency": 0.15
}

STATE_FILE = Path("data/validation/decision_state.json")

def load_weights():
    if STATE_FILE.exists():
        try:
            state = json.loads(STATE_FILE.read_text())
            return state.get("weights", DEFAULT_WEIGHTS)
        except:
            pass
    return DEFAULT_WEIGHTS

def save_weights(weights):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    state = {}
    if STATE_FILE.exists():
        try:
            state = json.loads(STATE_FILE.read_text())
        except:
            pass
    state["weights"] = weights
    STATE_FILE.write_text(json.dumps(state, indent=2))

def adjust_weights(history):
    """
    최근 10개 기록을 바탕으로 가중치 조정
    - 실패 원인이 FLOW_MISREAD면 flow 가중치 감소 (-0.02)
    - 성공 시 해당 가중치 소폭 증가 (+0.01)
    """
    weights = load_weights().copy()
    
    # 최근 10개만 추출
    recent_history = history[-10:]
    
    for record in recent_history:
        if record["result"] == "FAIL":
            f_type = record.get("failure_type")
            if f_type == "FLOW_MISREAD":
                weights["flow"] = max(0.1, weights["flow"] - 0.02)
            elif f_type == "OVERCONFIDENCE":
                # 자신감이 넘쳐서 틀린 경우 모든 가중치를 조금씩 깎고 base를 강화
                for k in weights:
                    weights[k] *= 0.95
        elif record["result"] == "SUCCESS":
            # 성공 시 flow 가중치 우선 강화 (핵심 엔진)
            weights["flow"] = min(0.5, weights["flow"] + 0.005)

    # 가중치 합이 1이 되도록 정규화
    total = sum(weights.values())
    for k in weights:
        weights[k] = round(weights[k] / total, 3)
        
    save_weights(weights)
    return weights
