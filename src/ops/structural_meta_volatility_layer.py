#!/usr/bin/env python3
import json
import logging
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Project Root Setup
ROOT = Path(__file__).parent.parent.parent
DATA_OPS = ROOT / "data_outputs" / "ops"
DATA_DECISION = ROOT / "data" / "decision"

# Output Paths
OUTPUT_JSON = DATA_OPS / "meta_volatility_state.json"
OUTPUT_MD = DATA_OPS / "meta_volatility_brief.md"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StructuralMetaVolatilityLayer:
    def __init__(self):
        pass

    def _load_json(self, path: Path):
        if not path.exists():
            logger.warning(f"File not found: {path}")
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            logger.error(f"Error loading {path}: {e}")
            return {}

    def execute(self):
        logger.info("Running Structural Meta-Volatility Engine v1.0...")

        # 1. Load Inputs
        regime_data = self._load_json(DATA_OPS / "regime_state.json")
        os_data = self._load_json(DATA_OPS / "investment_os_state.json")
        timing_data = self._load_json(DATA_OPS / "timing_state.json")
        comp_data = self._load_json(DATA_OPS / "probability_compression_state.json")
        conflict_data = self._load_json(DATA_OPS / "conflict_density_pack.json")
        video_pool = self._load_json(DATA_OPS / "video_candidate_pool.json")

        # 2. Extract Features
        # Regime
        regime_info = regime_data.get("regime", {})
        lq = regime_info.get("liquidity_state", "UNKNOWN")
        pl = regime_info.get("policy_state", "UNKNOWN")
        rs = regime_info.get("risk_state", "UNKNOWN")
        cv = regime_info.get("curve_state", "UNKNOWN")

        # Timing
        tm_info = timing_data.get("timing_gear", {})
        gear = tm_info.get("level", 1)
        sync = timing_data.get("synchronization", {}).get("status", "UNKNOWN")
        accel = timing_data.get("acceleration_watch", [])
        decel = timing_data.get("deceleration_warning", [])

        # Compression
        cp_info = comp_data.get("compression_state", {})
        direction = cp_info.get("direction", "NEUTRAL")
        pressure = cp_info.get("pressure_level", "LOW")
        stability = cp_info.get("stability", "STABLE")

        # Conflict
        conflicts = conflict_data.get("topics", [])
        conflict_density = "LOW"
        if len(conflicts) >= 10: conflict_density = "HIGH"
        elif len(conflicts) >= 5: conflict_density = "MEDIUM"

        # Video
        video_candidates = len(video_pool.get("top_candidates", []))

        # 3. Meta-Volatility Logic
        mode = "MIXED"
        compression_criteria = 0
        if pressure in ["HIGH", "ELEVATED"]: compression_criteria += 1
        if gear >= 3 and sync in ["PARTIAL", "MIXED", "LOW"]: compression_criteria += 1
        if lq in ["TIGHTENING", "RESTRICTIVE"] and rs == "ELEVATED": compression_criteria += 1
        if conflict_density in ["LOW", "MEDIUM"] and pressure == "HIGH": compression_criteria += 1

        expansion_criteria = 0
        if conflict_density == "HIGH" or len(conflicts) >= 8: expansion_criteria += 1
        if gear >= 4 and len(accel) >= 2: expansion_criteria += 1
        if video_candidates >= 2: expansion_criteria += 1
        if stability == "FRAGILE" and direction != "NEUTRAL": expansion_criteria += 1

        if compression_criteria >= 2 and expansion_criteria >= 2:
            mode = "MIXED"
        elif compression_criteria >= 2:
            mode = "COMPRESSION"
        elif expansion_criteria >= 2:
            mode = "EXPANSION"
        else:
            mode = "MIXED"

        # Fragility
        fragility = "MEDIUM"
        if (lq == "TIGHTENING" and gear >= 3 and stability == "FRAGILE") or (conflict_density == "HIGH" and stability == "FRAGILE"):
            fragility = "HIGH"
        elif rs == "EASING" and stability == "STABLE" and gear <= 2:
            fragility = "LOW"

        # Shock Window
        shock_window = "NONE"
        if fragility == "HIGH" and (gear >= 4 or conflict_density == "HIGH"):
            shock_window = "ELEVATED"
        elif pressure in ["HIGH", "ELEVATED"] or fragility in ["MEDIUM", "HIGH"]:
            shock_window = "WATCH"

        # 4. Interpretation
        one_liner = f"지금 시장은 {mode} 상태이며, 취약성은 {fragility}입니다."
        
        why_now = []
        if gear >= 3:
            why_now.append(f"Timing Gear {gear} 가속 및 {sync} 동기화 상태 감지")
        else:
            why_now.append(f"Timing Gear {gear} 수준의 저강도 시계열 흐름")
            
        if pressure in ["HIGH", "ELEVATED"]:
            why_now.append(f"Probability Compression 압력 {pressure} 도달로 인한 에너지 응축")
        else:
            why_now.append(f"상대적으로 낮은 변동성 압축 강도 ({pressure})")
            
        if lq in ["TIGHTENING", "RESTRICTIVE"]:
            why_now.append(f"유동성 {lq} 정권 하에서의 구조적 민감도 증폭")
        else:
            why_now.append(f"정권 차원의 위험 노출도 {rs} 상태 유지")

        invalidators = [
            f"Timing Gear {gear-1 if gear > 1 else 0} 이하로의 급격한 서사 감속",
            f"Stability가 {stability}에서 STABLE로의 구조적 전환 발생"
        ]

        # 5. Build State
        kst_now = datetime.now(timezone.utc) + timedelta(hours=9)
        state = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "date_kst": kst_now.strftime("%Y-%m-%d"),
            "state": {
                "mode": mode,
                "fragility": fragility,
                "shock_window": shock_window
            },
            "signals": {
                "regime": { "policy": pl, "liquidity": lq, "risk": rs, "curve": cv },
                "timing": { "gear": gear, "sync": sync, "accel_watch": accel, "decel_warning": decel },
                "compression": { "direction": direction, "pressure": pressure, "stability": stability },
                "conflict": { "density_level": conflict_density, "top_conflicts": [t.get("topic") for t in conflicts[:3]] },
                "video": { "candidates": video_candidates }
            },
            "interpretation": {
                "one_liner": one_liner,
                "why_now": why_now,
                "invalidators": invalidators
            }
        }

        # 6. Save Outputs
        OUTPUT_JSON.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info(f"Generated {OUTPUT_JSON}")

        self._generate_brief(state)
        logger.info(f"Generated {OUTPUT_MD}")

    def _generate_brief(self, state: dict):
        s = state["state"]
        i = state["interpretation"]
        sig = state["signals"]
        
        md = f"""# Structural Meta-Volatility Brief ({state['date_kst']})

## Meta-Volatility State
- **Mode**: {s['mode']}
- **Fragility**: {s['fragility']}
- **Shock Window**: {s['shock_window']}

## Executive Summary
> {i['one_liner']}

## Key Signals
- **Regime**: Liquidity {sig['regime']['liquidity']} / Risk {sig['regime']['risk']}
- **Timing**: Gear {sig['timing']['gear']} ({sig['timing']['sync']} Sync)
- **Compression**: {sig['compression']['direction']} (Pressure: {sig['compression']['pressure']})
- **Conflict**: {sig['conflict']['density_level']} Density

## Why Now?
{chr(10).join([f"- {w}" for w in i['why_now']])}

## Invalidators
{chr(10).join([f"- {v}" for v in i['invalidators']])}
"""
        OUTPUT_MD.write_text(md, encoding="utf-8")

if __name__ == "__main__":
    StructuralMetaVolatilityLayer().execute()
