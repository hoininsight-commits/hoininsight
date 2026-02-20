from __future__ import annotations
from dataclasses import dataclass
from typing import List, Literal, Union

EventType = Literal["earnings", "policy", "regulation", "contract", "geopolitics", "macro_release", "flow"]

@dataclass
class EventSource:
    publisher: str
    url: str

@dataclass
class EffectiveWindow:
    start_date: str
    end_date: str

@dataclass
class EventEvidence:
    label: str
    value: Union[float, int, str]
    unit: str
    context: str = ""

@dataclass
class GateEvent:
    event_id: str
    event_type: EventType
    title: str
    source: EventSource
    effective_window: EffectiveWindow
    evidence: List[EventEvidence]
    # Trust fields (Added)
    trust_score: float = 0.5
    requires_confirmation: bool = False
    trust_tier: str = "C"

@dataclass
class GateEventsPayload:
    schema_version: str
    as_of_date: str
    events: List[GateEvent]
