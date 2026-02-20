from typing import List, Dict, Any, Optional
from pathlib import Path
import json

class TickerOccupancyLayer:
    """
    STEP 52 — TICKER OCCUPANCY MAP
    Rules:
    1. 1-3 Tickers per bottleneck.
    2. Revenue 50% Rule (Focus).
    3. Manufacturer-First Priority.
    """
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        # Mock Revenue Table for Rule Enforcement
        # ticker: (revenue_focus_score 0-1.0, is_manufacturer bool)
        self.revenue_kb = {
            "TSM": (1.0, True),
            "ASML": (0.95, True),
            "NVDA": (0.85, True),
            "AMD": (0.80, True),
            "INTC": (0.75, True),
            "MU": (1.0, True),
            "AMAT": (0.90, True),
            "LRCX": (0.95, True),
            "AAPL": (0.45, False), # Fails 50% Rule for specific bottleneck usually, but is a leader
            "MSFT": (0.35, False),
            "GOOGL": (0.30, False),
            "META": (0.90, False), # Ads focus
            "TSLA": (0.85, True),
            "Samsung": (0.40, True), # Exception: Market Leader
            "SK Hynix": (1.0, True),
        }
        
    def select_tickers(self, candidates: List[str], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Main logic for Step 52.
        """
        # 1. Scoring & Filtering
        scored_candidates = []
        for ticker in candidates:
            score_data = self.revenue_kb.get(ticker, (0.5, False)) # Default to 50% if unknown
            revenue_focus, is_manufacturer = score_data
            
            # Rule: Revenue 50% Rule
            # Exception: Market Leader (Samsung example)
            is_leader = ticker == "Samsung"
            
            if revenue_focus < 0.5 and not is_leader:
                continue
                
            # Rule: Manufacturer-First (Adds to priority score)
            priority_score = revenue_focus
            if is_manufacturer:
                priority_score += 0.5 # Boost for manufacturers
                
            scored_candidates.append({
                "ticker": ticker,
                "priority_score": priority_score,
                "revenue_focus": revenue_focus,
                "is_manufacturer": is_manufacturer,
                "logic_role": "OWNER" if is_manufacturer else "BENEFICIARY"
            })
            
        # 2. Sorting
        # Primary: Priority Score (Revenue + Manufacturer Boost)
        # Secondary: Alphabetical
        scored_candidates.sort(key=lambda x: (x["priority_score"], x["ticker"]), reverse=True)
        
        # 3. Truncating (1-3 Tickers)
        final_list = scored_candidates[:3]
        
        # 4. Final Formatting
        results = []
        for x in final_list:
            results.append({
                "ticker": x["ticker"],
                "logic_role": x["logic_role"],
                "revenue_focus": x["revenue_focus"],
                "rationale": self._generate_rationale(x, context)
            })
            
        return results

    def _generate_rationale(self, item: Dict[str, Any], context: Dict[str, Any]) -> str:
        ticker = item["ticker"]
        role = item["logic_role"]
        is_manu = item["is_manufacturer"]
        
        if role == "OWNER":
            return f"{ticker}은(는) 해당 병목 기술을 직접 소유하고 제조하는 원천 기업으로서, 공급망의 핵심 키를 쥐고 있습니다."
        elif is_manu:
            return f"{ticker}은(는) 핵심 공정의 지배적 제조사로서, 이번 구조적 변화의 직접적인 실적 수혜가 예상됩니다."
        else:
            return f"{ticker}은(는) 매출 비중은 낮으나 해당 섹터의 지배적 리더로서, 구조적 재편의 방향성을 결정하는 주체입니다."
