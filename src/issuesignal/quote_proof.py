import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from .dashboard.models import DecisionCard, TriggerQuote
from .source_diversity import SourceDiversityEngine

class QuoteProofEngine:
    """
    (IS-31) Enforces official quote proof for triggers.
    Ensures that a signal is backed by verbatim official text.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def process_card(self, card: DecisionCard, artifacts: List[Dict[str, Any]]) -> Tuple[DecisionCard, List[str]]:
        """
        Assembles and verifies the trigger quote for a decision card.
        """
        logs = []
        quote = self._find_best_quote(card, artifacts)
        
        if not quote:
            card.trigger_quote = TriggerQuote(
                excerpt="No official quote found for this trigger.",
                source_kind="UNKNOWN",
                source_ref="-",
                verification_status="HOLD",
                reason_code="MISSING_QUOTE"
            )
            if card.status == "TRUST_LOCKED":
                card.status = "HOLD"
                card.reason = "MISSING_QUOTE_PROOF"
                logs.append("Status downgraded to HOLD: Missing official quote proof.")
        else:
            # Verification logic
            is_valid, reason, code = self._verify_quote(quote, artifacts)
            quote.verification_status = "PASS" if is_valid else ("REJECT" if "REJECT" in code else "HOLD")
            quote.reason_code = code
            card.trigger_quote = quote
            
            if code.startswith("REJECT"):
                card.status = "REJECT"
                card.reason = code
                logs.append(f"Issue REJECTED: {reason}")
            elif not is_valid:
                if card.status == "TRUST_LOCKED":
                    card.status = "HOLD"
                    card.reason = code
                    logs.append(f"Status downgraded to HOLD: {reason}")

        return card, logs

    def _find_best_quote(self, card: DecisionCard, artifacts: List[Dict[str, Any]]) -> Optional[TriggerQuote]:
        """
        Looks for candidate quotes in artifacts.
        """
        candidates = []
        for art in artifacts:
            # Look for trigger-level quotes
            if "trigger_quotes" in art:
                for q_data in art["trigger_quotes"]:
                    candidates.append(TriggerQuote(
                        excerpt=q_data.get("excerpt", ""),
                        source_kind=q_data.get("source_kind", "UNKNOWN"),
                        source_ref=q_data.get("source_ref", "-"),
                        source_date=q_data.get("source_date", "-"),
                        fact_type=q_data.get("fact_type", "OFFICIAL_STATEMENT")
                    ))
        
        # Sort by quality: OFFICIAL_TRANSCRIPT > OFFICIAL_STATEMENT > etc.
        priority = {
            "OFFICIAL_TRANSCRIPT": 3,
            "OFFICIAL_STATEMENT": 2,
            "POLICY_EXCERPT": 2,
            "CALENDAR_ITEM": 2,
            "SEC_FILING": 2,
            "REGULATORY_FILING": 2
        }
        
        if not candidates:
            return None
            
        candidates.sort(key=lambda x: priority.get(x.fact_type, 0), reverse=True)
        return candidates[0]

    def _verify_quote(self, quote: TriggerQuote, artifacts: List[Dict[str, Any]]) -> Tuple[bool, str, str]:
        """
        Applies IS-31 verification rules.
        """
        # Rule 1: Length
        if len(quote.excerpt) > 240 or len(quote.excerpt.splitlines()) > 2:
            return False, "Quote exceeds length limits (>240 chars or >2 lines).", "HOLD:LENGTH_EXCEEDED"

        diversity_engine = SourceDiversityEngine()
        
        # Rule 3: Independence / Cluster-based Diversity
        all_clusters = []
        all_kinds = []
        for art in artifacts:
            if "trigger_quotes" in art:
                for q in art["trigger_quotes"]:
                    q_text = q.get("excerpt", "")
                    cluster = diversity_engine.get_cluster(q.get("source_ref", ""), q_text, q.get("source_kind", "UNKNOWN"))
                    all_clusters.append(cluster.cluster_id)
                    all_kinds.append(cluster.cluster_type)

        unique_clusters = set(all_clusters)
        unique_kinds = set(all_kinds)
        
        # Assign cluster to current quote
        main_cluster = diversity_engine.get_cluster(quote.source_ref, quote.excerpt, quote.source_kind)
        quote.cluster_id = main_cluster.cluster_id

        # Non-independent (same cluster but multiple artifacts) - REJECT
        if len(unique_clusters) < 2 and len(all_clusters) >= 2:
            return False, "Circular reporting or wire chain detected.", "REJECT:WIRE_CHAIN_DUPLICATION"

        # Strong single source (OFFICIAL)
        if main_cluster.cluster_type == "OFFICIAL":
            return True, "PASS", "PASS"
            
        # MAJOR_MEDIA Diversity
        if len(unique_clusters) >= 2 and "MAJOR_MEDIA" in unique_kinds:
            return True, "PASS", "PASS"

        # Single news article check (simulated)
        if len(unique_clusters) == 1 and all_kinds[0] not in ["OFFICIAL"]:
            if "official said" in quote.excerpt.lower() or ("said" in quote.excerpt.lower() and "official" in quote.excerpt.lower()):
                 return False, "Single news article quoting 'official said' without link.", "HOLD:VAGUE_QUOTE"
            return False, "Single non-official source for quote.", "HOLD:SINGLE_SOURCE_RISK"

        return False, "Insufficient verification for quote.", "HOLD:MISSING_QUOTE"
