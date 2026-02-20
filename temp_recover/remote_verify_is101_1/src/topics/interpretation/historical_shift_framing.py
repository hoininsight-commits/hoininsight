"""
IS-96-6 Historical Shift Framing Layer
Deterministically upgrades interpretations into "Historical Regime Shift" narratives.
"""
from typing import List, Dict, Any, Optional
import json
from pathlib import Path
from datetime import datetime

class HistoricalShiftFramer:
    # Trigger Configuration: Thesis Key -> Shift Definition
    SHIFT_DEFINITIONS = {
        "LABOR_MARKET_SHIFT": {
            "shift_type": "LABOR_MARKET_REGIME_SHIFT",
            "historical_claim": "This is not a trend; it is the collapse of a decades-old equilibrium between Capital and Labor.",
            "what_changed": [
                "Degree Premium (White Collar) is eroding vs Body Sovereignty (Blue Collar)",
                "Cognitive tasks are deflationary; Physical tasks are inflationary"
            ],
            "why_it_matters_now": [
                "The first time in history technology replaces the middle-class first",
                "Physical infrastructure constraints necessitate high-wage manual labor"
            ],
            "what_breaks_next": [
                "Higher Education tuition models",
                "White-collar entry-level hiring pipeline"
            ]
        },
        "AI_INDUSTRIALIZATION": {
            "shift_type": "INDUSTRIAL_REVOLUTION_PHASE_SHIFT",
            "historical_claim": "We are moving from the 'Software Era' (Zero Marginal Cost) to the 'Industrial AI Era' (High CapEx cost).",
            "what_changed": [
                "Compute is no longer abstract; it is energy and steel",
                "The primary constraint has shifted from code to physics (Power, Cooling)"
            ],
            "why_it_matters_now": [
                "Big Tech CapEx has decoupled from immediate revenue",
                "National grids cannot support the projected load without reform"
            ],
            "what_breaks_next": [
                "Grid stability in localized tech hubs",
                "Legacy SaaS valuation multiples"
            ]
        },
        "INFRASTRUCTURE_SUPERCYCLE": {
            "shift_type": "CAPEX_CYCLE_INVERSION",
            "historical_claim": "The era of 'Capital Light' growth is over; the era of 'Heavy Asset' dominance has begun.",
            "what_changed": [
                "Interest rates are no longer zero, yet physical CAPEX is accelerating",
                "The physical world is re-pricing higher relative to the digital world"
            ],
            "why_it_matters_now": [
                "Supply chains physically cannot scale at the speed of software demand",
                "Real assets (Copper, Transformers) are the new bottlenecks"
            ],
            "what_breaks_next": [
                "JIT (Just-in-Time) supply chain models",
                "Utility pricing structures"
            ]
        },
        # Add other definitions as needed...
    }

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent.parent
        self.input_dir = self.base_dir / "data" / "decision"
        self.output_dir = self.input_dir

    def check_conditions(self, unit: Dict[str, Any]) -> bool:
        """
        Deterministic Trigger Rules:
        1. Context Key must match a defined SHIFT_DEFINITION
        2. Severity/Confidence must be high (>= 0.8) OR be a valid Hypothesis Jump
        """
        key = unit.get("interpretation_key")
        if key not in self.SHIFT_DEFINITIONS:
            return False
            
        # Condition A: Hypothesis Jump Ready
        if unit.get("hypothesis_jump", {}).get("status") == "READY":
            return True
            
        # Condition B: High Confidence
        if unit.get("confidence_score", 0) >= 0.8:
            return True
            
        return False

    def generate_frame(self, unit: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not self.check_conditions(unit):
            return None
        
        key = unit.get("interpretation_key")
        defn = self.SHIFT_DEFINITIONS[key]
        
        # Construct Frame
        return {
            "target_sector": unit.get("target_sector"),
            "interpretation_key": key,
            "shift_type": defn["shift_type"],
            "historical_claim": defn["historical_claim"],
            "what_changed": defn["what_changed"],
            "why_it_matters_now": defn["why_it_matters_now"],
            "what_breaks_next": defn["what_breaks_next"],
            "generated_at": datetime.now().isoformat()
        }

    def process(self):
        input_path = self.input_dir / "interpretation_units.json"
        if not input_path.exists():
            print("[SHIFT_FRAMER] No input file found.")
            return
            
        try:
            content = input_path.read_text()
            units = json.loads(content) if content.strip() else []
            if isinstance(units, dict): units = [units]
        except Exception as e:
            print(f"[SHIFT_FRAMER] Error reading input: {e}")
            return
        
        # Find first matching shift (Priority Winner)
        frame = None
        for unit in units:
            frame = self.generate_frame(unit)
            if frame:
                break # Single strongest narrative framing for now
        
        # Save output
        output_path = self.output_dir / "historical_shift_frame.json"
        if frame:
            with open(output_path, "w") as f:
                json.dump(frame, f, indent=2, ensure_ascii=False)
            print(f"[SHIFT_FRAMER] Generated frame for {frame['interpretation_key']}")
        else:
            # If no frame triggered, remove stale file to prevent confusion
            if output_path.exists():
                output_path.unlink()
            print("[SHIFT_FRAMER] No shift conditions met.")

if __name__ == "__main__":
    framer = HistoricalShiftFramer()
    framer.process()
