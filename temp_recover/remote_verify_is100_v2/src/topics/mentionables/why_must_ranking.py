"""
IS-97-5 Why-Must Ranking Layer
Deterministically ranks mentionable entities based on structural necessity (Bottleneck Logic).
"""
from typing import List, Dict, Any
import json
from pathlib import Path
from datetime import datetime
import yaml

class WhyMustRankingLayer:
    
    # Bottleneck Priority (Hardcoded "Pickaxe Logic")
    BOTTLENECK_PRIORITY = {
        "POWER_STORAGE": 1.0,  # Battery, ESS, Grid
        "COOLING": 1.0,         # Liquid Cooling
        "GRID_INFRA": 1.0,      # Transformers, Cables
        "SEMIS": 0.8,          # Chips (HBM, GPU)
        "PICKS_SHOVELS": 0.7,   # Equipment
        "HEDGE": 0.5,           # Gold, etc.
        "FINANCIAL": 0.4        # Banks
    }

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent.parent
        self.decision_dir = self.base_dir / "data" / "decision"
        self.registry_dir = self.base_dir / "registry"

    def calculate_bottleneck_score(self, role: str) -> float:
        """Factor A: Bottleneck Score (0.0 - 1.0)"""
        return self.BOTTLENECK_PRIORITY.get(role, 0.3)

    def calculate_timeline_score(self, unit: Dict[str, Any]) -> float:
        """Factor B: Timeline Proximity"""
        # If Hypothesis Jump is HOLD, apply penalty
        if unit.get("hypothesis_jump", {}).get("status") == "HOLD":
            return 0.2
        # Default ready state
        return 0.9

    def calculate_evidence_score(self, citations: List[str]) -> float:
        """Factor C: Evidence Strength"""
        if not citations: return 0.3
        
        score = 0.5
        for cit in citations:
            if "OFFICIAL" in cit or "STAT" in cit: score += 0.2
            elif "NEWS" in cit: score += 0.1
        return min(score, 1.0)

    def calculate_reliability_score(self, entity: Dict[str, Any]) -> float:
        """Factor D: Reliability (Stub mocked to 0.9 usually)"""
        # In real logic, check source_registry for entity link
        return 0.9 

    def calculate_cross_theme_score(self, entity_code: str, all_units: List[Dict]) -> float:
        """Factor E: Cross Theme Reuse"""
        count = 0
        # Placeholder logic: count occurrences across units (if mapped)
        # Here simplified to 0.5 base
        return 0.5

    def rank(self, mentionables: List[Dict], units: List[Dict], citations: Dict) -> Dict[str, Any]:
        
        ranked_items = []
        dropped_items = []
        
        # Build context map
        unit_map = {u.get("interpretation_key"): u for u in units}
        
        for item in mentionables:
            role = item.get("role", "UNKNOWN")
            code = item.get("code")
            
            # 1. Bottleneck Score
            b_score = self.calculate_bottleneck_score(role)
            
            # 2. Timeline (Context dependent)
            # Find relevant unit for this entity group (simplification: generic context)
            # In full impl, map entity->group->unit. Here use first active unit as proxy context
            active_unit = units[0] if units else {} 
            t_score = self.calculate_timeline_score(active_unit)
            
            # 3. Evidence
            ent_citations = citations.get(code, [])
            e_score = self.calculate_evidence_score(ent_citations)
            
            # 4. Reliability
            r_score = self.calculate_reliability_score(item)
            if r_score < 0.4:
                dropped_items.append({"entity": item.get("name"), "reason": "Low Reliability"})
                continue
                
            # 5. Cross Theme
            c_score = self.calculate_cross_theme_score(code, units)
            
            # FINAL FORMULA
            final = (0.35 * b_score) + (0.20 * t_score) + (0.20 * e_score) + (0.15 * r_score) + (0.10 * c_score)
            
            item["rank_signals"] = {
                "bottleneck_score": b_score,
                "timeline_proximity": t_score,
                "evidence_strength": e_score,
                "reliability": r_score,
                "cross_theme_reuse": c_score,
                "final_score": round(final, 3)
            }
            item["citations"] = ent_citations
            ranked_items.append(item)
            
        # Sort by final score desc
        ranked_items.sort(key=lambda x: x["rank_signals"]["final_score"], reverse=True)
        
        # Deduplication: Keep top item per Role, unless score gap is small
        # Simple Logic: Max 2 per role
        role_counts = {}
        final_list = []
        for item in ranked_items:
            role = item.get("role")
            role_counts[role] = role_counts.get(role, 0) + 1
            if role_counts[role] <= 2:
                # Add rank index
                item["rank"] = len(final_list) + 1
                final_list.append(item)
            else:
                dropped_items.append({"entity": item.get("name"), "reason": "Duplicate Role cap exceeded"})
        
        return {
            "as_of": datetime.now().strftime("%Y-%m-%d"),
            "top": final_list,
            "dropped": dropped_items
        }

    def process(self):
        # Load inputs
        try:
            m_path = self.decision_dir / "mentionables.json" # Assuming this exists or mocked
            u_path = self.decision_dir / "interpretation_units.json"
            
            mentionables = []
            if m_path.exists():
                mentionables = json.loads(m_path.read_text())
                
            units = []
            if u_path.exists():
                content = u_path.read_text()
                units = json.loads(content) if content.strip() else []
                if isinstance(units, dict): units = [units]
                
            # Mock citations if missing
            citations = {} 
            
            result = self.rank(mentionables, units, citations)
            
            # Save
            out_path = self.decision_dir / "mentionables_ranked.json"
            with open(out_path, "w") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
                
            print(f"[WHY-MUST] Ranked {len(result['top'])} items. Dropped {len(result['dropped'])}.")
            
        except Exception as e:
            print(f"[WHY-MUST] process error: {e}")

if __name__ == "__main__":
    layer = WhyMustRankingLayer()
    layer.process()
