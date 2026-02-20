from __future__ import annotations
from typing import Dict, Any, List, Tuple
from datetime import datetime

TIER_A_PUBLISHERS = {
    "Fed", "SEC", "ECB", "BOJ", "Bank of Korea", "Department of Justice",
    "EU Commission", "Federal Register", "Official Gazette", "SEC EDGAR",
    "Korea Exchange", "KRX", "DART", "Companies House", "National Gazette"
}

TIER_B_PUBLISHERS = {
    "Reuters", "Bloomberg", "Financial Times", "Wall Street Journal",
    "CNBC", "Nikkei", "Yonhap News"
}

HIGH_RISK_TYPES = {"regulation", "contract", "legal"}

def classify_tier(source: Dict[str, Any] | Any) -> str:
    publisher = ""
    if isinstance(source, dict):
        publisher = source.get("publisher", "")
    else:
        publisher = getattr(source, "publisher", "")
    
    if any(p.lower() in publisher.lower() for p in TIER_A_PUBLISHERS):
        return "A"
    if any(p.lower() in publisher.lower() for p in TIER_B_PUBLISHERS):
        return "B"
    return "C"

def score_event(event: Dict[str, Any] | Any, as_of_date: str) -> Tuple[float, bool, str]:
    """
    Returns (trust_score, requires_confirmation, trust_tier)
    """
    # Normalize event to dict for scoring logic if it's an object
    if not isinstance(event, dict):
        e_dict = {
            "event_type": getattr(event, "event_type", ""),
            "source": getattr(event, "source", {}),
            "effective_window": getattr(event, "effective_window", {}),
            "evidence": getattr(event, "evidence", []),
            "sources": getattr(event, "sources", None) # optional multi-source
        }
    else:
        e_dict = event

    source = e_dict.get("source", {})
    tier = classify_tier(source)
    score = 0.5 # Base

    # 1) Tier Bonus
    if tier == "A": score += 0.4
    elif tier == "B": score += 0.2

    # 2) Timing
    window = e_dict.get("effective_window", {})
    start_date = ""
    if isinstance(window, dict):
        start_date = window.get("start_date", "")
    else:
        start_date = getattr(window, "start_date", "")
    
    if start_date == as_of_date:
        score += 0.1 # Just released today

    # 3) Evidence Richness
    evidence = e_dict.get("evidence", [])
    if len(evidence) >= 1:
        score += 0.1
    if len(evidence) >= 3:
        score += 0.1

    # 4) Cross-source / Confirmation Logic
    sources = e_dict.get("sources", None)
    tierA_count = 1 if tier == "A" else 0
    tierB_count = 1 if tier == "B" else 0
    
    if isinstance(sources, list):
        tierA_count = sum(1 for s in sources if classify_tier(s) == "A")
        tierB_count = sum(1 for s in sources if classify_tier(s) == "B")
        # Multi-source bonus
        if tierA_count >= 2: score += 0.2
        elif tierB_count >= 2: score += 0.1

    requires_confirmation = False

    # Speech-only heuristic: policy/geopolitics without evidence from non-Tier A
    if e_dict.get("event_type") in {"policy", "geopolitics"} and len(evidence) == 0 and tier != "A":
        requires_confirmation = True

    # High-risk types require cross-source (Tier A or at least 2 Tier B)
    if e_dict.get("event_type") in HIGH_RISK_TYPES:
        if not (tierA_count >= 1 or tierB_count >= 2):
            requires_confirmation = True

    # Clamp
    score = max(0.0, min(1.0, score))
    return score, requires_confirmation, tier
