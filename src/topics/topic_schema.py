from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

REQUIRED = [
    "ts_utc",
    "dataset_id",
    "topic_id",
    "title",
    "score",
    "severity",
    "evidence",
    "rationale",
    "links",
]

@dataclass
class TopicV1:
    ts_utc: str
    dataset_id: str
    topic_id: str
    title: str
    score: float
    severity: str
    evidence: Dict[str, Any]
    rationale: str
    links: List[Dict[str, str]]

@dataclass
class TopicV2(TopicV1):
    narrative_score: float
    video_ready: bool
    causal_chain: Dict[str, Optional[str]]
    actor_tier_score: float
    cross_axis_count: int
    cross_axis_multiplier: float
    escalation_flag: bool

@dataclass
class TopicV3(TopicV2):
    conflict_flag: bool
    expectation_gap_score: int
    expectation_gap_level: str
    tension_multiplier_applied: bool
    final_narrative_score: float

def validate_topic_v1(obj: Dict[str, Any]) -> None:
    for k in REQUIRED:
        if k not in obj:
            raise ValueError(f"topic_v1 missing field: {k}")

def validate_topic_v2(obj: Dict[str, Any]) -> None:
    validate_topic_v1(obj)
    v2_fields = [
        "narrative_score", "video_ready", "causal_chain",
        "actor_tier_score", "cross_axis_count", 
        "cross_axis_multiplier", "escalation_flag"
    ]
    for k in v2_fields:
        if k not in obj:
            raise ValueError(f"topic_v2 missing field: {k}")

def validate_topic_v3(obj: Dict[str, Any]) -> None:
    validate_topic_v2(obj)
    v3_fields = [
        "conflict_flag", "expectation_gap_score", 
        "expectation_gap_level", "tension_multiplier_applied",
        "final_narrative_score"
    ]
    for k in v3_fields:
        if k not in obj:
            raise ValueError(f"topic_v3 missing field: {k}")
