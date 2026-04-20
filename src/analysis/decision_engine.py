import math
from pathlib import Path

class DecisionEngine:
    @staticmethod
    def evaluate(signal: dict, base_dir: Path = None) -> dict:
        """확률을 구조적으로 계산하여 결정 (v3.0 Truth Engine 연동)"""
        
        # 0. Truth Engine 파라미터 로드
        weights = {"flow": 0.35, "price": 0.25, "event": 0.25, "consistency": 0.15}
        cf = 1.0
        if base_dir:
            try:
                from src.analysis.truth_engine import TruthEngine
                te = TruthEngine(base_dir)
                params = te.get_calibrated_params()
                weights = params["weights"]
                cf = params["calibration_factor"]
            except: pass

        # 1. Score 산출 (v2.1 구조 유지)
        
        # A. Flow Score
        flow_dir = signal.get("flow_direction", "outflow")
        flow_conf = signal.get("flow_confirmation", False)
        if flow_dir == "inflow" and flow_conf:
            flow_score = 1.0
        elif flow_dir == "inflow":
            flow_score = 0.5
        else:
            flow_score = -1.0
            
        # B. Price Score
        price_strength = signal.get("price_strength", "sideways")
        price_mapping = {
            "strong_up": 1.0, "weak_up": 0.5, "sideways": 0.0,
            "weak_down": -0.5, "strong_down": -1.0
        }
        price_score = price_mapping.get(price_strength, 0.0)
        
        # C. Event Score
        trigger = signal.get("trigger_event", "none")
        event_score = 1.0 if trigger != "none" else 0.0
            
        # D. Consistency Score
        consistency_val = signal.get("flow_consistency", 0)
        if consistency_val >= 2: consistency_score = 1.0
        elif consistency_val <= -2: consistency_score = -1.0
        else: consistency_score = 0.0
        
        # 2. Weighted Sum (P) - 보정된 가중치 적용
        p_val = (weights["flow"] * flow_score) + \
                (weights["price"] * price_score) + \
                (weights["event"] * event_score) + \
                (weights["consistency"] * consistency_score)
        
        # 3. Bull Probability (Sigmoid 활용 - x3 민감도)
        bull_prob = 1 / (1 + math.exp(-p_val * 3.0))
        bear_prob = 1 - bull_prob
        
        # 4. Confidence (Calibration 계수 적용)
        confidence = abs(bull_prob - 0.5) * 2 * cf
        
        # 5. Action 결정 (v2.1 로직 강화)
        best_scenario = "BULL" if bull_prob > 0.5 else "BEAR"
        
        if confidence > 0.7:
            action = "BUY" if best_scenario == "BULL" else "WATCH"
        elif confidence > 0.5:
            action = "WATCH"
        else:
            action = "HOLD"

        return {
            "action": action,
            "confidence": round(confidence, 2),
            "best_scenario": best_scenario,
            "bull_probability": round(bull_prob, 2),
            "bear_probability": round(bear_prob, 2),
            "weights_used": weights,
            "calibration_applied": cf,
            "decision_hint": f"P_Val {p_val:.2f} / Conf {confidence:.2f} (CF: {cf})"
        }
