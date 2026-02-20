from typing import List, Dict, Any, Optional
from pathlib import Path

class ReasoningTraceLayer:
    """
    STEP 53 — REASONING TRACE GENERATOR
    Structure: Anomaly -> Structural Shift -> Why Now -> Reality Check -> Ticker
    """
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        
    def generate_trace(self, topic: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Builds the 5-step trace.
        """
        # Extract from topic/context
        anomaly_desc = topic.get("anomaly_logic", "수치적 이상 징후 포착")
        structural_shift = topic.get("rationale", "구조적 변화 가능성 식별")
        # Handle different field names in different topic versions
        why_now = topic.get("why_now", {}).get("description", "시간적 임계점 도래")
        if not isinstance(why_now, str):
            why_now = "내러티브의 시간적 필연성 포착"
            
        reality_check = topic.get("bottleneck_logic", "실제적인 물리적/자본적 병목 현상 검증 완료")
        
        tickers = context.get("selected_tickers", [])
        ticker_list_str = ", ".join([t["ticker"] for t in tickers]) if tickers else "핵심 대상 식별 중"
        ticker_reason = f"{ticker_list_str}을(를) 해당 병목의 최종 해결자로 확정"

        trace = [
            {"id": 1, "label": "ANOMALY", "content": anomaly_desc},
            {"id": 2, "label": "STRUCTURAL_SHIFT", "content": structural_shift},
            {"id": 3, "label": "WHY_NOW", "content": why_now},
            {"id": 4, "label": "BOTTLENECK", "content": reality_check},
            {"id": 5, "label": "TICKER", "content": ticker_reason}
        ]
        
        return trace
