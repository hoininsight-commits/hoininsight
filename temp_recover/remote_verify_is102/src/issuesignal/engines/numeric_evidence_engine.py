from typing import List, Dict, Any
import json
from pathlib import Path
from src.collectors.financials.sec_financials_connector import SECFinancialsConnector

class NumericEvidenceEngine:
    """
    (IS-89) Numeric Evidence Engine.
    Attaches 'Numeric Evidence' (2 key numbers) to candidates if available.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.connector = SECFinancialsConnector(base_dir)

    def attach_evidence(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Iterates through candidates, checks if they relate to a known entity,
        and attaches numeric evidence.
        """
        enriched_candidates = []
        
        for cand in candidates:
            # Simple Entity Extraction (Heuristic: Check against known tickers in snapshot)
            # In production, use Named Entity Recognition (NER)
            ticker = self._extract_ticker(cand)
            
            if ticker:
                snapshot = self.connector.fetch_snapshot(ticker)
                if snapshot:
                    metrics = snapshot.get("metrics", [])
                    if metrics:
                         cand["numeric_evidence"] = metrics[:2] # Top 2 metrics
                         cand["numeric_source"] = snapshot.get("source_url", "Official Report")
                         # Register in source_mix
                         if "numeric" not in cand.get("source_mix", []):
                             cand["source_mix"] = cand.get("source_mix", []) + ["numeric"]
            
            enriched_candidates.append(cand)
            
        return enriched_candidates

    def _extract_ticker(self, candidate: Dict[str, Any]) -> str:
        """
        Heuristic extraction from theme/title.
        """
        text = candidate.get("theme", "") + " " + candidate.get("title", "")
        if "NVIDIA" in text.upper() or "NVDA" in text.upper(): return "NVDA"
        if "MICROSOFT" in text.upper() or "MSFT" in text.upper(): return "MSFT"
        if "SAMSUNG" in text.upper() or "삼성전자" in text.upper(): return "005930.KS"
        return ""
