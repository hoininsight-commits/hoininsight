import json
from pathlib import Path
from typing import Any, Dict, List
from src.topics.gate.speakability_gate import SpeakabilityGate
from src.topics.narrator.narrative_skeleton import NarrativeSkeletonBuilder

class DecisionAssembler:
    """
    IS-96-4: Decision Output Assembly Layer
    Aggregates Interpretation, Speakability, and Narrative Skeleton into unified assets.
    """

    def __init__(self, output_dir: str = "data/decision"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.gate = SpeakabilityGate()
        self.skeleton_builder = NarrativeSkeletonBuilder()

    def assemble(self, interpretation_units: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Processes a list of interpretation units through the gated pipeline.
        """
        speakability_decisions = {}
        narrative_skeletons = {}
        
        for unit in interpretation_units:
            unit_id = unit.get("interpretation_id", "unknown")
            
            # 1. Evaluate Speakability
            decision = self.gate.evaluate(unit)
            speakability_decisions[unit_id] = decision
            
            # 2. Build Narrative Skeleton
            skeleton = self.skeleton_builder.build(unit, decision)
            narrative_skeletons[unit_id] = skeleton
            
        results = {
            "interpretation_units": interpretation_units,
            "speakability_decision": speakability_decisions,
            "narrative_skeleton": narrative_skeletons
        }
        
        return results

    def save(self, results: Dict[str, Any]):
        """
        Persists results to individual JSON files.
        """
        file_map = {
            "interpretation_units.json": results["interpretation_units"],
            "speakability_decision.json": results["speakability_decision"],
            "narrative_skeleton.json": results["narrative_skeleton"]
        }
        
        for filename, data in file_map.items():
            out_path = self.output_dir / filename
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"[OK] Saved to {out_path}")

def run_decision_assembly(interpretation_units: List[Dict[str, Any]], output_dir: str = "data/decision"):
    assembler = DecisionAssembler(output_dir)
    results = assembler.assemble(interpretation_units)
    assembler.save(results)
    return results
