import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List

class RelationshipBreakInterpreter:
    """
    IS-96-8: Relationship Break Interpreter
    Converts relationship stress data into interpretation units.
    """

    def __init__(self, base_dir: Path = Path(".")):
        self.base_dir = base_dir
        self.input_path = self.base_dir / "data" / "decision" / "relationship_stress.json"
        self.output_dir = self.base_dir / "data" / "decision"
        self.output_file = self.output_dir / "interpretation_units.json"

    def interpret(self):
        if not self.input_path.exists():
            print("[INTERPRETER] relationship_stress.json missing. Skipping.")
            return
        
        data = json.loads(self.input_path.read_text(encoding="utf-8"))
        relationships = data.get("relationships", [])
        
        # Load existing units
        units = []
        if self.output_file.exists():
            try:
                content = self.output_file.read_text(encoding="utf-8")
                units = json.loads(content) if content.strip() else []
            except:
                units = []
        
        # Remove existing REL_STRESS entries for today
        units = [u for u in units if not (u.get("interpretation_key") == "RELATIONSHIP_BREAK_RISK" and u.get("as_of_date") == datetime.now().strftime("%Y-%m-%d"))]

        new_units = []
        for rel in relationships:
            if rel["break_risk"] in ["HIGH", "MED"]:
                # Check for MED with potential Hypothesis Jump
                # We need reliability again
                ev_count = len(rel["evidence"])
                avg_rel = sum(e["reliability"] for e in rel["evidence"]) / ev_count if ev_count > 0 else 0
                
                is_high = rel["break_risk"] == "HIGH"
                is_med_hypo = (rel["break_risk"] == "MED" and avg_rel < 0.7)
                
                status = "READY" if is_high else "HOLD"
                
                unit_id = f"IS-96-{datetime.now().strftime('%Y%m%d')}-{rel['entity_a'][:4]}-{rel['entity_b'][:4]}"
                
                unit = {
                    "interpretation_id": unit_id,
                    "as_of_date": datetime.now().strftime("%Y-%m-%d"),
                    "target_sector": "STRATEGIC_ALLIANCE",
                    "interpretation_key": "RELATIONSHIP_BREAK_RISK",
                    "theme": "RELATIONSHIP_BREAK_RISK",
                    "confidence_score": rel["stress_score"],
                    "evidence_tags": [e["title"] for e in rel["evidence"]],
                    "structural_narrative": f"{rel['entity_a']}와 {rel['entity_b']} 사이의 {rel['relationship_type']} 관계에서 구조적 균열 신호가 감지되었습니다. (Stress Score: {rel['stress_score']})",
                    "derived_metrics_snapshot": {
                        "stress_score": rel["stress_score"],
                        "signals": rel["signals"],
                        "break_risk": rel["break_risk"],
                        "reliability": avg_rel
                    },
                    "hypothesis_jump": {
                        "status": status,
                        "trigger_reason": f"Relationship Stress ({rel['break_risk']})",
                        "independent_sources_count": ev_count
                    },
                    "why_now": rel["why_now"],
                    "checklist_3": [
                        "confirm_source_2plus (n>=2 independent sources)",
                        "confirm_capital_link_change",
                        "confirm_supplier_switch_signals"
                    ],
                    "risk_3": [
                        "rumor risk",
                        "negotiation reversal",
                        "timing uncertainty"
                    ],
                    "evidence_refs": [e["source_id"] for e in rel["evidence"]]
                }
                new_units.append(unit)

        units.extend(new_units)
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        with open(self.output_file, "w", encoding="utf-8") as f:
            json.dump(units, f, indent=2, ensure_ascii=False)
            
        print(f"[INTERPRETER] Relationship Break Analysis: Emitted {len(new_units)} units.")

if __name__ == "__main__":
    i = RelationshipBreakInterpreter()
    i.interpret()
