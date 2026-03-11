
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum
import json

class ConfidenceLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

@dataclass
class NarrativeTopic:
    topic_anchor: str
    narrative_driver: str
    trigger_event: str
    core_narrative: str
    intent_signals: List[str]
    structural_hint: str
    era_fit: str
    confidence_level: ConfidenceLevel
    risk_note: str
    disclaimer: str = "This is a NARRATIVE TOPIC (Short-term Story). NOT A STRUCTURAL TOPIC."
    
    def to_dict(self):
        return {
            "topic_anchor": self.topic_anchor,
            "narrative_driver": self.narrative_driver,
            "trigger_event": self.trigger_event,
            "core_narrative": self.core_narrative,
            "intent_signals": self.intent_signals,
            "structural_hint": self.structural_hint,
            "era_fit": self.era_fit,
            "confidence_level": self.confidence_level.value,
            "risk_note": self.risk_note,
            "disclaimer": self.disclaimer
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            topic_anchor=data.get("topic_anchor", ""),
            narrative_driver=data.get("narrative_driver", ""),
            trigger_event=data.get("trigger_event", ""),
            core_narrative=data.get("core_narrative", ""),
            intent_signals=data.get("intent_signals", []),
            structural_hint=data.get("structural_hint", ""),
            era_fit=data.get("era_fit", ""),
            confidence_level=ConfidenceLevel(data.get("confidence_level", "LOW")),
            risk_note=data.get("risk_note", "")
        )

    def to_markdown(self):
        return f"""
[NARRATIVE_TOPIC]
- Topic Anchor: {self.topic_anchor}
- Narrative Driver: {self.narrative_driver}
- Trigger Event: {self.trigger_event}
- Core Narrative: {self.core_narrative}
- Intent Signals: {', '.join(self.intent_signals)}
- Structural Hint: {self.structural_hint}
- Era Fit: {self.era_fit}
- Confidence Level: {self.confidence_level.value}
- Risk Note: {self.risk_note}
- Disclaimer: {self.disclaimer}
"""
