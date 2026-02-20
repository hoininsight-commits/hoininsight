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

def validate_topic_v1(obj: Dict[str, Any]) -> None:
    for k in REQUIRED:
        if k not in obj:
            raise ValueError(f"topic_v1 missing field: {k}")
