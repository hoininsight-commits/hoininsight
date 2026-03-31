from typing import List, Dict, Any
from pathlib import Path
from src.collectors.market.price_performance_connector import PricePerformanceConnector
from src.collectors.market.valuation_snapshot_connector import ValuationSnapshotConnector

class RelativeReratingEngine:
    """
    (IS-90) Relative Re-rating Engine.
    Generates 'Relative Re-rating Card' thesis based on performance gap and valuation.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.price_conn = PricePerformanceConnector(base_dir)
        self.val_conn = ValuationSnapshotConnector(base_dir)

    def attach_relative_card(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Attaches 'Relative Card' to candidates.
        """
        for cand in candidates:
            # Heuristic Ticker Extraction (Same as IS-89, should centralize this later)
            ticker = self._extract_ticker(cand)
            if not ticker: continue
            
            # Determine Peer Group (Mock logic for MVP)
            peer_group = "S&P500"
            if ticker in ["NVDA", "MSFT"]: peer_group = "BigTech"
            if ticker == "005930.KS": peer_group = "GlobalSemi"
            
            # Fetch Data
            price_data = self.price_conn.fetch_relative_perf(ticker, peer_group)
            val_data = self.val_conn.fetch_valuation(ticker)
            
            if price_data:
                # Generate Thesis
                gap = price_data.get("gap_1y", "+0%")
                is_outperforming = "+" in gap
                
                thesis = ""
                if is_outperforming:
                    thesis = f"{peer_group} 대비 {gap} 초과수익, 밸류에이션 부담 점검 필요"
                else:
                    thesis = f"{peer_group} 대비 {gap} 소외, 키맞추기(Re-rating) 가능성 주목"
                
                cand["relative_card"] = {
                    "peer_group": peer_group,
                    "perf_gap_1y": gap,
                    "valuation_band": val_data.get("current_fwd_pe", "N/A"),
                    "avg_pe": val_data.get("avg_5y_pe", "N/A"),
                    "rerate_thesis": thesis,
                    "risk_anchor": "금리 변동성 확대 시 멀티플 축소 위험" # Default Risk
                }
                
                # Check for IS-90 logic: If HARD_FACT present (which it is if data exists), allow STRUCTURE/SCENARIO
                # This is handled by Fusion/Editorial Selector mostly via score boosting
                cand["source_mix"] = cand.get("source_mix", []) + ["relative"]

        return candidates

    def _extract_ticker(self, candidate: Dict[str, Any]) -> str:
        text = candidate.get("theme", "") + " " + candidate.get("title", "")
        if "NVIDIA" in text.upper() or "NVDA" in text.upper(): return "NVDA"
        if "MICROSOFT" in text.upper() or "MSFT" in text.upper(): return "MSFT"
        if "SAMSUNG" in text.upper() or "삼성전자" in text.upper(): return "005930.KS"
        return ""
