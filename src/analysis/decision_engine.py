import math

class DecisionEngine:
    @staticmethod
    def evaluate(signal: dict) -> dict:
        """확률을 구조적으로 계산하여 결정 (v2.1)"""
        
        # 1. Score 산출 (v2.1)
        
        # A. Flow Score
        flow_dir = signal.get("flow_direction", "outflow")
        flow_conf = signal.get("flow_confirmation", False)
        if flow_dir == "inflow" and flow_conf:
            flow_score = 1.0 # strong
        elif flow_dir == "inflow":
            flow_score = 0.5 # weak
        else:
            flow_score = -1.0 # outflow
            
        # B. Price Score
        price_strength = signal.get("price_strength", "sideways")
        price_mapping = {
            "strong_up": 1.0, "weak_up": 0.5, "sideways": 0.0,
            "weak_down": -0.5, "strong_down": -1.0
        }
        price_score = price_mapping.get(price_strength, 0.0)
        
        # C. Event Score
        trigger = signal.get("trigger_event", "none")
        if trigger != "none":
            event_score = 1.0 # 실적/정책 확정 프록시
        else:
            event_score = 0.0
            
        # D. Consistency Score
        consistency_val = signal.get("flow_consistency", 0)
        if consistency_val >= 2: consistency_score = 1.0
        elif consistency_val <= -2: consistency_score = -1.0
        else: consistency_score = 0.0
        
        # 2. Weighted Sum (P)
        p_val = (0.35 * flow_score) + (0.25 * price_score) + (0.25 * event_score) + (0.15 * consistency_score)
        
        # 3. Bull Probability (Sigmoid 활용 - 민감도 보정을 위해 x3 적용)
        # P_Value가 1.0일 때 약 95% 확률이 나오도록 조정
        bull_prob = 1 / (1 + math.exp(-p_val * 3.0))
        bear_prob = 1 - bull_prob
        
        # 4. Confidence
        confidence = abs(bull_prob - 0.5) * 2
        
        # 5. Action 결정 (v2.1)
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
            "scores": {
                "flow": flow_score,
                "price": price_score,
                "event": event_score,
                "consistency": consistency_score
            },
            "decision_hint": f"P_Value {p_val:.2f} / Confidence {confidence:.2f} 기반 수치 결정"
        }
