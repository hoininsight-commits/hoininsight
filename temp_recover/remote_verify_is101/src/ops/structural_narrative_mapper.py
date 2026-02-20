from __future__ import annotations
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

class StructuralNarrativeMapper:
    """
    Converts raw FACT ANCHORS into STRUCTURAL NARRATIVE FRAMES.
    Deterministic mapping only, no subjective judgment.
    """
    
    FRAME_ENUM = [
        "CAPITAL_REALLOCATION",
        "POLICY_SHIFT",
        "TECH_INFLECTION",
        "SUPPLY_CHAIN_RECONFIG",
        "REGULATORY_OPTIONALITY",
        "COST_STRUCTURE_CHANGE",
        "DEMAND_REACCELERATION",
        "STRATEGIC_DEPENDENCY"
      ]

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def map_fact(self, fact: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Maps a single fact to 0-N structural frames.
        """
        fact_type = fact.get("fact_type", "").upper()
        fact_text = fact.get("fact_text", "").lower()
        entities = [e.lower() for e in fact.get("entities", [])]
        
        frames = []
        
        # Mapping Rules (Deterministic)
        
        # 1. CAPITAL_REALLOCATION
        if fact_type == "BUDGET" or "investment" in fact_text or "funding" in fact_text or "capital" in fact_text:
            frames.append({
                "frame": "CAPITAL_REALLOCATION",
                "reason": f"Fact mentions {fact_type}/investment related to {', '.join(entities)}."
            })
            
        # 2. POLICY_SHIFT
        if fact_type == "POLICY" or "regulation" in fact_text or "guideline" in fact_text:
             frames.append({
                "frame": "POLICY_SHIFT",
                "reason": f"Official {fact_type} document addresses {', '.join(entities)} framework."
            })
            
        # 3. TECH_INFLECTION
        if fact_type == "TECH" or "innovation" in fact_text or "architecture" in fact_text or "material" in fact_text:
            frames.append({
                "frame": "TECH_INFLECTION",
                "reason": f"Technical update for {', '.join(entities)} indicates architecture shift."
            })
            
        # 4. SUPPLY_CHAIN_RECONFIG
        if "supply chain" in fact_text or "logistics" in fact_text or "production" in fact_text:
            frames.append({
                "frame": "SUPPLY_CHAIN_RECONFIG",
                "reason": f"Chain dynamics for {', '.join(entities)} are reconfigured per fact text."
            })

        # 5. REGULATORY_OPTIONALITY
        if "legal" in fact_text or "court" in fact_text or "compliance" in fact_text:
            frames.append({
                "frame": "REGULATORY_OPTIONALITY",
                "reason": f"Legal status of {', '.join(entities)} changes the regulatory path."
            })

        # 6. COST_STRUCTURE_CHANGE
        if "cost" in fact_text or "operating" in fact_text or "margin" in fact_text:
             frames.append({
                "frame": "COST_STRUCTURE_CHANGE",
                "reason": f"Fact details cost or operational changes for {', '.join(entities)}."
            })

        # 7. DEMAND_REACCELERATION
        if "order" in fact_text or "demand" in fact_text or "consumer" in fact_text:
            frames.append({
                "frame": "DEMAND_REACCELERATION",
                "reason": f"Market demand signals for {', '.join(entities)} are updated."
            })

        # 8. STRATEGIC_DEPENDENCY
        if "defense" in fact_text or "energy" in fact_text or "dependency" in fact_text or "sovereign" in fact_text:
            frames.append({
                "frame": "STRATEGIC_DEPENDENCY",
                "reason": f"Fact text highlights sovereignty or dependency for {', '.join(entities)}."
            })

        return frames

    def enrich_facts(self, facts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enriches a list of facts with structural frames.
        """
        for fact in facts:
            fact["structural_frames"] = self.map_fact(fact)
        return facts

if __name__ == "__main__":
    # Test
    mapper = StructuralNarrativeMapper(Path("."))
    mock_fact = {
        "fact_type": "POLICY",
        "fact_text": "New regulation on AI chip exports",
        "entities": ["AI", "Exports"]
    }
    print(json.dumps(mapper.map_fact(mock_fact), indent=2))
