#!/usr/bin/env python3
"""
Phase 27: Structural Probability Compression Layer v1.0
=======================================================
Synthesizes structural signals into a market compression state.
Adheres to the NO-BEHAVIOR-CHANGE principle.
"""

import json
import logging
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("ProbabilityCompression")

# Constants
ROOT = Path(__file__).resolve().parent.parent.parent
DATA_OPS = ROOT / "data" / "ops"
DOCS_DECISION = ROOT / "docs" / "data" / "decision"
OUTPUT_JSON = DATA_OPS / "probability_compression_state.json"
OUTPUT_MD = DATA_OPS / "probability_compression_brief.md"

class StructuralProbabilityCompressionLayer:
    def __init__(self):
        DATA_OPS.mkdir(parents=True, exist_ok=True)

    def _load_json(self, path: Path) -> dict:
        if not path.exists():
            logger.warning(f"File not found: {path}")
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            logger.error(f"Error loading {path}: {e}")
            return {}

    def execute(self):
        logger.info("Running Structural Probability Compression Layer v1.0...")

        # 1. Load Inputs
        regime_data = self._load_json(DATA_OPS / "regime_state.json")
        os_data = self._load_json(DATA_OPS / "investment_os_state.json")
        capital_data = self._load_json(DATA_OPS / "capital_allocation_state.json")
        timing_data = self._load_json(DATA_OPS / "timing_state.json")
        conflict_data = self._load_json(DATA_OPS / "conflict_density_pack.json")
        video_pool = self._load_json(DATA_OPS / "video_candidate_pool.json")
        today_data = self._load_json(DOCS_DECISION / "today.json")

        # 2. Extract Features
        regime_state = regime_data.get("regime", {}).get("liquidity_state", "UNKNOWN")
        timing_gear = timing_data.get("timing_gear", {}).get("level", 1)
        capital_mode = capital_data.get("allocation_profile", {}).get("mode", "NEUTRAL_BALANCED")
        conflict_density = len(conflict_data.get("topics", []))
        video_candidates = len(video_pool.get("top_candidates", []))
        
        top_topics = today_data.get("top_topics", []) if isinstance(today_data, dict) else (today_data if isinstance(today_data, list) else [])
        max_intensity = 0
        if top_topics:
            intensities = [t.get("intensity", 0) for t in top_topics if isinstance(t, dict)]
            max_intensity = max(intensities) if intensities else 0

        # 3. Compression Logic (Mapping Based)
        direction = "NEUTRAL_COMPRESSION"
        pressure = "MODERATE"
        stability = "TRANSITION"
        
        # Rule set
        if regime_state == "TIGHTENING":
            direction = "DOWNWARD_BIAS"
            if timing_gear >= 4 or conflict_density >= 10:
                pressure = "HIGH"
                stability = "FRAGILE"
            else:
                pressure = "MODERATE"
                stability = "TRANSITION"
        elif regime_state == "EASING":
            direction = "UPWARD_BIAS"
            if timing_gear >= 3:
                pressure = "HIGH"
                stability = "STABLE"
            else:
                pressure = "MODERATE"
                stability = "TRANSITION"
        else:
            direction = "NEUTRAL_COMPRESSION"
            pressure = "LOW" if timing_gear <= 2 else "MODERATE"
            stability = "STABLE" if timing_gear <= 2 else "TRANSITION"

        # 4. Scenario Tree & Decision Compression
        scenario = {
            "primary_path": "Defensive Rotation 지속" if direction == "DOWNWARD_BIAS" else ("Structural Growth 동조화" if direction == "UPWARD_BIAS" else "횡보 및 축 정렬"),
            "secondary_path": "Volatility Expansion" if direction == "DOWNWARD_BIAS" else ("Mini-Bubble 형성" if direction == "UPWARD_BIAS" else "개별 종목 장세"),
            "invalidator": "Regime 완화 전환" if direction == "DOWNWARD_BIAS" else ("금리 급등 및 유동성 위축" if direction == "UPWARD_BIAS" else "Axis 이탈")
        }
        
        decision = {
            "operator_posture": "Cautious Expansion" if direction == "DOWNWARD_BIAS" else ("Aggressive Alignment" if direction == "UPWARD_BIAS" else "Wait & See"),
            "risk_band": "NARROW" if pressure == "HIGH" else "NORMAL",
            "conviction_state": "Conditional" if stability == "FRAGILE" else "Strong"
        }

        # 5. Build Drivers
        drivers = [
            {"type": "Regime", "impact": f"Liquidity {regime_state}"},
            {"type": "Timing", "impact": f"Gear {timing_gear} Acceleration" if timing_gear >= 3 else f"Gear {timing_gear} IDLE"},
            {"type": "Conflict", "impact": "High Density" if conflict_density >= 10 else "Normal Density"}
        ]

        # 6. Construct State
        kst_now = datetime.now(timezone.utc) + timedelta(hours=9)
        state = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "date_kst": kst_now.strftime("%Y-%m-%d"),
            "regime_state": regime_state,
            "timing_gear": timing_gear,
            "capital_mode": capital_mode,
            "compression_state": {
                "direction": direction,
                "pressure_level": pressure,
                "stability": stability
            },
            "drivers": drivers,
            "scenario_tree": scenario,
            "decision_compression": decision
        }

        # 7. Save Outputs
        OUTPUT_JSON.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info(f"Generated {OUTPUT_JSON}")

        self._generate_brief(state)
        logger.info(f"Generated {OUTPUT_MD}")

    def _generate_brief(self, state: dict):
        comp = state["compression_state"]
        tree = state["scenario_tree"]
        decision = state["decision_compression"]
        
        md = f"""# Structural Probability Compression Brief ({state['date_kst']})

## Compression State: **{comp['direction']}**
- **Pressure Level**: {comp['pressure_level']}
- **Stability**: {comp['stability']}

## Scenario Tree
- **Primary Path**: {tree['primary_path']}
- **Secondary Path**: {tree['secondary_path']}
- **Invalidator**: {tree['invalidator']}

## Decision Compression
- **Operator Posture**: {decision['operator_posture']}
- **Risk Band**: {decision['risk_band']}
- **Conviction State**: {decision['conviction_state']}

## Key Drivers
{chr(10).join([f"- **{d['type']}**: {d['impact']}" for d in state['drivers']])}
"""
        OUTPUT_MD.write_text(md, encoding="utf-8")

if __name__ == "__main__":
    StructuralProbabilityCompressionLayer().execute()
