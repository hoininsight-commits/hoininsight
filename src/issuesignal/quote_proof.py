import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from .dashboard.models import DecisionCard, TriggerQuote

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
            
            if code == "REJECT:NON_INDEPENDENT":
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

        # Rule 2: Strength
        if quote.fact_type == "OFFICIAL_TRANSCRIPT":
            # For transcript, we ideally want to see context, but we check presence of source_ref
            if quote.source_ref != "-":
                return True, "PASS", "PASS"

        # Check for independent sources if not strong enough
        all_refs = []
        all_kinds = []
        for art in artifacts:
            if "trigger_quotes" in art:
                for q in art["trigger_quotes"]:
                    if q.get("excerpt") == quote.excerpt:
                        all_refs.append(q.get("source_ref"))
                        all_kinds.append(q.get("source_kind"))

        # Rule 3: Independence / Repetitive Source Check
        unique_refs = set(all_refs)
        unique_kinds = set(all_kinds)
        
        # Non-independent (same kind and ref but different artifacts) - Check this FIRST
        if len(unique_refs) < 2 and len(all_refs) >= 2:
            return False, "Two articles citing same press release.", "REJECT:NON_INDEPENDENT"

        # Strong single source
        if quote.source_kind in ["GOV", "REGULATOR", "COURT"]:
            return True, "PASS", "PASS"
            
        # Single news article check (simulated)
        if len(unique_refs) == 1 and all_kinds[0] not in ["GOV", "REGULATOR", "COURT"]:
            if "official said" in quote.excerpt.lower() or ("said" in quote.excerpt.lower() and "official" in quote.excerpt.lower()):
                 return False, "Single news article quoting 'official said' without link.", "HOLD:VAGUE_QUOTE"
            return False, "Single non-official source for quote.", "HOLD:SINGLE_SOURCE_RISK"

        if len(unique_refs) >= 2 and len(unique_kinds) >= 2:
            return True, "PASS", "PASS"

        return False, "Insufficient verification for quote.", "HOLD:MISSING_QUOTE"
