from dataclasses import dataclass
from typing import List, Optional

@dataclass
class RotationRule:
    rule_id: str
    condition_desc: str
    target_sector: str
    logic_ko: str
    required_states: dict # key: value (e.g., {"rate_regime": "TIGHTENING", "inflation": "HIGH"})
    priority: int = 1

# Define Rule Set
# This is a deterministic mapping table as requested.
ROTATION_RULES = [
    RotationRule(
        rule_id="ROT_001",
        condition_desc="High Inflation + Tightening (Stagflation Risk)",
        target_sector="Energy & Defensive",
        logic_ko="고물가와 긴축이 지속되는 구간에서는 방어주와 에너지 섹터로 자본이 피신합니다.",
        required_states={"rate_regime": "TIGHTENING", "inflation_regime": "HIGH"},
        priority=10
    ),
    RotationRule(
        rule_id="ROT_002",
        condition_desc="Rate Cut Expectation + Liquidity Expansion",
        target_sector="Growth Tech (Semiconductor/AI)",
        logic_ko="유동성 확장과 금리 인하 기대감이 맞물릴 때, 자본은 성장성이 높은 기술주로 쏠립니다.",
        required_states={"rate_regime": "EASING_ANTICIPATION", "liquidity": "EXPANDING"},
        priority=10
    ),
    RotationRule(
        rule_id="ROT_003",
        condition_desc="Inverted Yield Curve (Recession Fear)",
        target_sector="Short-term Bonds & Gold",
        logic_ko="장단기 금리 역전 심화로 경기 침체 우려가 커지면 자본은 안전자산(채권/금)으로 이동합니다.",
        required_states={"yield_curve": "INVERTED", "risk_sentiment": "OFF"},
        priority=8
    ),
    RotationRule(
        rule_id="ROT_004",
        condition_desc="Geopolitical Escalation",
        target_sector="Defense & Commodities",
        logic_ko="지정학적 긴장이 고조될 때 안보 자산(방산)과 필수 원자재로의 자본 이동은 필수적입니다.",
        required_states={"geopolitics": "ESCALATION"},
        priority=9
    ),
    RotationRule(
        rule_id="ROT_005",
        condition_desc="Normal Growth (Goldilocks)",
        target_sector="Consumer Discretionary & Industrials",
        logic_ko="물가가 안정되고 성장이 지속되는 골디락스 구간에서는 소비재와 산업재가 주도합니다.",
        required_states={"inflation_regime": "STABLE", "growth_regime": "SOLID"},
        priority=5
    )
]
