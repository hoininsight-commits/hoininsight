#!/usr/bin/env python3
"""
Phase 25: Strategic Capital Allocation Layer v1.0
================================================
Provides a structural frame for capital allocation based on Regime and OS Stance.
Adheres to the NO-BEHAVIOR-CHANGE principle.
"""

import json
import logging
import sys
from pathlib import Path
from datetime import datetime, timezone

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("CapitalAllocation")

# Constants
ROOT = Path(__file__).resolve().parent.parent.parent
DATA_OPS = ROOT / "data_outputs" / "ops"
OUTPUT_JSON = DATA_OPS / "capital_allocation_state.json"
OUTPUT_MD = DATA_OPS / "capital_allocation_brief.md"

# Allocation Templates (Mapping Table)
# Regime + OS Stance -> Allocation Mode
ALLOCATION_MAP = {
    ("TIGHTENING", "DEFENSIVE_BIAS"): {
        "mode": "DEFENSIVE_BALANCED",
        "cash_bias": "HIGH",
        "beta_exposure": "REDUCED",
        "sector_rotation_bias": "RATE_SENSITIVE",
        "volatility_posture": "CONTROLLED",
        "core": "안정성 중심 (채권/배당)",
        "tactical": "이벤트 드리븐 (숏/헷지)",
        "hedge": "변동성 방어 (VIX/Gold)"
    },
    ("TIGHTENING", "NEUTRAL"): {
        "mode": "DEFENSIVE_ROTATION",
        "cash_bias": "MEDIUM",
        "beta_exposure": "NEUTRAL",
        "sector_rotation_bias": "VALUE_CASHFLOW",
        "volatility_posture": "MONITORED",
        "core": "가치주/현금흐름 중심",
        "tactical": "섹터 로테이션",
        "hedge": "하락 변동성 보험"
    },
    ("EASING", "RISK_ON"): {
        "mode": "AGGRESSIVE_GROWTH",
        "cash_bias": "LOW",
        "beta_exposure": "EXPANDED",
        "sector_rotation_bias": "GROWTH_TECH",
        "volatility_posture": "ACTIVE",
        "core": "성장주/기술주 중심",
        "tactical": "베타 플레이",
        "hedge": "최소 헷지"
    },
    ("TRANSITION", "NEUTRAL"): {
        "mode": "BARBELL",
        "cash_bias": "MEDIUM",
        "beta_exposure": "BALANCED",
        "sector_rotation_bias": "CORE_SATELLITE",
        "volatility_posture": "DYNAMIC",
        "core": "바벨 전략 (초우량 + 초성장)",
        "tactical": "균형 재조정",
        "hedge": "양방향 변동성 대응"
    },
    # Fallback/Default
    ("DEFAULT", "DEFAULT"): {
        "mode": "NEUTRAL_BALANCED",
        "cash_bias": "MEDIUM",
        "beta_exposure": "NEUTRAL",
        "sector_rotation_bias": "DIVERSIFIED",
        "volatility_posture": "WAIT_AND_SEE",
        "core": "지수 추종/분산 투자",
        "tactical": "신규 기회 탐색",
        "hedge": "기본 리스크 관리"
    }
}

class CapitalAllocationLayer:
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
        logger.info("Running Strategic Capital Allocation Layer v1.0...")

        # 1. Load Inputs
        os_data = self._load_json(DATA_OPS / "investment_os_state.json")
        regime_data = self._load_json(DATA_OPS / "regime_state.json")
        
        # 2. Extract Key States
        regime_state = regime_data.get("regime", {}).get("liquidity_state", "UNKNOWN")
        # In case the JSON structure is slightly different (standardizing for Phase 25)
        if regime_state == "UNKNOWN":
            regime_state = regime_data.get("regime", {}).get("state", "UNKNOWN")
        
        os_stance = os_data.get("os_summary", {}).get("stance", "NEUTRAL")

        # 3. Determine Allocation Profile
        key = (regime_state, os_stance)
        template = ALLOCATION_MAP.get(key, ALLOCATION_MAP[("DEFAULT", "DEFAULT")])

        # 4. Construct State
        state = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "date_kst": datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=9))).strftime("%Y-%m-%d") if 'timedelta' in globals() else datetime.now().strftime("%Y-%m-%d"),
            "regime_state": regime_state,
            "os_stance": os_stance,
            "allocation_profile": {
                "mode": template["mode"],
                "cash_bias": template["cash_bias"],
                "beta_exposure": template["beta_exposure"],
                "sector_rotation_bias": template["sector_rotation_bias"],
                "volatility_posture": template["volatility_posture"]
            },
            "framework": {
                "core_bucket": template["core"],
                "tactical_bucket": template["tactical"],
                "hedge_bucket": template["hedge"]
            },
            "priority_rotation": [
                {
                    "axis": os_data.get("os_summary", {}).get("focus", ["Policy"])[0],
                    "tilt": "UNDERWEIGHT_GROWTH" if regime_state == "TIGHTENING" else "OVERWEIGHT_GROWTH",
                    "logic": f"{regime_state} 환경 기반 자본 효율성 고려"
                }
            ],
            "risk_expansion_warning": [
                "VIX 급등 시 포지션 축소",
                "Yield Curve 정상화 시 전략 재평가"
            ]
        }
        
        # Override date_kst with a safer way if timedelta not imported
        from datetime import timedelta
        state["date_kst"] = (datetime.now(timezone.utc) + timedelta(hours=9)).strftime("%Y-%m-%d")

        # 5. Save Outputs
        OUTPUT_JSON.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info(f"Generated {OUTPUT_JSON}")

        self._generate_brief(state)
        logger.info(f"Generated {OUTPUT_MD}")

    def _generate_brief(self, state: dict):
        profile = state["allocation_profile"]
        frame = state["framework"]
        rotation = state["priority_rotation"][0]
        
        md = f"""# Strategic Capital Allocation Brief ({state['date_kst']})

## Allocation Mode: **{profile['mode']}**
- **Cash Bias**: {profile['cash_bias']}
- **Beta Exposure**: {profile['beta_exposure']}
- **Sector Rotation Bias**: {profile['sector_rotation_bias']}
- **Volatility Posture**: {profile['volatility_posture']}

## Strategic Framework
- **Core Bucket**: {frame['core_bucket']}
- **Tactical Bucket**: {frame['tactical_bucket']}
- **Hedge Bucket**: {frame['hedge_bucket']}

## Priority Rotation
- **Axis**: {rotation['axis']}
- **Tilt**: {rotation['tilt']}
- **Rationale**: {rotation['logic']}

## Risk Expansion Warning
{chr(10).join([f"- {w}" for w in state['risk_expansion_warning']])}
"""
        OUTPUT_MD.write_text(md, encoding="utf-8")

if __name__ == "__main__":
    CapitalAllocationLayer().execute()
