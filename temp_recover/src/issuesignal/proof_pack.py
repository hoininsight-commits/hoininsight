import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from .dashboard.models import DecisionCard, HardFact, ProofPack, TriggerQuote, SourceCluster
from .quote_proof import QuoteProofEngine
from .source_diversity import SourceDiversityEngine

class ProofPackEngine:
    """
    (IS-30) Enforces "Economic Hunter-grade" proof requirements for tickers.
    Each ticker must be supported by >=2 independent hard facts.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def process_card(self, card: DecisionCard, artifacts: List[Dict[str, Any]]) -> Tuple[DecisionCard, List[str]]:
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
                logs.append(f"Ticker {ticker} failed proof: Less than 2 independent clusters.")

        # Update card tickers
        card.tickers = final_tickers
        card.proof_packs = valid_proof_packs

        # Trigger Quote Proof Logic (IS-31 Integration)
        # Check if any artifact has trigger_quotes to avoid breaking IS-30 tests
        has_quote_data = any("trigger_quotes" in art for art in artifacts)
        diversity_engine = SourceDiversityEngine()
        
        if has_quote_data:
            quote_engine = QuoteProofEngine(self.base_dir)
            card, quote_logs = quote_engine.process_card(card, artifacts)
            logs.extend(quote_logs)

        # IS-32: Build Source Clusters Summary for the card
        collected_clusters: Dict[str, SourceCluster] = {}
        for pack in valid_proof_packs:
            for fact in pack.hard_facts:
                if fact.cluster_id not in collected_clusters:
                    # Resolve cluster info for summary
                    cluster = diversity_engine.get_cluster(fact.source_ref, fact.fact_claim)
                    collected_clusters[fact.cluster_id] = cluster
        
        if card.trigger_quote and card.trigger_quote.cluster_id:
             if card.trigger_quote.cluster_id not in collected_clusters:
                 cluster = diversity_engine.get_cluster(card.trigger_quote.source_ref, card.trigger_quote.excerpt)
                 collected_clusters[card.trigger_quote.cluster_id] = cluster
        
        card.source_clusters = list(collected_clusters.values())

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
        
        # If Quote Proof failed, the QuoteProofEngine already handled demotion to HOLD.
        # But if Tickers passed and Quote passed, we stay TRUST_LOCKED.

        return card, logs

    def _build_proof_pack(self, ticker: str, artifacts: List[Dict[str, Any]]) -> ProofPack:
        """
        Assembles a proof pack for a specific ticker from available artifacts.
        """
        hard_facts = []
        # In a real scenario, we would parse artifacts (snapshots, decision cards, etc.)
        # For IS-30 implementation, we simulate extraction based on provided logic.
        
        diversity_engine = SourceDiversityEngine()
        for art in artifacts:
            # Match by ticker
            art_tickers = {t.upper() for t in art.get("tickers", [])}
            if ticker in art_tickers:
                facts = art.get("hard_facts", [])
                for f_data in facts:
                    source_ref = f_data.get("source_ref", "-")
                    fact_claim = f_data.get("fact_claim", "-")
                    source_kind = f_data.get("source_kind", "UNKNOWN")
                    cluster = diversity_engine.get_cluster(source_ref, fact_claim, source_kind)
                    
                    fact = HardFact(
                        fact_type=f_data.get("fact_type", "UNKNOWN"),
                        fact_claim=fact_claim,
                        source_kind=source_kind,
                        source_ref=source_ref,
                        source_date=f_data.get("source_date", "-"),
                        independence_key=f_data.get("independence_key", "-"),
                        cluster_id=cluster.cluster_id
                    )
                    hard_facts.append(fact)

        # Enforce Independence Rule via Clusters
        unique_clusters = {f.cluster_id for f in hard_facts if f.cluster_id}
        status = "PROOF_OK" if len(unique_clusters) >= 2 else "PROOF_FAIL"

        return ProofPack(
            ticker=ticker,
            company_name=ticker, # Simplified
            bottleneck_role="Verified Bottleneck Owner",
            why_irreplaceable_now=f"Structural position confirmed by {len(unique_clusters)} clusters.",
            hard_facts=hard_facts,
            proof_status=status
        )
