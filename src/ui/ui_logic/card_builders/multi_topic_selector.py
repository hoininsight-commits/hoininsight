import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

class MultiTopicSelector:
    """
    [IS-104] Multi-Topic Selection & Content Packaging Layer
    Selects 1 Long-form and 3~4 Short-form topics per day.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.decision_dir = base_dir / "data" / "decision"
        self.ui_dir = base_dir / "data" / "ui"
        self.logger = logging.getLogger("MultiTopicSelector")

    def load_json(self, path: Path) -> Any:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except Exception as e:
            self.logger.error(f"Failed to load {path}: {e}")
            return {}

    def run(self):
        # 1. Load Inputs
        # Primary source: interpretation_units.json (list of topics)
        topics = self.load_json(self.decision_dir / "interpretation_units.json")
        if not isinstance(topics, list):
            topics = []

        # Additional inputs for logic
        hero_lock = self.load_json(self.decision_dir / "hero_topic_lock.json")
        break_scenario = self.load_json(self.decision_dir / "break_scenario.json")
        risk_calendar = self.load_json(self.ui_dir / "schedule_risk_calendar_90d.json")
        
        # Current Date
        target_date = datetime.now().strftime("%Y-%m-%d")
        if topics:
            target_date = topics[0].get("as_of_date", target_date)

        # 2. Filter Candidate Pool
        candidates = []
        dropped_topics = []

        for t in topics:
            topic_id = t.get("interpretation_id") or t.get("topic_id")
            conf = t.get("confidence_score", 0.0)
            
            # Simple thresholding
            if conf < 0.3:
                dropped_topics.append({
                    "topic_id": topic_id,
                    "reason": f"신뢰도 부족 ({conf:.2f})"
                })
                continue
            
            # Additional metadata for role assignment
            candidates.append(t)

        # Sort by confidence score
        candidates.sort(key=lambda x: x.get("confidence_score", 0), reverse=True)

        # 3. Role Assignment
        long_form = None
        short_forms = []
        
        # LONG-FORM Assignment (Must be 1)
        if candidates:
            # First, check if there's a locked hero
            locked_id = hero_lock.get("topic_id")
            if locked_id:
                for i, c in enumerate(candidates):
                    if c.get("interpretation_id") == locked_id:
                        long_form = self._build_long_form(c)
                        candidates.pop(i)
                        break
            
            # If no lock found, pick the highest confidence
            if not long_form and candidates:
                long_form = self._build_long_form(candidates[0])
                candidates.pop(0)

        # SHORT-FORM Assignment (Max 3~4)
        for c in candidates:
            if len(short_forms) >= 4:
                dropped_topics.append({
                    "topic_id": c.get("interpretation_id"),
                    "reason": "최대 쇼츠 개수 초과 (우선순위 밀림)"
                })
                continue
            
            # Angle Detection (CAPITAL, SCHEDULE, FLOW, WARNING)
            angle = self._detect_angle(c, break_scenario, risk_calendar)
            hook = self._generate_short_hook(c, angle)
            
            short_forms.append({
                "topic_id": c.get("interpretation_id"),
                "angle": angle["desc"],
                "hook": hook,
                "type": angle["type"]
            })

        # Final Package
        package = {
            "date": target_date,
            "long_form": long_form if long_form else {
                "topic_id": "NONE",
                "title": "오늘의 메인 주제 없음",
                "reason": "적합한 구조적 서사가 발견되지 않았습니다.",
                "confidence": "HOLD"
            },
            "short_forms": short_forms,
            "dropped_topics": dropped_topics
        }

        # Save
        output_path = self.ui_dir / "daily_content_package.json"
        output_path.write_text(json.dumps(package, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"[SELECTOR] Generated {output_path}")

    def _build_long_form(self, t: Dict) -> Dict:
        return {
            "topic_id": t.get("interpretation_id"),
            "title": t.get("target_sector", "알 수 없는 섹터"),
            "reason": t.get("structural_narrative", "구조적 변화가 감지되었습니다."),
            "confidence": "READY" if t.get("confidence_score", 0) > 0.7 else "HOLD"
        }

    def _detect_angle(self, t: Dict, break_scenario: Dict, calendar: Dict) -> Dict:
        # Defaults
        angle_type = "FLOW"
        angle_desc = "섹터 흐름 변화"
        
        topic_id = t.get("interpretation_id")
        tags = t.get("evidence_tags", [])
        
        # 1. WARNING (Break Scenario)
        if break_scenario and break_scenario.get("topic_id") == topic_id:
            return {"type": "WARNING", "desc": "구조적 균열 위험"}
        
        # 2. SCHEDULE (Risk Calendar)
        if calendar and isinstance(calendar.get("fixed_events"), list):
            for ev in calendar["fixed_events"]:
                if ev.get("sector") == t.get("target_sector"):
                    return {"type": "SCHEDULE", "desc": f"주요 일정 ({ev.get('event_name')}) 임박"}

        # 3. CAPITAL (Flow or Earnings)
        if any(tag in ["FLOW_ROTATION", "CAPITAL_STRUCTURE"] for tag in tags):
            return {"type": "CAPITAL", "desc": "자본 수급 집중"}
        
        if "EARNINGS_VERIFY" in tags:
            return {"type": "CAPITAL", "desc": "실적 검증 국면"}

        return {"type": angle_type, "desc": angle_desc}

    def _generate_short_hook(self, t: Dict, angle: Dict) -> str:
        sector = t.get("target_sector", "섹터")
        if angle["type"] == "WARNING":
            return f"{sector} 파트너십 구조에 미세한 균열이 감지되었습니다."
        if angle["type"] == "SCHEDULE":
            return f"{sector} 관련 결정적 데이터 발표가 며칠 남지 않았습니다."
        if angle["type"] == "CAPITAL":
            return f"{sector} 쪽으로 외국인 수급이 비정상적으로 쏠리고 있습니다."
        
        return f"{sector} 시장의 핵심 동학이 바뀌는 조짐이 보입니다."

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    selector = MultiTopicSelector(Path("."))
    selector.run()
