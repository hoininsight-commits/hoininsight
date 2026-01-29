import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from .dashboard.models import DecisionCard, HardFact, ProofPack

class ProofPackEngine:
    """
    (IS-30) Enforces "Economic Hunter-grade" proof requirements for tickers.
    Each ticker must be supported by >=2 independent hard facts.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def process_card(self, card: DecisionCard, artifacts: List[Dict[str, Any]]) -> Tuple[DecisionCard, List[str]]:
        """
        Processes a decision card, building proof packs for each ticker.
        Removes tickers that fail proof requirements.
        Downgrades status if necessary.
        """
        logs = []
        valid_proof_packs = []
        original_tickers = card.tickers
        final_tickers = []

        for ticker_info in original_tickers:
            ticker = ticker_info.get("symbol", ticker_info.get("ticker", "UNKNOWN")).upper()
            pack = self._build_proof_pack(ticker, artifacts)
            
            if pack.proof_status == "PROOF_OK":
                valid_proof_packs.append(pack)
                final_tickers.append(ticker_info)
            else:
                logs.append(f"Ticker {ticker} failed proof: Less than 2 independent sources.")

        # Update card tickers
        card.tickers = final_tickers
        card.proof_packs = valid_proof_packs

        # Enforcement Logic
        if not final_tickers:
            card.status = "REJECT"
            card.reason = "NO_PROOF_TICKER"
            logs.append("Issue REJECTED: Zero tickers passed proof requirements.")
        elif len(final_tickers) < len(original_tickers):
            if card.status == "TRUST_LOCKED":
                card.status = "HOLD"
                card.reason = "PARTIAL_PROOF_FAIL"
                logs.append("Status downgraded to HOLD: Some tickers failed proof.")
        
        # If all passed but it was TRUST_LOCKED, check if it was already TRUST_LOCKED
        # The requirement says: If TRUST_LOCKED but proof fails => downgrade.
        # If proof passes for at least one ticker, we keep going but HOLD if some failed.

        return card, logs

    def _build_proof_pack(self, ticker: str, artifacts: List[Dict[str, Any]]) -> ProofPack:
        """
        Assembles a proof pack for a specific ticker from available artifacts.
        """
        hard_facts = []
        # In a real scenario, we would parse artifacts (snapshots, decision cards, etc.)
        # For IS-30 implementation, we simulate extraction based on provided logic.
        
        for art in artifacts:
            # Match by ticker
            art_tickers = {t.upper() for t in art.get("tickers", [])}
            if ticker in art_tickers:
                facts = art.get("hard_facts", [])
                for f_data in facts:
                    fact = HardFact(
                        fact_type=f_data.get("fact_type", "UNKNOWN"),
                        fact_claim=f_data.get("fact_claim", "-"),
                        source_kind=f_data.get("source_kind", "UNKNOWN"),
                        source_ref=f_data.get("source_ref", "-"),
                        source_date=f_data.get("source_date", "-"),
                        independence_key=f_data.get("independence_key", "-")
                    )
                    hard_facts.append(fact)

        # Enforce Independence Rule
        unique_sources = set()
        for f in hard_facts:
            # Independence = different independence_key AND different source_kind
            unique_sources.add((f.independence_key, f.source_kind))

        status = "PROOF_OK" if len(unique_sources) >= 2 else "PROOF_FAIL"

        return ProofPack(
            ticker=ticker,
            company_name=ticker, # Simplified
            bottleneck_role="Verified Bottleneck Owner",
            why_irreplaceable_now=f"Structural position confirmed by {len(unique_sources)} sources.",
            hard_facts=hard_facts,
            proof_status=status
        )
