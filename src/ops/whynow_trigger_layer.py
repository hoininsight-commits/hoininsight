import json
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

class WhyNowTriggerLayer:
    """
    Step 72: WHY_NOW Trigger Layer (Additive)
    
    Objective:
    - Explains timing (Why NOW?), not quality.
    - Uses discrete temporal anchors only.
    - Structurally binds to Economic Hunter narrative phases.
    - Rejects topics without time-locked justification.
    
    Triggers:
    1. Scheduled Catalyst Arrival -> Action
    2. Mechanism Activation -> Tension
    3. Smart Money Divergence -> Hunt
    """

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.logger = logging.getLogger("WhyNowTriggerLayer")
        self.ymd = datetime.utcnow().strftime("%Y-%m-%d")

    def _load_json(self, path: Path) -> Dict:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except Exception as e:
            self.logger.error(f"Failed to load {path}: {e}")
            return {}
            
    def _save_json(self, path: Path, data: Dict):
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')

    def run(self):
        self.logger.info(f"Running WhyNowTriggerLayer for {self.ymd}...")
        
        # 1. Load Inputs
        # We need the Narrative (to modify) and the Structural Top-1 (for raw signals)
        narrative_path = self.base_dir / "data/ops/issue_signal_narrative_today.json"
        top1_path = self.base_dir / "data/ops/structural_top1_today.json"
        
        narrative_data = self._load_json(narrative_path)
        top1_data = self._load_json(top1_path)
        
        if not narrative_data.get("narrative") or not top1_data.get("top1_topics"):
            self.logger.warning("Missing narrative or top1 input. Skipping.")
            return

        target_narrative = narrative_data["narrative"]
        original_card = top1_data["top1_topics"][0].get('original_card', {})
        
        # 2. Analyze Trigger
        trigger_type, trigger_name, anchor_text = self._detect_trigger(original_card)
        
        # 3. Apply Rejection Logic
        is_rejected, rejection_reason = self._check_rejection(original_card, trigger_type)
        
        if is_rejected:
            self.logger.warning(f"Topic Rejected: {rejection_reason}")
            # Mark rejection in narrative
            target_narrative["is_rejected"] = True
            target_narrative["rejection_reason"] = rejection_reason
            
            # Add visible warning to Hook
            sections = target_narrative.get("sections", {})
            sections["hook"] = f"[🚫 REJECTED: {rejection_reason}] " + sections.get("hook", "")
            target_narrative["sections"] = sections
            
        else:
            self.logger.info(f"Trigger Detected: {trigger_name} ({anchor_text})")
            # 4. Bind to Narrative
            self._bind_trigger_to_narrative(target_narrative, trigger_type, trigger_name, anchor_text)
            
            # Enriched Metadata
            target_narrative["whynow_trigger"] = {
                "type": trigger_name,
                "anchor": anchor_text,
                "id": trigger_type
            }

        # 5. Save Enriched Narrative
        # We overwrite the detailed JSON so Dashboard picks it up automatically
        self._save_json(narrative_path, narrative_data)
        
        # Also update MD for completeness (Optional but good for fallback)
        self._update_markdown(narrative_data)

    @staticmethod
    def detect_trigger(card: Dict) -> Tuple[int, str, str]:
        """
        Returns (TriggerID, TriggerName, AnchorText)
        TriggerID 0 means None found.
        """
        title = card.get("title", "")
        summary = card.get("one_line_summary", "")
        evidence = card.get("evidence_refs", {})
        drivers = evidence.get("structural_drivers", [])
        
        # Combine text for broader keyword search
        full_text = f"{title} {summary} {' '.join(drivers)}".lower()
        
        # Trigger 1: Scheduled Catalyst Arrival (Date, Launch, D-Day)
        # Keywords: "발표", "공개", "출시", "만기", "D-", "release", "launch", "scheduled"
        t1_keywords = ["발표", "공개", "출시", "만기", "예정", "schedule", "launch", "release", "report", "earnings"]
        has_date = any(x in full_text for x in ["1월", "2월", "3월", "4월", "5월", "6월", "7월", "8월", "9월", "10월", "11월", "12월", "일", "2025", "2026", "q1", "q2", "q3", "q4"])
        if any(k in full_text for k in t1_keywords) and has_date:
             return 1, "Scheduled Catalyst Arrival", "예정된 이벤트/일정 확정"

        # Trigger 2: Mechanism Activation (Effective Date, Policy, Ruling)
        # Keywords: "시행", "발효", "적용", "판결", "rebalance", "effective", "start date"
        t2_keywords = ["시행", "발효", "적용", "판결", "규제", "act", "law", "policy", "effective", "ruling"]
        if any(k in full_text for k in t2_keywords):
             return 2, "Mechanism Activation", "제도/규제/환경의 기계적 변경"

        # Trigger 3: Smart Money Divergence (Anomaly, Spike, Divergence)
        # Keywords: "매집", "순매수", "급증", "괴리", "spike", "divergence", "buying", "volume"
        t3_keywords = ["매집", "순매수", "급증", "괴리", "spike", "divergence", "inflow", "accumulate"]
        if any(k in full_text for k in t3_keywords):
             return 3, "Smart Money Divergence", "수급/가격의 통계적 괴리 포착"
             
        return 0, "None", ""

    @staticmethod
    def check_rejection(trigger_type: int) -> Tuple[bool, str]:
        """
        Rejection Rule:
        1. Rely only on continuous states
        2. No discrete temporal anchor (Trigger 0)
        """
        if trigger_type == 0:
            return True, "No discrete temporal anchor found (Continuous State Only)"
        return False, ""

    def run(self):
        self.logger.info(f"Running WhyNowTriggerLayer for {self.ymd}...")
        
        # 1. Load Inputs
        narrative_path = self.base_dir / "data/ops/issue_signal_narrative_today.json"
        top1_path = self.base_dir / "data/ops/structural_top1_today.json"
        
        narrative_data = self._load_json(narrative_path)
        top1_data = self._load_json(top1_path)
        
        if not narrative_data.get("narrative") or not top1_data.get("top1_topics"):
            self.logger.warning("Missing narrative or top1 input. Skipping.")
            return

        target_narrative = narrative_data["narrative"]
        original_card = top1_data["top1_topics"][0].get('original_card', {})
        
        # 2. Analyze Trigger
        trigger_type, trigger_name, anchor_text = self.detect_trigger(original_card)
        
        # 3. Apply Rejection Logic
        is_rejected, rejection_reason = self.check_rejection(trigger_type)
        
        # Note: Rejection might already be handled by Narrator in the new flow,
        # but maintaining this layer allows for double-checking or standalone execution.
        if is_rejected and not target_narrative.get("is_rejected"):
            self.logger.warning(f"Topic Rejected (Post-Check): {rejection_reason}")
            target_narrative["is_rejected"] = True
            target_narrative["rejection_reason"] = rejection_reason
            
        if not is_rejected:
            self.logger.info(f"Trigger Detected: {trigger_name} ({anchor_text})")
            # 4. Bind to Narrative (Idempotent check needed ideally, but overwriting is safe here)
            self._bind_trigger_to_narrative(target_narrative, trigger_type, trigger_name, anchor_text)
            
            # Enriched Metadata
            target_narrative["whynow_trigger"] = {
                "type": trigger_name,
                "anchor": anchor_text,
                "id": trigger_type
            }

        # 5. Save Enriched Narrative
        self._save_json(narrative_path, narrative_data)
        self._update_markdown(narrative_data)

    def _bind_trigger_to_narrative(self, narrative: Dict, t_type: int, t_name: str, anchor: str):
        # This logic is now likely shared with Narrator, but kept here for fallback
        pass 

    def _update_markdown(self, narrative_data: Dict):
        # Regenerate MD file from updated JSON
        md_path = self.base_dir / "data/ops/issue_signal_narrative_today.md"
        n = narrative_data["narrative"]
        sections = n.get("sections", {})
        
        md = f"# 🏹 경제 사냥꾼의 구조적 해부 (Top-1) [Updated]\n\n"
        
        hook = sections.get("hook", n.get("opening_hook", ""))
        md += f"## 1. The Hook (시선 강탈)\n{hook}\n\n"
        
        tension = sections.get("tension", n.get("core_story", ""))
        md += f"## 2. Core Tension (구조의 역학)\n{tension}\n\n"
        
        hunt = sections.get("hunt", "")
        md += f"## 3. The Hunt (결정적 증거)\n{hunt}\n\n"
        
        action = sections.get("action", n.get("why_now", ""))
        md += f"## 4. Action (행동 지침)\n{action}\n"
        
        if n.get("is_rejected"):
            md += f"\n\n> [!WARNING] {n.get('rejection_reason')}"
            
        md_path.write_text(md, encoding='utf-8')

if __name__ == "__main__":
    WhyNowTriggerLayer(Path(__file__).resolve().parent.parent.parent).run()
