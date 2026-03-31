"""
src/ops/conflict_pair_map.py
Static Mapping for Contradiction Patterns (Phase 22C).
Used to explain potential conflicts between different market signals.
No-Behavior-Change: Pure explanation/mapping, no scoring.
"""

# Pattern ID -> Contradiction Details
CONFLICT_PAIR_MAP = {
    "RATE_UP_FLOW_IN": {
        "pattern": "금리 인상/긴축 시그널 + 자본 유입/리스크온",
        "description": "정책 금리 상승 압력에도 불구하고 시장 유동성이 확대되거나 자산 매수세가 강해지는 상충 상황",
        "lhs_label": "금리/긴축 시그널",
        "rhs_label": "자본 유입/리스크온"
    },
    "EARNINGS_UP_PRICE_DOWN": {
        "pattern": "실적 호조 + 주가 하락 (Sell the News)",
        "description": "기업 실적 발표가 예상치를 상회했음에도 자본 회수 또는 선반영 해소로 인해 가격이 하락하는 상충 상황",
        "lhs_label": "실적 호조",
        "rhs_label": "가격 하락"
    },
    "REGULATION_UP_INVEST_UP": {
        "pattern": "규제 강화 + 투자 급증",
        "description": "정부 또는 기관의 규제/압박에도 불구하고 해당 섹터에 대한 대규모 설비 투자나 자본 투입이 지속되는 상황",
        "lhs_label": "규제 강화",
        "rhs_label": "투자 급증"
    },
    "USD_UP_RISK_ON": {
        "pattern": "달러 강세 + 위험자산 강세",
        "description": "안전 자산인 달러 가치가 상승함과 동시에 주식, 코인 등 위험 자산의 가격이 동반 상승하는 이례적 상황",
        "lhs_label": "달러 강세",
        "rhs_label": "위험자산 강세"
    },
    "OIL_UP_INFLATION_DOWN": {
        "pattern": "유가 상승 + 물가 둔화",
        "description": "에너지 가격 상승으로 인한 비용 압박에도 불구하고 전반적인 소비자 물가 지표가 하락하는 구조적 괴리",
        "lhs_label": "유가 상승",
        "rhs_label": "물가 둔화"
    }
}

def get_conflict_candidate(dataset_id, axes, causal_chain):
    """
    Suggests a contradiction pair based on topics and causal chains.
    Returns a list of matching patterns.
    """
    candidates = []
    
    # Simple keyword-based matching for Phase 22C
    cc_text = str(causal_chain).lower()
    
    # 1. RATE_UP_FLOW_IN logic
    if "rate" in cc_text or "fed" in cc_text:
        if "flow" in cc_text or "inflow" in cc_text or "bull" in cc_text:
            candidates.append("RATE_UP_FLOW_IN")
            
    # 2. EARNINGS_UP_PRICE_DOWN
    if "earnings" in cc_text or "profit" in cc_text:
        if "down" in cc_text or "fall" in cc_text or "negative" in cc_text:
            candidates.append("EARNINGS_UP_PRICE_DOWN")
            
    # 3. USD_UP_RISK_ON
    if "usd" in cc_text or "dollar" in cc_text:
        if "risk-on" in cc_text or "growth" in cc_text:
            candidates.append("USD_UP_RISK_ON")
            
    # Default if axes are mixed but no specific keyword hit
    if len(axes) >= 2 and not candidates:
        # Potential conflict between top 2 axes
        pass
        
    return [CONFLICT_PAIR_MAP[c] for c in candidates if c in CONFLICT_PAIR_MAP]
