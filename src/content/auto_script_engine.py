import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AutoScriptEngine")

class AutoScriptEngine:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data"
        self.ops_dir = self.data_dir / "ops"
        self.output_dir = self.data_dir / "content"

    def run_analysis(self):
        logger.info("Starting Auto Narrative Script Generation...")
        
        # 1. Load Data
        actions = self._load_json(self.ops_dir / "operator_actions.json", [])
        escalation = self._load_json(self.ops_dir / "narrative_escalation.json", [])
        early_topics = self._load_json(self.ops_dir / "early_topic_candidates.json", [])
        capital_flow = self._load_json(self.ops_dir / "capital_flow_impact.json", {}) # Standard filename
        portfolio = self._load_json(self.ops_dir / "portfolio_relevance.json", {})
        mentionables = self._load_json(self.ops_dir / "mentionables.json", [])
        today_data = self._load_json(self.project_root / "docs" / "data" / "decision" / "today.json", {})

        # Mapping for easy lookup
        esc_map = {item["theme"]: item for item in escalation if "theme" in item}
        
        scripts = []
        
        # 2. Filter & Generate
        for action_item in actions:
            theme = action_item.get("theme")
            action = action_item.get("action")
            
            esc_item = esc_map.get(theme, {})
            stage = esc_item.get("stage", "QUIET")
            
            # Condition: Action TRACK/FOCUS or Stage ESCALATING+
            is_high_priority = action in ["TRACK", "FOCUS"]
            is_escalating = stage in ["ESCALATING", "DOMINANT"]
            
            if not (is_high_priority or is_escalating):
                continue
                
            logger.info(f"Generating script for high-priority theme: {theme} ({action}/{stage})")
            
            # 3. Component Generation
            script_obj = self._generate_components(
                theme=theme,
                action_item=action_item,
                esc_item=esc_item,
                capital_flow=capital_flow,
                portfolio=portfolio,
                today_data=today_data
            )
            
            scripts.append({
                "theme": theme,
                "action": action,
                "escalation_stage": stage,
                "action_score": action_item.get("action_score"),
                "script": script_obj,
                "script_full": self._assemble_full_text(script_obj)
            })

        # 4. Save Output
        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_path = self.output_dir / "auto_scripts.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(scripts, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Auto Script analysis completed. Generated {len(scripts)} scripts at {output_path}")

    def _generate_components(self, theme: str, action_item: Dict, esc_item: Dict, capital_flow: Dict, portfolio: Dict, today_data: Dict) -> Dict:
        """Generates the 7 core components of the script."""
        
        # 1. Hook
        hooks = [
            f"지금 시장에서 조용히 커지고 있는 {theme} 이야기 알고 있었어?",
            f"지금 시장이 갑자기 {theme}에 반응하는 이유 알고 있었어?",
            f"당신이 놓치고 있을지 모를 {theme}의 거대한 신호가 포착됐어."
        ]
        hook = hooks[action_item.get("action_score", 0) % len(hooks)]

        # 2. Context
        context = f"최근 시장에서는 {theme} 관련 신호가 빠르게 증가하고 있어. "
        context += "단순한 노이즈가 아니라 구조적인 변화의 시작일 가능성이 매우 높은 상태야."

        # 3. Why Now
        why_now = "이번 움직임이 특히 중요한 이유는 "
        reasons = []
        if esc_item.get("cycle_reactivation"): reasons.append("내러티브 주기의 재점화")
        if esc_item.get("evolution_alignment"): reasons.append("테마 진화 경로와의 일치")
        if esc_item.get("narrative_propagation"): reasons.append("확산 속도의 급격한 가속")
        
        if not reasons:
            why_now += f"현재 이 내러티브가 {esc_item.get('stage', '상승')} 단계에 진입했기 때문이야."
        else:
            why_now += f"{', '.join(reasons)} 같은 결정적 신호들이 동시에 나타나고 있기 때문이지."

        # 4. Evidence
        score = action_item.get("action_score", 0)
        conf = action_item.get("confidence", "NORMAL")
        evidence = f"실제로 엔진 분석 결과, 이번 테마의 액션 스코어는 {score}점을 기록했어. "
        evidence += f"내러티브 성장세가 {esc_item.get('velocity', '강력한')} 속도로 진행 중이라는 점이 데이터로 증명되고 있어."

        # 5. Market Impact
        # Try to get sector from capital_flow or generic
        sectors = capital_flow.get("top_sectors", ["관련 핵심 분야"])
        if isinstance(sectors, list) and len(sectors) > 0:
            sector_text = " 및 ".join(sectors[:2])
        else:
            sector_text = "핵심 수혜 분야"
            
        market_impact = f"이 흐름이 이어진다면 시장에서는 {sector_text} 같은 섹터들이 가장 먼저 반응할 가능성이 높아. "
        market_impact += "자본의 흐름이 이미 이 방향을 가리키고 있다는 점에 주목해야 해."

        # 6. Operator Insight
        action = action_item.get("action", "OBSERVE")
        operator_insight = f"현재 운영 엔진의 하달된 공식 액션은 '{action}'이야. "
        if action == "FOCUS":
            operator_insight += "지금은 모든 화력을 집중해서 이 흐름의 정점을 포착해야 하는 구간이야."
        elif action == "TRACK":
            operator_insight += "본격적인 폭발 직전 단계에서 흐름을 놓치지 말고 추적해야 하는 타이밍인 거지."
        else:
            operator_insight += "차분하게 시장의 반응을 살피며 대응 전략을 짜야 하는 시기야."

        # 7. Closing
        closing = f"지금 시장이 왜 다시 {theme} 이야기를 꺼내기 시작했을까? "
        closing += "앞으로 이 흐름이 어디까지 번질지 우리 엔진과 함께 계속 지켜봐야 할 것 같아."

        return {
            "hook": hook,
            "context": context,
            "why_now": why_now,
            "evidence": evidence,
            "market_impact": market_impact,
            "operator_insight": operator_insight,
            "closing": closing
        }

    def _assemble_full_text(self, obj: Dict) -> str:
        return "\n\n".join([
            obj["hook"],
            obj["context"],
            obj["why_now"],
            obj["evidence"],
            obj["market_impact"],
            obj["operator_insight"],
            obj["closing"]
        ])

    def _load_json(self, path: Path, default: Any) -> Any:
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except Exception as e:
                logger.error(f"Error loading {path}: {e}")
        return default

if __name__ == "__main__":
    import sys
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    engine = AutoScriptEngine(root)
    engine.run_analysis()
