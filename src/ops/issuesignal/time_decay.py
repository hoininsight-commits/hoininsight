from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

class TriggerTimeDecayEngine:
    """
    IS-33: TRIGGER_TIME_DECAY_ENGINE
    Manages the lifecycle and confidence decay of IssueSignal triggers.
    """

    STATE_KO = {
        "ACTIVE": "활성",
        "HOLD": "보류",
        "SILENT": "침묵"
    }

    def __init__(self, max_lifetime_hours: int = 48):
        self.max_lifetime_hours = max_lifetime_hours

    def process_trigger(self, trigger: Dict[str, Any], current_time: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Calculates confidence, determines state, and adds Korean metadata.
        """
        if current_time is None:
            current_time = datetime.now(timezone.utc)

        trigger_time_str = trigger.get("event_time_utc") or trigger.get("timestamp")
        if not trigger_time_str:
            # Fallback if no time: assume new
            trigger["current_confidence"] = 100
            trigger["decay_state_ko"] = self.STATE_KO["ACTIVE"]
            trigger["elapsed_time_str"] = "시간 정보 없음"
            return trigger

        try:
            # Handle common formats (Z or +00:00)
            trigger_time = datetime.fromisoformat(trigger_time_str.replace("Z", "+00:00"))
            if trigger_time.tzinfo is None:
                trigger_time = trigger_time.replace(tzinfo=timezone.utc)
        except ValueError:
            trigger["current_confidence"] = 100
            trigger["decay_state_ko"] = self.STATE_KO["ACTIVE"]
            trigger["elapsed_time_str"] = "형식 오류"
            return trigger

        # 1. Calc Elapsed Hours
        elapsed_delta = current_time - trigger_time
        elapsed_hours = max(0, elapsed_delta.total_seconds() / 3600)
        
        # 2. Calc Confidence
        initial_conf = trigger.get("initial_confidence", 100)
        # Linear decay: Current = Initial * (1 - Elapsed / MaxLife)
        decay_factor = max(0, 1 - (elapsed_hours / self.max_lifetime_hours))
        current_conf = int(initial_conf * decay_factor)
        
        # 3. Determine State
        state = "SILENT"
        if current_conf >= 70:
            state = "ACTIVE"
        elif current_conf >= 40:
            state = "HOLD"
        
        # Check for manual state override (irreversible unless re-armed)
        prev_state = trigger.get("decay_state_internal", "ACTIVE")
        if state == "ACTIVE" and prev_state in ["HOLD", "SILENT"]:
             state = prev_state
        elif state == "HOLD" and prev_state == "SILENT":
             state = prev_state

        # 4. Update Trigger
        trigger["current_confidence"] = current_conf
        trigger["decay_state_internal"] = state
        trigger["decay_state_ko"] = self.STATE_KO[state]
        trigger["elapsed_hours"] = round(elapsed_hours, 1)
        trigger["elapsed_time_str"] = self._format_elapsed_ko(elapsed_hours)
        
        return trigger

    def re_arm(self, trigger: Dict[str, Any], new_evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Restores confidence if new independent hard evidence is found.
        Only OFFICIAL, REGULATORY, or FILING families allow re-arm.
        """
        has_hard_evidence = False
        allowed_families = ["OFFICIAL", "REGULATORY", "FILINGS"]
        
        for e in new_evidence:
            family = e.get("family", "").upper()
            if family in allowed_families:
                has_hard_evidence = True
                break
        
        if has_hard_evidence:
            current_conf = trigger.get("current_confidence", 0)
            new_conf = min(100, current_conf + 30)
            trigger["current_confidence"] = new_conf
            # Re-determine state (can move UP)
            if new_conf >= 70:
                trigger["decay_state_internal"] = "ACTIVE"
            elif new_conf >= 40:
                trigger["decay_state_internal"] = "HOLD"
            else:
                trigger["decay_state_internal"] = "SILENT"
            
            trigger["decay_state_ko"] = self.STATE_KO[trigger["decay_state_internal"]]
            trigger["re_armed"] = True
            
        return trigger

    def _format_elapsed_ko(self, hours: float) -> str:
        if hours < 1:
            mins = int(hours * 60)
            return f"{mins}분 경과"
        elif hours < 24:
            return f"{int(hours)}시간 경과"
        else:
            days = int(hours / 24)
            rem_hours = int(hours % 24)
            return f"{days}일 {rem_hours}시간 경과"
