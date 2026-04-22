from typing import List, Dict

class TopicSelector:
    """[TASK #100.6] 최종 점수 계산 및 토픽 선정"""

    def __init__(self):
        pass

    def select(self, candidates: List[Dict], evaluations: List[Dict]) -> Dict:
        # Create lookup for evaluations
        eval_map = {e["candidate_id"]: e for e in evaluations}
        
        scored_candidates = []
        for cand in candidates:
            c_id = cand["candidate_id"]
            ev = eval_map.get(c_id)
            if not ev or ev.get("topic_decision") == "DROP":
                continue
                
            # Formula from TASK #100 Section 6
            # Part 1: Deterministic Scores (0-1 range)
            det_score = (cand.get("recency_score", 0) + cand.get("breadth_score", 0) + cand.get("evidence_score", 0)) / 3.0
            
            # Part 2: LLM Scores (0-10 range)
            llm_score = (ev.get("topic_fit_score", 0) + ev.get("market_impact_score", 0) + ev.get("contentability_score", 0)) / 3.0
            
            # Weighted average
            final_score = (det_score * 0.5) + (llm_score * 0.5)
            
            cand["final_score"] = round(final_score, 4)
            cand["evaluation"] = ev
            scored_candidates.append(cand)
            
        # Sort by score
        scored_candidates.sort(key=lambda x: x["final_score"], reverse=True)
        
        selection = {
            "MAIN": scored_candidates[0] if scored_candidates else None,
            "SECONDARY": scored_candidates[1:3] if len(scored_candidates) > 1 else [],
            "EARLY": [c for c in scored_candidates[3:] if c["candidate_type"] == "EVENT"][:2]
        }
        
        return selection
