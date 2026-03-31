import os
import json
from pathlib import Path
from datetime import datetime

class ThemeEvolutionEngine:
    """
    Engine to determine the lifecycle stage of a detected theme.
    Classifies themes into: PRE-STORY, EMERGING, EXPANSION, MAINSTREAM, EXHAUSTION.
    """
    
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.early_theme_path = self.project_root / "data" / "theme" / "top_early_theme.json"
        self.narrative_path = self.project_root / "data" / "theme" / "theme_narrative.json"
        self.signal_path = self.project_root / "data" / "ops" / "hoin_signal_today.json"
        self.flow_path = self.project_root / "data" / "ops" / "capital_flow_impact.json"
        self.story_path = self.project_root / "data" / "story" / "today_story.json"
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

    def _get_stage(self, score):
        if score <= 0.20: return "PRE-STORY"
        if score <= 0.40: return "EMERGING"
        if score <= 0.65: return "EXPANSION"
        if score <= 0.85: return "MAINSTREAM"
        return "EXHAUSTION"

    def _get_action_hint(self, stage):
        hints = {
            "PRE-STORY": "WATCH / MONITOR",
            "EMERGING": "TRACK / PREPARE",
            "EXPANSION": "ACTION / ACCUMULATE",
            "MAINSTREAM": "HOLD / TAKE PROFIT",
            "EXHAUSTION": "EXIT / AVOID"
        }
        return hints.get(stage, "OBSERVE")

    def run_evolution_analysis(self):
        print("[ThemeEvolutionEngine] Starting Lifecycle Evolution Analysis...")
        
        top_early = self._load_json(self.early_theme_path)
        narrative = self._load_json(self.narrative_path)
        signals = self._load_json(self.signal_path)
        flow = self._load_json(self.flow_path)
        story = self._load_json(self.story_path)
        top_topic = self._load_json(self.top_topic_path)
        
        if not top_early:
            print("[ThemeEvolutionEngine] ⚠️ No top early theme found. Skipping.")
            return None
            
        theme_name = top_early.get("theme", "Unknown")
        
        # 1. Signal Breadth (0.25)
        # Based on number of supporting signals in top_early
        support_signals = top_early.get("signals", [])
        signal_breadth = min(1.0, len(support_signals) / 4.0)
        
        # 2. Narrative Spread (0.20)
        # Check if theme is mentioned in story or top_topic
        narrative_spread = 0.0
        if story and theme_name.lower() in str(story).lower():
            narrative_spread += 0.5
        if top_topic and theme_name.lower() in str(top_topic).lower():
            narrative_spread += 0.5
            
        # 3. Capital Flow Confirmation (0.20)
        capital_conf = 0.0
        if flow:
            flow_theme = flow.get("top_capital_flow_theme", {}).get("theme", "")
            if theme_name.lower() in flow_theme.lower():
                capital_conf = 1.0
            elif flow.get("top_capital_flow_theme", {}).get("impact_direction") == "POSITIVE":
                capital_conf = 0.5 # Indirect support
                
        # 4. Persistence (0.20)
        # For now, base it on the score from early detection
        persistence = top_early.get("score", 0.5)
        
        # 5. Saturation (0.15)
        # Higher if it's already top_topic
        saturation = 0.0
        if top_topic and theme_name.lower() in str(top_topic).lower():
            saturation = 0.7
        
        # Evolution Score Calculation
        evo_score = (
            0.25 * signal_breadth +
            0.20 * narrative_spread +
            0.20 * capital_conf +
            0.20 * persistence +
            0.15 * (1.0 - saturation)
        )
        
        stage = self._get_stage(evo_score)
        
        why_stage = []
        if signal_breadth > 0.6: why_stage.append("다양한 데이터 채널에서 중복 신호 포착")
        if narrative_spread > 0.4: why_stage.append("시장 서사(Market Story) 단계로 진입 중")
        if capital_conf > 0.6: why_stage.append("실제 자본 흐름의 뒷받침을 확인")
        if saturation < 0.3: why_stage.append("아직 시장 전반에 퍼지지 않은 초기 상태")
        else: why_stage.append("이미 주요 내러티브로 인식되고 있음")

        evolution_state = {
            "theme": theme_name,
            "stage": stage,
            "score": round(evo_score, 2),
            "signal_breadth": round(signal_breadth, 2),
            "narrative_spread": round(narrative_spread, 2),
            "capital_flow_confirmation": round(capital_conf, 2),
            "persistence": round(persistence, 2),
            "saturation": round(saturation, 2),
            "why_stage": why_stage,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        top_evolution = {
            "theme": theme_name,
            "stage": stage,
            "summary": f"{theme_name} 테마는 현재 {stage} 단계에 있으며, 시스템은 {self._get_action_hint(stage)} 전략을 권고합니다.",
            "action_hint": self._get_action_hint(stage)
        }
        
        # Save files
        with open(self.output_dir / "theme_evolution_state.json", "w", encoding="utf-8") as f:
            json.dump(evolution_state, f, indent=2, ensure_ascii=False)
            
        with open(self.output_dir / "top_theme_evolution.json", "w", encoding="utf-8") as f:
            json.dump(top_evolution, f, indent=2, ensure_ascii=False)
            
        print(f"[ThemeEvolutionEngine] Evolution Analysis complete: {theme_name} -> {stage}")
        return top_evolution

if __name__ == "__main__":
    root = Path(__file__).parent.parent.parent
    engine = ThemeEvolutionEngine(root)
    engine.run_evolution_analysis()
