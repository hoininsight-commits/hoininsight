from datetime import datetime
from pathlib import Path

class SpeechTriggerEngine:
    """
    (IS-7) Detects pre-event triggers from speech, tone, or narrative shifts.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        
    def analyze_speech(self, source: str, text: str, meta: dict = None) -> dict:
        """
        Detects SPEECH_SHIFT triggers.
        """
        # 1. Detection Logic (Mock implementation)
        # In production, this would use NLP/LLM for intensity, timing, and focus analysis.
        
        intensity_shift = self._check_intensity_shift(text)
        timing_abnormality = meta.get("timing_abnormality", False) if meta else False
        focus_shift = self._check_focus_shift(text)
        
        is_trigger = intensity_shift or timing_abnormality or focus_shift
        
        if not is_trigger:
            return {"status": "NONE", "trigger_type": None}
            
        # 2. Generate Output
        why_now = f"Recent statement from {source} shows a significant shift in {self._get_shift_reason(intensity_shift, focus_shift)}."
        ignore_impossible = f"The statement directly impacts {self._get_impact_area(text)} which is a core liquidity bottleneck."
        
        return {
            "status": "TRIGGERED",
            "trigger_type": "SPEECH_SHIFT",
            "source": source,
            "why_now": why_now,
            "ignore_reason": ignore_impossible,
            "timestamp": datetime.utcnow().isoformat()
        }

    def _check_intensity_shift(self, text: str) -> bool:
        # Heuristic: Check for "high intensity" keywords
        intensity_keywords = ["concerned", "critical", "urgent", "active", "significant"]
        return any(kw in text.lower() for kw in intensity_keywords)

    def _check_focus_shift(self, text: str) -> bool:
        # Heuristic: Check for new focus topics
        focus_keywords = ["employment", "labor", "geopolitical", "supply chain"]
        return any(kw in text.lower() for kw in focus_keywords)

    def _get_shift_reason(self, intensity, focus) -> str:
        if intensity and focus: return "narrative intensity and focus"
        if intensity: return "narrative intensity"
        return "focus shift"

    def _get_impact_area(self, text: str) -> str:
        if "rate" in text.lower() or "fed" in text.lower():
            return "rate path expectations"
        if "china" in text.lower() or "tariff" in text.lower():
            return "geopolitical trade structure"
        return "market liquidity structure"
