from __future__ import annotations

import re
from typing import Dict, Any, List

class ProposalScorer:
    """
    Phase 32: Proposal Prioritization & Alignment Scoring Engine.
    Calculates alignment scores based on Hoin Insight Constitution.
    """
    
    def __init__(self, definition_index: dict = None):
        self.definitions = definition_index or {}
        
        # Scoring Weights (Fixed)
        self.weights = {
            "definition_alignment": 0.40,
            "evidence_strength": 0.25,
            "regime_consistency": 0.20,
            "impact_scope": 0.15
        }
    
    def calculate_score(self, proposal_text: str, regime_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate specific score components and total weighted score (0-100).
        """
        text = proposal_text.lower()
        
        # 1. Definition Alignment (40%)
        # Does the proposal reference core definition concepts?
        def_terms = [
            "data collection master", "anomaly detection logic", "baseline signals",
            "metric", "indicator", "threshold", "additive", "expansion", "dataset"
        ]
        def_hits = sum(1 for term in def_terms if term in text)
        # Cap at 5 hits = 100%
        s1 = min(def_hits * 20, 100)
        
        # 2. Evidence Strength (25%)
        # Does it have strong evidence markers?
        # Heuristic: Length, structured sections, numbers
        vocab_strong = ["observed", "repeated", "pattern", "correlation", "multiple sources", "confirmed"]
        vocab_hits = sum(1 for v in vocab_strong if v in text)
        
        # Length check (if very short, low score)
        length_score = min(len(text) / 500 * 50, 50) # Max 50 pts for length
        vocab_score = min(vocab_hits * 10, 50) # Max 50 pts for vocab
        s2 = length_score + vocab_score
        
        # 3. Regime Consistency (20%)
        # Matches current regime context?
        regime_name = str(regime_info.get("regime", "")).lower()
        confidence = regime_info.get("confidence", "LOW")
        
        s3 = 50.0 # Base score
        if regime_name and regime_name != "unknown":
            # Split regime name keywords
            keywords = [k for k in regime_name.split() if len(k) > 3]
            match_count = sum(1 for k in keywords if k in text)
            if match_count > 0:
                s3 += 30
            else:
                s3 -= 10
                
        if confidence == "HIGH":
            s3 += 20
        elif confidence == "MEDIUM":
            s3 += 10
            
        s3 = max(0, min(100, s3))
        
        # 4. Impact Scope (15%)
        # Global/Structural vs Local
        s4 = 50.0
        if "global" in text or "structural" in text or "macro" in text:
            s4 += 40
        elif "sector" in text or "specific" in text:
            s4 += 20
            
        if "temporary" in text or "noise" in text:
            s4 -= 20
            
        s4 = max(0, min(100, s4))
        
        # Final Calculation
        total_score = (
            s1 * self.weights["definition_alignment"] +
            s2 * self.weights["evidence_strength"] +
            s3 * self.weights["regime_consistency"] +
            s4 * self.weights["impact_scope"]
        )
        
        breakdown = [
            f"Def({s1:.0f})",
            f"Evid({s2:.0f})",
            f"Regime({s3:.0f})",
            f"Impact({s4:.0f})"
        ]
        
        return {
            "alignment_score": round(total_score, 1),
            "score_breakdown": " | ".join(breakdown),
            "components": {
                "definition": s1,
                "evidence": s2,
                "regime": s3,
                "impact": s4
            }
        }
