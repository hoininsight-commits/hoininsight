import os
import json
from pathlib import Path
from datetime import datetime

class NarrativeMomentumEngine:
    """
    Engine to analyze the speed and acceleration of market themes.
    Classifies momentum into: ACCELERATING, BUILDING, STABLE, COOLING, COLLAPSING.
    """
    
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.evolution_state_path = self.project_root / "data" / "theme" / "theme_evolution_state.json"
        self.early_theme_path = self.project_root / "data" / "theme" / "top_early_theme.json"
        self.signal_path = self.project_root / "data" / "ops" / "hoin_signal_today.json"
        self.flow_path = self.project_root / "data" / "ops" / "capital_flow_impact.json"
        self.top_topic_path = self.project_root / "data" / "topic" / "top_topic.json"
        
        self.output_dir = self.project_root / "data" / "theme"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _load_json(self, path):
        if not path.exists():
            return None
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None

    def _get_momentum_state(self, score):
        if score >= 0.40: return "ACCELERATING"
        if score >= 0.10: return "BUILDING"
        if score >= -0.09: return "STABLE"
        if score >= -0.39: return "COOLING"
        return "COLLAPSING"

    def _get_action_hint(self, state):
        hints = {
            "ACCELERATING": "CONTENT PRIORITY / HIGH ALERT",
            "BUILDING": "GRADUAL COVERAGE / MONITOR",
            "STABLE": "MAINTAIN EXPOSURE",
            "COOLING": "REDUCE FREQUENCY",
            "COLLAPSING": "EXIT NARRATIVE / ARCHIVE"
        }
        return hints.get(state, "OBSERVE")

    def run_momentum_analysis(self):
        print("[NarrativeMomentumEngine] Starting Momentum Analysis...")
        
        evo_state = self._load_json(self.evolution_state_path)
        top_early = self._load_json(self.early_theme_path)
        signals = self._load_json(self.signal_path)
        flow = self._load_json(self.flow_path)
        top_topic = self._load_json(self.top_topic_path)
        
        if not evo_state:
            print("[NarrativeMomentumEngine] ⚠️ No evolution state found. Skipping.")
            return None
            
        theme_name = evo_state.get("theme", "Unknown")
        
        # 1. Narrative Acceleration (0.30)
        # Based on evolution score and topic presence
        narrative_accel = evo_state.get("narrative_spread", 0.5) * 0.8 # Simulated acceleration
        
        # 2. Capital Flow Acceleration (0.25)
        # Change in capital flow confirmation
        capital_flow_accel = evo_state.get("capital_flow_confirmation", 0.5) * 0.7
        
        # 3. Signal Density Change (0.25)
        # Based on early theme score
        signal_density_change = top_early.get("score", 0.6) * 0.6
        
        # 4. Topic Pressure Trend (0.20)
        # Simulated trend based on evolution stage
        topic_trend = 0.5
        if evo_state.get("stage") == "EMERGING":
            topic_trend = 0.8
        elif evo_state.get("stage") == "EXPANSION":
            topic_trend = 0.9
        elif evo_state.get("stage") == "EXHAUSTION":
            topic_trend = -0.5
            
        # Momentum Score Calculation (-1.0 to +1.0)
        # For simulation, we map positive drivers to positive momentum
        momentum_score = (
            0.30 * narrative_accel +
            0.25 * capital_flow_accel +
            0.25 * signal_density_change +
            0.20 * topic_trend
        )
        
        # Clip to [-1.0, 1.0]
        momentum_score = max(-1.0, min(1.0, momentum_score))
        
        state = self._get_momentum_state(momentum_score)
        
        why_momentum = []
        if narrative_accel > 0.4: why_momentum.append("내러티브 탐지 빈도가 급격히 상승 중")
        if capital_flow_accel > 0.4: why_momentum.append("관련 테마로의 자본 유입 속도 가속화")
        if signal_density_change > 0.4: why_momentum.append("이상 신호의 발생 밀도가 임계치 돌파")
        if topic_trend > 0.6: why_momentum.append("시스템 엔진의 주제 선정 압력이 우상향")

        momentum_state = {
            "theme": theme_name,
            "momentum_score": round(momentum_score, 2),
            "momentum_state": state,
            "narrative_acceleration": round(narrative_accel, 2),
            "capital_flow_acceleration": round(capital_flow_accel, 2),
            "signal_density_change": round(signal_density_change, 2),
            "topic_pressure_trend": round(topic_trend, 2),
            "why_momentum": why_momentum,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        top_momentum = {
            "theme": theme_name,
            "momentum_state": state,
            "momentum_score": round(momentum_score, 2),
            "action_hint": self._get_action_hint(state)
        }
        
        # Save files
        with open(self.output_dir / "theme_momentum_state.json", "w", encoding="utf-8") as f:
            json.dump(momentum_state, f, indent=2, ensure_ascii=False)
            
        with open(self.output_dir / "top_theme_momentum.json", "w", encoding="utf-8") as f:
            json.dump(top_momentum, f, indent=2, ensure_ascii=False)
            
        print(f"[NarrativeMomentumEngine] Momentum Analysis complete: {theme_name} -> {state}")
        return top_momentum

if __name__ == "__main__":
    root = Path(__file__).parent.parent.parent
    engine = NarrativeMomentumEngine(root)
    engine.run_momentum_analysis()
