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
    final_score: float

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
    rank_features: RankFeatures = field(default_factory=lambda: RankFeatures(0,0,0,0,0))

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
