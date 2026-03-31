from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger("BottleneckRanker")

# SCORING CONSTANTS
BASE_SCORE = 50

TYPE_BONUS = {
    "ACQUISITION": 20,       # Assets/IP control -> High Exclusivity
    "AGREEMENT": 10,         # Contract -> Moderate
    "FINANCIAL_OBLIGATION": -10, # Debt/Bond -> Defensive
    "TERMINATION": -20       # Loss of control
}

KEYWORD_BONUS = {
    "exclusive": 15,    # Monopoly
    "sole": 15,         # Monopoly
    "global": 10,       # Scale
    "worldwide": 10,    # Scale
    "patent": 10,       # IP Moat
    "intellectual property": 10,
    "supply": 5,        # Value Chain
    "strategic": 5,     # Long-term
    "definitive": 5     # Binding
}

MIN_SCORE_THRESHOLD = 75
MAX_PROTAGONISTS = 2

class BottleneckRanker:
    """
    Ranks Corporate Action Facts to identify 'Protagonists'
    who control the structural bottleneck of the sector.
    """
    
    @staticmethod
    def rank_protagonists(facts: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Input: List of Corporate Facts (IS-59 format)
        Output: {
            "protagonists": [Top 1-2 facts > 70 score],
            "supporting": [Rest]
        }
        """
        if not facts:
            return {"protagonists": [], "supporting": []}
            
        ranked_items = []
        
        for fact in facts:
            score = BASE_SCORE
            details = fact.get("details", {})
            raw_summary = details.get("raw_summary", "").lower()
            fact_text = fact.get("fact_text", "").lower()
            
            # 1. Type Bonus
            action_type = details.get("action_type", "UNKNOWN")
            score += TYPE_BONUS.get(action_type, 0)
            
            # 2. Keyword Bonus
            # Check both summary and text
            combined_text = f"{fact_text} {raw_summary}"
            
            matched_keywords = []
            for kw, bonus in KEYWORD_BONUS.items():
                if kw in combined_text:
                    score += bonus
                    matched_keywords.append(kw)
            
            # Cap at 100
            score = min(score, 100)
            
            # Generate "Why" Reasoning
            # e.g. "독점적 공급 계약(Exclusive)을 통해 섹터 내 대체 불가능한 지위를 확보했습니다."
            if matched_keywords:
                key_reasons = ", ".join([k.upper() for k in matched_keywords[:2]])
                reasoning = f"핵심 키워드({key_reasons})가 포함된 {action_type} 행동으로 구조적 장악력이 높습니다."
            else:
                reasoning = f"{action_type} 행동을 통해 시장 내 입지를 강화하고 있습니다."
                
            # Add metadata
            ranked_item = fact.copy()
            ranked_item["bottleneck_score"] = score
            ranked_item["bottleneck_reason"] = reasoning
            ranked_items.append(ranked_item)
            
        # Sort by Score Desc
        ranked_items.sort(key=lambda x: x["bottleneck_score"], reverse=True)
        
        # Select Protagonists
        protagonists = []
        supporting = []
        
        for item in ranked_items:
            if len(protagonists) < MAX_PROTAGONISTS and item["bottleneck_score"] >= MIN_SCORE_THRESHOLD:
                protagonists.append(item)
            else:
                supporting.append(item)
                
        logger.info(f"Bottleneck Analysis: {len(protagonists)} protagonists found out of {len(facts)} facts.")
        return {
            "protagonists": protagonists,
            "supporting": supporting
        }
