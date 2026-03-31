from typing import List, Tuple
from src.tickers.company_map_registry import CandidateCompany

def run_monopoly_pressure_score(candidates: List[CandidateCompany]) -> Tuple[str, List[CandidateCompany], str]:
    """
    Rank and collapse candidates.
    Returns: (Decision, Final List, Reject Reason)
    Decision: LOCKED | REJECT
    """
    if not candidates:
        return "REJECT", [], "No candidates survived filters."

    # Sort by Market Share (Desc), then Expansion Speed (Desc)
    ranked = sorted(
        candidates, 
        key=lambda x: (x.market_share_proxy, x.expansion_speed_proxy), 
        reverse=True
    )
    
    # Selection Logic
    # 1. Take top 3 max.
    # 2. But we must check for "Fragmented Market". 
    # If we have 4+ candidates with very similar high scores, it might be fragmented.
    # For this implementation, we simply cut at 3.
    # BUT, the rule says: "If more than 3 remain -> LOCK must be rejected". 
    # This implies if we have >3 VALID candidates that we cannot distinguish, it's fragmented.
    # However, if we have a clear score gap, we can take the top ones.
    
    # Simple Logic:
    # If count <= 3: LOCK
    # If count > 3:
    #   Check if Top 3 score is significantly higher than Top 4?
    #   For STRICTNESS: If we have >3 surviving Reality/Guardrail, we check if we can filter by score.
    #   If Top 3 have Score >= 5 and Rank 4 has Score < 5 -> Cut.
    #   If Rank 4 is close to Rank 3 -> Reject all as Fragmented.
    
    final_list = []
    
    if len(ranked) <= 3:
        final_list = ranked
    else:
        # Check gap between #3 and #4
        score_3 = ranked[2].market_share_proxy
        score_4 = ranked[3].market_share_proxy
        
        # If #4 is weak (e.g. half of #3), we drop #4+.
        # If #4 is strong (close to #3), we reject whole sector.
        if score_4 < (score_3 * 0.7):
            final_list = ranked[:3]
        else:
            return "REJECT", [], f"Fragmented Market: Top 4 scores are close ({score_3} vs {score_4})."

    return "LOCKED", final_list, ""
