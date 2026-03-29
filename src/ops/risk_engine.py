import json
from pathlib import Path
from datetime import datetime
from src.ops.risk_helpers import generate_invalidation

class RiskEngine:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.risk_path = self.project_root / "data" / "operator" / "risk_state.json"
        
    def _load(self, path):
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def build_risk(self):
        print("[RiskEngine] Calculating risk state...")
        
        core = self._load(self.project_root / "data" / "operator" / "core_theme_state.json")
        momentum = self._load(self.project_root / "data" / "theme" / "top_theme_momentum.json")
        evolution = self._load(self.project_root / "data" / "theme" / "top_theme_evolution.json")
        
        if not core or not momentum or not evolution:
            print("⚠️ Missing input data for risk engine.")
            return None
            
        risk_score = 0.2  # Base risk
        
        # Momentum Deceleration
        m_state = momentum.get("state", "STABLE")
        if m_state == "DECELERATING":
            risk_score += 0.4
            
        # Late Stage Evolution
        e_stage = evolution.get("stage", "UNKNOWN")
        if e_stage in ["PEAK", "EXHAUSTION"]:
            risk_score += 0.4
            
        risk_level = "LOW"
        if risk_score >= 0.7:
            risk_level = "HIGH"
        elif risk_score >= 0.4:
            risk_level = "MEDIUM"
            
        risk_state = {
            "theme": core.get("core_theme"),
            "risk_score": round(risk_score, 2),
            "risk_level": risk_level,
            "risk_reason": f"Accumulated score from momentum ({m_state}) and evolution ({e_stage}).",
            "risk_evidence": [f"momentum_state={m_state}", f"evolution_stage={e_stage}"],
            "invalidation": generate_invalidation(core.get("core_theme", "")),
            "stop_signal": m_state,
            "metadata": {
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "engine": "RiskEngine-v1.1"
            }
        }
        
        with open(self.risk_path, "w", encoding="utf-8") as f:
            json.dump(risk_state, f, indent=2, ensure_ascii=False)
            
        print(f"[RiskEngine] Risk Level: {risk_level} (Score: {risk_score})")
        return risk_state

if __name__ == "__main__":
    # Test run
    root = Path(__file__).resolve().parent.parent.parent
    engine = RiskEngine(root)
    engine.build_risk()
