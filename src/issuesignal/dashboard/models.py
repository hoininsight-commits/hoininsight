from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class DecisionCard:
    topic_id: str
    title: str
    status: str # TRUST_LOCKED, TRIGGER, PRE_TRIGGER, HOLD, REJECT, EDITORIAL_LIGHT
    one_liner: str = "-"
    trigger_type: str = "-"
    actor: str = "-"
    actor_type: str = "없음"
    actor_tag: str = "-"
    bottleneck_link: str = "-"
    ticker_path: Dict[str, Any] = field(default_factory=dict)
    bridge_info: Optional[Dict[str, Any]] = None
    decision_tree_data: List[Dict[str, Any]] = field(default_factory=list)
    must_item: str = "-"
    tickers: List[Dict[str, str]] = field(default_factory=list)
    kill_switch: str = "-"
    reason: str = "-"
    signature: Optional[str] = None
    # IS-30 Additions
    authority_sentence: str = "-"
    forced_capex: str = "-"
    bottleneck: str = "-"
    proof_packs: List['ProofPack'] = field(default_factory=list)
    # IS-31 Additions
    trigger_quote: Optional['TriggerQuote'] = None
    # IS-32 Additions
    source_clusters: List['SourceCluster'] = field(default_factory=list)
    # IS-50 Additions (Flexible Blocks)
    blocks: Dict[str, Any] = field(default_factory=dict)
    # IS-56 Operational Fields
    decision_rationale: str = "-"
    observed_metrics: List[str] = field(default_factory=list)
    leader_stocks: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    card_version: str = "v1"

@dataclass
class RejectLog:
    timestamp: str
    topic_id: str
    reason_code: str
    fact_text: str = "-"

@dataclass
class HardFact:
    fact_type: str # CONTRACT, REGULATION, etc.
    fact_claim: str
    source_kind: str # GOV, FILING, etc.
    source_ref: str
    source_date: str = "-"
    independence_key: str = "-"
    # IS-32 Additions
    cluster_id: str = "UNKNOWN"

@dataclass
class ProofPack:
    ticker: str
    company_name: str
    bottleneck_role: str
    why_irreplaceable_now: str
    hard_facts: List[HardFact] = field(default_factory=list)
    proof_status: str = "PROOF_FAIL" # PROOF_OK, PROOF_FAIL

@dataclass
class TriggerQuote:
    excerpt: str
    source_kind: str # GOV, FILING, etc.
    source_ref: str
    source_date: str = "-"
    fact_type: str = "OFFICIAL_STATEMENT"
    verification_status: str = "HOLD" # PASS, HOLD, REJECT
    reason_code: str = "MISSING_QUOTE"
    # IS-32 Additions
    cluster_id: str = "UNKNOWN"

@dataclass
class SourceCluster:
    cluster_id: str
    cluster_type: str # OFFICIAL, MAJOR_MEDIA, General, etc.
    origin_name: str
    reason: str = "-"

@dataclass
class HoinEvidenceItem:
    title: str
    summary: str
    date: str
    source_file: str
    bullets: List[str] = field(default_factory=list)
    tickers: List[str] = field(default_factory=list)
    topic_key: Optional[str] = None

@dataclass
class UnifiedLinkRow:
    issue_card: DecisionCard
    linked_evidence: List[HoinEvidenceItem] = field(default_factory=list)
    link_status: str = "NO_HOIN_EVIDENCE" # MATCHED, NO_HOIN_EVIDENCE
    match_reason: Optional[str] = None

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
    # IS-29 Additions
    hoin_evidence: List[HoinEvidenceItem] = field(default_factory=list)
    link_view: List[UnifiedLinkRow] = field(default_factory=list)
