from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Union

Confidence = Literal["LOW", "MEDIUM", "HIGH"]
Category = Literal["earnings", "guidance", "rotation", "policy", "geopolitics", "flows", "valuation", "macro", "other"]

@dataclass
class NumberItem:
    label: str
    value: Union[float, int, str]
    unit: str

@dataclass
class RankFeatures:
    hook_score: float
    number_score: float
    timeliness_score: float
    explainability_score: float
    evidence_quality_score: float = 0.0 # Added for event triggers
    final_score: float = 0.0

@dataclass
class Candidate:
    candidate_id: str
    as_of_date: str
    question: str
    category: Category
    hook_signals: List[str] = field(default_factory=list)
    evidence_refs: List[str] = field(default_factory=list)
    numbers: List[NumberItem] = field(default_factory=list)
    confidence: Confidence = "LOW"
    requires_confirmation: bool = False # Added for source trust filtering
    rank_features: RankFeatures = field(default_factory=lambda: RankFeatures(0,0,0,0,0,0))

@dataclass
class DecisionEvidence:
    key: str
    value: Any
    expected_baseline: Optional[Any] = None
    source: str = "N/A"
    timestamp: str = ""
    confidence: float = 1.0

@dataclass
class DecisionTrace:
    trigger_name: str
    triggered: bool
    reasons: List[str] = field(default_factory=list)
    evidence: List[DecisionEvidence] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SpeakEligibility:
    eligible: bool = False
    triggers: List[str] = field(default_factory=list)
    summary: str = ""
    trace: Dict[str, DecisionTrace] = field(default_factory=dict)
    anchors: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class GateOutput:
    as_of_date: str
    topic_id: str
    title: str
    question: str
    why_people_confused: str
    key_reasons: List[str]
    numbers: List[NumberItem]
    risk_one: str
    confidence: Confidence
    handoff_to_structural: bool
    handoff_reason: str
    source_candidates: List[str]
    speak_eligibility: SpeakEligibility = field(default_factory=SpeakEligibility)
