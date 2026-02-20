from pathlib import Path
from typing import List

class TriggerPriorityEngine:
    """
    (IS-8) Selects high-priority triggers and handles collisions.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        
    def evaluate_priorities(self, triggers: List[dict]) -> List[dict]:
        """
        Assigns READY/HOLD/REJECT state to each trigger.
        """
        if not triggers:
            return []
            
        # 1. Scoring
        scored_triggers = []
        for t in triggers:
            score = self._calculate_priority_score(t)
            t["priority_score"] = score
            scored_triggers.append(t)
            
        # 2. Sorting
        scored_triggers.sort(key=lambda x: x["priority_score"], reverse=True)
        
        # 3. Collision Resolution
        results = []
        for i, t in enumerate(scored_triggers):
            if i < 3 and t["priority_score"] > 50: # Max 3 READY
                t["status"] = "READY"
            else:
                t["status"] = "HOLD"
            results.append(t)
            
        # 4. Global Reject Check
        # If no trigger is strong enough, or they completely cancel each other out
        if all(t["priority_score"] < 40 for t in scored_triggers):
            for t in results: t["status"] = "REJECT"
            
        return results

    def _calculate_priority_score(self, trigger: dict) -> int:
        score = 50 # Base
        
        # Qualitative Boosters
        text = str(trigger).lower()
        
        # Capital Force
        if any(x in text for x in ["must", "force", "require", "mandatory"]):
            score += 20
            
        # Time Sensitivity
        if any(x in text for x in ["now", "immediate", "urgent", "today"]):
            score += 15
            
        # Linkage (Policy + Security + Finance)
        link_count = 0
        if "policy" in text: link_count += 1
        if "security" in text or "defense" in text: link_count += 1
        if "finance" in text or "capital" in text: link_count += 1
        
        score += (link_count * 5)
        
        return min(score, 100)
