import json
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple

class EconomicHunterTopicLockLayer:
    """
    Step 76: ECONOMIC_HUNTER_TOPIC_LOCK_LAYER
    Decides if a Top-1 topic should be locked into the 'Economic Hunter' video format.
    """
    
    STRUCTURAL_ACTORS = [
        "정부", "대통령", "중앙은행", "FED", "연준", "빅테크", "BIGTECH", 
        "군사", "관세", "규제", "GOVERNMENT", "PRESIDENT", "CENTRAL BANK"
    ]

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.logger = logging.getLogger("EconomicHunterTopicLockLayer")

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

    def evaluate_lock(self) -> Dict[str, Any]:
        """
        Evaluate if the Top-1 should be locked.
        """
        # 1. Load Inputs
        top1_path = self.base_dir / "data/ops/structural_top1_today.json"
        narrative_path = self.base_dir / "data/ops/issue_signal_narrative_today.json"
        
        top1_data = self._load_json(top1_path)
        narrative_data = self._load_json(narrative_path)
        
        if not top1_data.get("top1_topics") or not narrative_data.get("narrative"):
            self.logger.error("Reject: Missing Step 74/72/75 inputs.")
            return {"topic_lock": False, "reason": "Missing inputs"}

        topic = top1_data["top1_topics"][0]
        original_card = topic.get("original_card", {})
        narrative = narrative_data["narrative"]
        
        # Check WHY_NOW (Step 72 result in narrative)
        whynow_trigger = narrative.get("whynow_trigger")
        if not whynow_trigger:
            self.logger.warning("Reject: No WHY_NOW trigger found.")
            return {"topic_lock": False, "reason": "No WHY_NOW trigger"}

        # Perform Condition Checks
        cond_a, cond_a_detail = self._check_condition_a(original_card)
        cond_b, cond_b_detail = self._check_condition_b(original_card)
        cond_c, cond_c_detail = self._check_condition_c(original_card)
        cond_d, cond_d_detail = self._check_condition_d(narrative)

        satisfied = []
        details = []
        if cond_a: 
            satisfied.append("A")
            details.append(cond_a_detail)
        if cond_b: 
            satisfied.append("B")
            details.append(cond_b_detail)
        if cond_c: 
            satisfied.append("C")
            details.append(cond_c_detail)
        if cond_d: 
            satisfied.append("D")
            details.append(cond_d_detail)

        # Reject Rule (Step 76-7)
        is_rejected, reject_reason = self._check_rejection_rules(narrative, satisfied)
        if is_rejected:
            self.logger.info(f"Topic Rejected from Top-1 Lock: {reject_reason}")
            # We don't necessarily delete the topic, but we prevent locking and could flag for removal
            topic["topic_lock"] = False
            topic["topic_format"] = "STANDARD_REPORT"
            topic["reject_info"] = reject_reason
            self._save_json(top1_path, top1_data)
            return {"topic_lock": False, "reason": reject_reason}

        # Lock Decision (2+ conditions)
        if len(satisfied) >= 2:
            decisive = satisfied[0] # Simplification for requirement
            lock_info = {
                "topic_format": "ECONOMIC_HUNTER_VIDEO",
                "topic_lock": True,
                "satisfied_conditions": satisfied,
                "decisive_factor": decisive,
                "lock_reason": f"Conditions {', '.join(satisfied)} met: {'; '.join(details)}"
            }
            topic.update(lock_info)
            self.logger.info(f"Topic LOCKED as Economic Hunter: {satisfied}")
        else:
            topic["topic_lock"] = False
            topic["topic_format"] = "STANDARD_REPORT"
            self.logger.info(f"Topic NOT Locked (Conditions: {satisfied})")

        # Save Result
        self._save_json(top1_path, top1_data)
        
        return topic

    def _check_condition_a(self, card: Dict) -> Tuple[bool, str]:
        # Lock Condition A — 시간 압력
        ps = card.get("pre_structural_signal", {})
        anchor = ps.get("temporal_anchor", "").lower()
        
        # Deadlines
        keywords = ["deadline", "d-day", "만기", "시행", "결정", "발표", "확정"]
        if any(k in anchor for k in keywords):
            return True, f"Deadline found in anchor: {anchor}"
            
        # Escalation Time Compression
        esc_info = card.get("escalation_info", {})
        if "A" in esc_info.get("reason", ""):
            return True, "Time Compression detected in Escalation"
            
        return False, ""

    def _check_condition_b(self, card: Dict) -> Tuple[bool, str]:
        # Lock Condition B — 구조적 행위자
        ps = card.get("pre_structural_signal", {})
        actor = ps.get("trigger_actor", "")
        entities = ps.get("related_entities", [])
        
        all_actors = [actor] + entities
        for a in all_actors:
            if any(keyword in a.upper() for keyword in self.STRUCTURAL_ACTORS):
                return True, f"Structural Actor detected: {a}"
        return False, ""

    def _check_condition_c(self, card: Dict) -> Tuple[bool, str]:
        # Lock Condition C — 행동 강제성
        ps = card.get("pre_structural_signal", {})
        rationale = ps.get("rationale", "").lower()
        up_cond = ps.get("escalation_path", {}).get("condition_to_upgrade_to_WHY_NOW", "").lower()
        
        keywords = ["선택이 아닌 대응", "강요", "불가피", "mandatory", "forced", "inevitable", "must respond"]
        if any(kw in rationale for kw in keywords) or any(kw in up_cond for kw in keywords):
            return True, "Forced response structure detected"
        return False, ""

    def _check_condition_d(self, narrative: Dict) -> Tuple[bool, str]:
        # Lock Condition D — 내러티브 압력
        # Why Now section phrasing check
        whynow_block = ""
        sections = narrative.get("sections", {})
        # Search for why now block in action or tension where whynow_trigger is bound
        text = str(sections.get("action", "")) + str(sections.get("tension", "")) + str(sections.get("hunt", ""))
        
        keywords = ["지금 말하지 않으면 늦는다", "마지막 기회", "임계점", "지금 당장", "긴급", "urgent", "now or never"]
        if any(kw in text for kw in keywords):
            return True, "Narrative implies 'now or never' urgency"
        return False, ""

    def _check_rejection_rules(self, narrative: Dict, satisfied: List[str]) -> Tuple[bool, str]:
        # Step 76-7 Reject Rules
        
        # 1. No Lock conditions met despite WHY_NOW
        if not satisfied:
            return True, "No lock conditions met despite having WHY_NOW"
            
        # 2. Status-type language (Outlook, possibility, concern)
        title = narrative.get("title", "").lower()
        sections = narrative.get("sections", {})
        combined_text = (title + str(sections.get("hook", ""))).lower()
        
        status_keywords = ["전망", "가능성", "우려", "outlook", "possibility", "concern", "potential"]
        # If ONLY status keywords and no strong lock conditions?
        # Actually rule says "상태형 언어만 존재하는 경우"
        # We check if there are strong verbs vs status verbs.
        if any(kw in combined_text for kw in status_keywords) and len(satisfied) < 2:
            return True, "Only status-type language detected"

        # 3. 30일 후에도 동일한 내러티브가 유지 가능한 경우 (Durability)
        # If there's no temporal pressure (A) and it's meta-topic-ish
        if "A" not in satisfied and "C" not in satisfied:
             # Assume lack of A and C means it might be a slow-burn topic
             return True, "Topic lacks immediate temporal or structural urgency (Durability too high)"
             
        return False, ""
