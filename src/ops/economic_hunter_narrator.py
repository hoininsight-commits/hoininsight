import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

class EconomicHunterNarrator:
    """
    Step 71: Economic Hunter Narrative Layer
    Transforms the 'Structural Top-1' topic into a compelling 'Economic Hunter' script
    using the 4-step structure: Hook -> Tension -> Hunt -> Action.
    Deterministic, Template-based.
    """
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.logger = logging.getLogger("EconomicHunterNarrator")
        self.ymd = datetime.utcnow().strftime("%Y-%m-%d")
        
    def _load_json(self, path: Path) -> Dict:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except Exception as e:
            self.logger.error(f"Failed to load {path}: {e}")
            return {}

    def run(self):
        self.logger.info(f"Running EconomicHunterNarrator for {self.ymd}...")
        
        # 1. Load Structural Top-1
        top1_path = self.base_dir / "data/ops/structural_top1_today.json"
        top1_data = self._load_json(top1_path)
        
        top1_list = top1_data.get('top1_topics', [])
        if not top1_list:
            self.logger.warning("No Top-1 topic found. Skipping narrative generation.")
            self._write_empty_result()
            return

        top1 = top1_list[0]
        original_card = top1.get('original_card', {})
        
        # 2. Extract Fields
        title = top1.get('title', 'Untitled')
        summary = top1.get('one_line_summary', '')
        why_now = top1.get('why_now', '')
        
        evidence = original_card.get('evidence_refs', {})
        drivers = evidence.get('structural_drivers', [])
        risk = evidence.get('risk_factor', '확인 필요')
        
        # [NEW] Step 73: Bind WhyNow Trigger
        try:
            from src.ops.whynow_trigger_layer import WhyNowTriggerLayer
            # Use public detection logic
            trigger_type, trigger_name, anchor_text = WhyNowTriggerLayer.detect_trigger(original_card)
            # Use public rejection logic
            is_rejected, rejection_reason = WhyNowTriggerLayer.check_rejection(trigger_type)
        except ImportError:
            # Fallback if module not found/refactored differently, though it should exist
            self.logger.error("Could not import WhyNowTriggerLayer")
            trigger_type, trigger_name, anchor_text = 0, "Unknown", ""
            is_rejected, rejection_reason = False, ""
        
        if is_rejected and original_card.get("escalation_status") != "ESC_WHY_NOW":
            self.logger.warning(f"Topic Rejected by WhyNow Layer: {rejection_reason}")
            self._write_rejected_result(title, rejection_reason)
            return
        
        if original_card.get("escalation_status") == "ESC_WHY_NOW":
             self.logger.info(f"Topic Escalated: Bypassing standard WhyNow rejection.")
             is_rejected = False # Ensure we proceed

        # 3. Generate Narrative (4-Step Structure)
        
        # Step 1: The Hook (역발상 질문)
        hook = f"님들, '{title}' 이슈가 단순한 뉴스가 아니라는 거 알고 있었어?"
        if "실적" in title:
            hook = f"님들, '{title}' 숫자에 숨겨진 진짜 의미, 다들 놓치고 있는 거 알아?"
        elif "트럼프" in title or "정책" in title:
            hook = f"님들, '{title}' 뒤에 숨겨진 진짜 의도, 99%는 모르더라."

        # Step 2: Core Tension (구조적 역학/위협)
        tension = (
            f"지금 시장은 '{summary}' 흐름을 단순한 정보로만 보고 있어. "
            f"하지만 진짜 선수들은 이게 구조적 재정의(Structural Redefinition)의 신호탄이라는 걸 알고 있지. "
            f"표면적인 뉴스보다 그 밑단에서 작동하는 거대한 머니 무브(Money Move)를 봐야 해."
        )

        # Step 3: The Hunt (3-5 Evidence Points)
        hunt_points = []
        for i, driver in enumerate(drivers):
            hunt_points.append(f"{i+1}️⃣ {driver}")
        
        if not hunt_points:
             hunt_points.append("1️⃣ 구조적 수급 변화 포착")
             hunt_points.append("2️⃣ 이익률의 구조적 레벨업")
             hunt_points.append("3️⃣ 외국인/기관의 비정상적 매집")

        hunt_text = "경제 사냥꾼이 포착한 결정적 증거 3가지는 이거야.\n\n" + "\n".join(hunt_points)

        # Step 4: Actionable Connection (행동 지침)
        action = (
            f"결론 딱 정해줄게. '{risk}' 리스크만 체크되면 지금이 진입 타이밍이야. "
            f"특히 {why_now}. "
            f"남들 뉴스 보고 헤맬 때 우리는 이 구조적 변화에 올라타자. 지금 기회는 다시 안 올 수도 있어."
        )
        
        # [NEW] Inject [⚡ WHY NOW] Binding
        esc_info = original_card.get("escalation_info")
        self.logger.info(f"Escalation Status: {original_card.get('escalation_status')}")
        if original_card.get("escalation_status") == "ESC_WHY_NOW" and esc_info:
            trigger_name = esc_info.get("trigger_name", "Escalated Trigger")
            reason = esc_info.get("reason", "N/A")
            timeline = esc_info.get("timeline", [])
            timeline_str = " -> ".join(timeline[-3:]) if timeline else "N/A"
            self.logger.info(f"Escalating: {trigger_name} (Reason: {reason})")
            
            why_now_block = f"\n\n[⚡ WHY NOW – Escalated]\n- **Trigger:** {trigger_name}\n- **Escalation Reason:** {reason}\n- **Timeline:** {timeline_str}\n\n이 이슈는 Pre-Structural 단계에서 포착된 후, 시스템 조건 충족으로 인해 자동으로 WHY NOW로 승격되었습니다."
            
            # Inject based on trigger mapping logic in Step 75
            t_id = esc_info.get("trigger_id")
            if t_id == 1: action += why_now_block
            elif t_id == 2: tension += why_now_block
            else: hunt_text += why_now_block
        else:
            # Fallback to direct detection or existing trigger
            self.logger.info(f"Using standard/fallback trigger: {trigger_name}")
            why_now_block = f"\n\n[⚡ WHY NOW: {trigger_name}]\n이 이슈가 지금 중요한 이유는 '{anchor_text}' 때문입니다. 시점이 명확한 트리거입니다."
            if trigger_type == 1: action += why_now_block
            elif trigger_type == 2: tension += why_now_block
            elif trigger_type == 3: hunt_text += why_now_block

        # 4. Construct Output Object
        narrative = {
            "topic_id": original_card.get('topic_id'),
            "title": title,
            "narrative_type": "ECONOMIC_HUNTER_V1",
            "sections": {
                "hook": hook,
                "tension": tension,
                "hunt": hunt_text,
                "action": action
            },
            "raw_drivers": drivers,
            "risk_note": risk,
            "source_basis": ["STRUCTURAL_SEED", "ISSUE_SIGNAL"],
            "confidence": "HIGH",
            "whynow_trigger": {
                "type": trigger_name,
                "anchor": anchor_text,
                "id": trigger_type
            }
        }
        
        # 5. Output JSON & MD
        out_json_path = self.base_dir / "data/ops/issue_signal_narrative_today.json"
        out_data = {
            "run_date": self.ymd,
            "narrative": narrative
        }
        out_json_path.write_text(json.dumps(out_data, indent=2, ensure_ascii=False), encoding='utf-8')
        
        # Markdown Output
        out_md_path = self.base_dir / "data/ops/issue_signal_narrative_today.md"
        md = f"# 🏹 경제 사냥꾼의 구조적 해부 (Top-1)\n\n"
        md += f"## 1. The Hook (시선 강탈)\n{hook}\n\n"
        md += f"## 2. Core Tension (구조의 역학)\n{tension}\n\n"
        md += f"## 3. The Hunt (결정적 증거)\n{hunt_text}\n\n"
        md += f"## 4. Action (행동 지침)\n{action}\n"
        
        out_md_path.write_text(md, encoding='utf-8')
        self.logger.info(f"Generated Economic Hunter narrative for {title}")

    def _write_empty_result(self):
        out_json_path = self.base_dir / "data/ops/issue_signal_narrative_today.json"
        out_json_path.write_text(json.dumps({"run_date": self.ymd, "narrative": None}, indent=2), encoding='utf-8')
        
        out_md_path = self.base_dir / "data/ops/issue_signal_narrative_today.md"
        out_md_path.write_text("# 경제 사냥꾼의 구조적 해부\n\n- 내러티브 생성 대상 없음.", encoding='utf-8')

    def _write_rejected_result(self, title: str, reason: str):
         out_json_path = self.base_dir / "data/ops/issue_signal_narrative_today.json"
         narrative = {
             "title": title,
             "is_rejected": True,
             "rejection_reason": reason,
             "sections": {
                 "hook": f"[🚫 REJECTED: {reason}] {title}"
             }
         }
         out_json_path.write_text(json.dumps({"run_date": self.ymd, "narrative": narrative}, indent=2, ensure_ascii=False), encoding='utf-8')
          
         out_md_path = self.base_dir / "data/ops/issue_signal_narrative_today.md"
         out_md_path.write_text(f"# [REJECTED] {title}\n\n> [!WARNING] {reason}", encoding='utf-8')

if __name__ == "__main__":
    EconomicHunterNarrator(Path(__file__).resolve().parent.parent.parent).run()
