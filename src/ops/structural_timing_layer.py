#!/usr/bin/env python3
"""
Phase 26: Structural Timing Layer v1.0
=====================================
Interprets market rhythm and defines 'Timing Gears' (Level 1-5).
Adheres to the NO-BEHAVIOR-CHANGE principle.
"""

import json
import logging
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("StructuralTiming")

# Constants
ROOT = Path(__file__).resolve().parent.parent.parent
DATA_OPS = ROOT / "data" / "ops"
DOCS_DECISION = ROOT / "docs" / "data" / "decision"
OUTPUT_JSON = DATA_OPS / "timing_state.json"
OUTPUT_MD = DATA_OPS / "timing_brief.md"

class StructuralTimingLayer:
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
        logger.info("Running Structural Timing Layer v1.0...")

        # 1. Load Inputs
        regime_data = self._load_json(DATA_OPS / "regime_state.json")
        os_data = self._load_json(DATA_OPS / "investment_os_state.json")
        capital_data = self._load_json(DATA_OPS / "capital_allocation_state.json")
        conflict_data = self._load_json(DATA_OPS / "conflict_density_pack.json")
        video_pool = self._load_json(DATA_OPS / "video_candidate_pool.json")
        today_data = self._load_json(DOCS_DECISION / "today.json")

        # 2. Extract Features for Timing
        regime_state = regime_data.get("regime", {}).get("liquidity_state", "UNKNOWN")
        os_stance = os_data.get("os_summary", {}).get("stance", "NEUTRAL")
        capital_mode = capital_data.get("allocation_profile", {}).get("mode", "NEUTRAL_BALANCED")
        
        conflict_density = len(conflict_data.get("topics", []))
        video_candidates = len(video_pool.get("top_candidates", []))
        
        # Today's signal strength (intensity)
        top_topics = today_data.get("top_topics", []) if isinstance(today_data, dict) else (today_data if isinstance(today_data, list) else [])
        max_intensity = 0
        if top_topics:
            intensities = [t.get("intensity", 0) for t in top_topics if isinstance(t, dict)]
            max_intensity = max(intensities) if intensities else 0

        # 3. Timing Gear Logic (Simple Mapping)
        # Level 1: IDLE
        # Level 2: LOW_MOMENTUM
        # Level 3: BUILDING
        # Level 4: HIGH_PRESSURE
        # Level 5: BREAKOUT
        
        level = 2
        label = "LOW_MOMENTUM"
        desc = "구조는 명확하나 속도는 제한적"
        
        if video_candidates == 0 and max_intensity < 40:
            level = 1
            label = "IDLE"
            desc = "구조적 시그널 부재로 인한 대기 상태"
        elif conflict_density >= 10 and max_intensity >= 70:
            level = 4
            label = "HIGH_PRESSURE"
            desc = "구조적 충돌 및 임계 강도 도달 (가속 구간)"
            if video_candidates >= 3:
                level = 5
                label = "BREAKOUT"
                desc = "다축 동조화 및 구조적 폭발 구간"
        elif max_intensity >= 50 or video_candidates > 0:
            level = 3
            label = "BUILDING"
            desc = "축 정합성 강화 및 모멘텀 형성 구간"
            
        # 4. Synchronization Status
        sync = {
            "axis_alignment": "STRONG" if max_intensity >= 60 else ("PARTIAL" if max_intensity >= 30 else "WEAK"),
            "conflict_pressure": "HIGH" if conflict_density >= 10 else ("MODERATE" if conflict_density >= 5 else "LOW"),
            "narrative_velocity": "ACCELERATING" if video_candidates >= 2 else "STABLE"
        }

        # 5. Construct State
        kst_now = datetime.now(timezone.utc) + timedelta(hours=9)
        state = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "date_kst": kst_now.strftime("%Y-%m-%d"),
            "regime_state": regime_state,
            "os_stance": os_stance,
            "capital_mode": capital_mode,
            "timing_gear": {
                "level": level,
                "label": label,
                "description": desc
            },
            "synchronization": sync,
            "acceleration_watch": [
                "동일 축 지표 2개 이상 동시 강도 상승",
                "Conflict Density 급증",
                "Regime 전환 시그널 발생"
            ],
            "deceleration_warning": [
                "Video 후보 0건 지속",
                "Axis 정합도 약화",
                "내러티브 강도 급락"
            ]
        }

        # 6. Save Outputs
        OUTPUT_JSON.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info(f"Generated {OUTPUT_JSON}")

        self._generate_brief(state)
        logger.info(f"Generated {OUTPUT_MD}")

    def _generate_brief(self, state: dict):
        gear = state["timing_gear"]
        sync = state["synchronization"]
        
        md = f"""# Structural Timing Brief ({state['date_kst']})

## Timing Gear: **Level {gear['level']} ({gear['label']})**
- **Description**: {gear['description']}

## Synchronization Status
- **Axis Alignment**: {sync['axis_alignment']}
- **Conflict Pressure**: {sync['conflict_pressure']}
- **Narrative Velocity**: {sync['narrative_velocity']}

## Acceleration Watch
{chr(10).join([f"- {w}" for w in state['acceleration_watch']])}

## Deceleration Warning
{chr(10).join([f"- {w}" for w in state['deceleration_warning']])}
"""
        OUTPUT_MD.write_text(md, encoding="utf-8")

if __name__ == "__main__":
    StructuralTimingLayer().execute()
