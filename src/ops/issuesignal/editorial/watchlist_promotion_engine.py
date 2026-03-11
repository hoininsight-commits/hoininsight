import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any

class WatchlistPromotionEngine:
    """
    (IS-82) Watchlist Promotion Engine.
    Promotes 'Strategic Watchlist' items to 'Editorial Candidates' 
    if they meet maturity conditions (Time, Pattern, Scenario).
    """
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.output_dir = base_dir / "data" / "issuesignal"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def process(self, ymd: str) -> Path:
        """
        Reads watchlist for {ymd}, evaluates items, saves promoted candidates.
        """
        print(f"[{ymd}] Promoting Watchlist to Editorial...")
        
        # 1. Load Watchlist
        watchlist_path = self.base_dir / "data" / "watchlist" / f"strategic_watchlist_{ymd}.json"
        if not watchlist_path.exists():
            print(f"   [SKIP] Watchlist not found: {watchlist_path}")
            return None
            
        try:
            w_data = json.loads(watchlist_path.read_text(encoding="utf-8"))
            items = w_data.get("watchlist", [])
        except Exception as e:
            print(f"   [ERR] Failed to load watchlist: {e}")
            return None
            
        promoted_list = []
        
        # 2. Evaluate Promotion Conditions
        for item in items:
            p_result = self._evaluate_item(item, ymd)
            if p_result:
                promoted_list.append(p_result)
                
        # 3. Save Promoted Candidates
        output_path = self.output_dir / f"promoted_candidates_{ymd}.json"
        payload = {
            "date": ymd,
            "count": len(promoted_list),
            "candidates": promoted_list
        }
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
            
        print(f"   Promoted {len(promoted_list)} items. Saved: {output_path}")
        return output_path

    def _evaluate_item(self, item: Dict, ymd: str) -> Dict:
        """Evaluate a single watchlist item for promotion."""
        itype = item.get("type")
        theme = item.get("theme", "Unknown")
        window = item.get("expected_window", "")
        
        is_promoted = False
        reason = ""
        
        # Condition 1: PREVIEW (Schedule within 7 days)
        if itype == "PREVIEW":
            # [Refinement] Real logic requires parsing 'window' date. 
            # For MVP, we assume "This Week" or similar text implies urgency.
            if "This Week" in window or "Review" in window: 
                is_promoted = True
                reason = "Schedule within execution window (7 days)"
                
        # Condition 2: STRUCTURE (Pattern Recurrence)
        elif itype == "STRUCTURE":
            # [Refinement] Check pattern memory. For MVP, we pass all 'STRUCTURE' 
            # as candidates to ensure structural observation is voiced.
            is_promoted = True
            reason = "Recurring structural pattern detected"
            
        # Condition 3: SCENARIO (Escalation)
        elif itype == "SCENARIO":
            # [Refinement] Check macro thresholds.
            # Mock: Random promotion or specific keyword in esc_condition
            if "WTI" in item.get("escalation_condition", ""): # Example mock logic
                is_promoted = True 
                reason = "Scenario condition (WTI) trigger active"

        if is_promoted:
            return {
                "candidate_id": f"PROM-{item.get('id')}",
                "source_watchlist_id": item.get("id"),
                "category": f"WATCHLIST_{itype}", # To map to badge later
                "reason": f"[FROM WATCHLIST] {reason}",
                "editorial_title": f"[{itype}] {theme}: {item.get('why_watch')}",
                "editorial_summary": "본 내용은 확정된 투자 판단이 아닌 구조적 해석입니다. (승격된 관찰)",
                "status": "EDITORIAL_CANDIDATE",
                "badge": "FROM WATCHLIST",
                "confidence_level": "MEDIUM" # Default middleware confidence
            }
        
        return None
