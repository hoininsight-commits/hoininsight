from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class DecisionCard:
    topic_id: str
    title: str
    status: str # TRUST_LOCKED, TRIGGER, PRE_TRIGGER, HOLD, REJECT
    one_liner: str = "-"
    trigger_type: str = "-"
    actor: str = "-"
    must_item: str = "-"
    tickers: List[Dict[str, str]] = field(default_factory=list)
    kill_switch: str = "-"
    reason: str = "-"
    signature: Optional[str] = None

@dataclass
class RejectLog:
    timestamp: str
    topic_id: str
    reason_code: str
    fact_text: str = "-"

@dataclass
class TimelinePoint:
    date: str
    counts: Dict[str, int] # status -> count

@dataclass
class DashboardSummary:
    date: str
    engine_status: str # SUCCESS, FAIL, WARNING
    counts: Dict[str, int] # TRUST_LOCKED, TRIGGER, etc.
    top_cards: List[DecisionCard] = field(default_factory=list)
    watchlist: List[DecisionCard] = field(default_factory=list)
    hold_queue: List[DecisionCard] = field(default_factory=list)
    reject_logs: List[RejectLog] = field(default_factory=list)
    timeline: List[TimelinePoint] = field(default_factory=list)
