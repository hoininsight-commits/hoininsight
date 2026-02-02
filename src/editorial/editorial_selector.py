from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from pathlib import Path

class DailyEditorialSelector:
    """
    (IS-87) Daily Editorial Selector.
    Selects top 1-2 narrative candidates based on 'Editor Score'.
    Enforces the 'Editor' role to choose what to say.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def select(self, candidates: List[Dict[str, Any]], context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Selects top candidates.
        
        Input:
         - candidates: List of Narrative Candidates (IS-86)
         - context: Optional context (like today.json data)
         
        Output:
         - List of selected picking dicts (with rank, score, rationale).
        """
        scored_candidates = []
        
        for cand in candidates:
            score, rationale = self._calculate_score(cand)
            cand_copy = cand.copy()
            cand_copy["editor_score"] = score
            cand_copy["editor_rationale"] = rationale
            scored_candidates.append(cand_copy)
            
        # Sort by score desc
        scored_candidates.sort(key=lambda x: x["editor_score"], reverse=True)
        
        if not scored_candidates:
            return []
            
        # Selection Logic (Top 1-2)
        picks = []
        
        # Rank 1
        top1 = scored_candidates[0]
        top1["selected_rank"] = 1
        picks.append(top1)
        
        # Rank 2 Condition: Score >= 90% of Top 1 AND Different Type
        if len(scored_candidates) > 1:
            top2 = scored_candidates[1]
            if top2["editor_score"] >= (top1["editor_score"] * 0.9):
                if top2["dominant_type"] != top1["dominant_type"]:
                    top2["selected_rank"] = 2
                    picks.append(top2)
                    
        return picks

    def _calculate_score(self, candidate: Dict[str, Any]) -> (int, str):
        """
        Calculates Editor Score based on IS-87 rules.
        """
        score = 50 # Base
        rationales = []
        
        # 1. Timeliness / Urgency
        hints = candidate.get("promotion_hint", "")
        # Assuming Tone is passed or inferred via hints or fusion logic
        # For IS-87 MVP, we use promotion_hint as proxy for impact/urgency if tone missing
        if "DAILY" in hints: 
            score += 15
            rationales.append("Daily Relevance")
            
        # 2. Why Now (Check for Why-Now panel existence/keyword)
        why_now = candidate.get("why_now", "")
        if "시점" in why_now or "지금" in why_now:
            score += 15
            rationales.append("Strong Why-Now")
            
        # 3. Fusion Depth
        source_mix = candidate.get("source_mix", [])
        if len(source_mix) >= 2:
            score += 10
            rationales.append("Multi-Signal Fusion")

        # 4. Structure Continuity
        # Mock check for IS-71 bridge (If theme mentions '구조')
        if "구조" in candidate.get("theme", ""):
            score += 15
            rationales.append("Structural Bridge")
            
        # Penalties
        # No penalty logic in mock context without proof checking yet, assume validated by Fusion Engine
        
        rationale_text = " / ".join(rationales)
        return score, rationale_text
