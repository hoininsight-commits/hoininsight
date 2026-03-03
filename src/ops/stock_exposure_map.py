"""
src/ops/stock_exposure_map.py
Structural Mapping between Engine Axis and Market Sectors/Stocks.
No-Behavior-Change: Pure mapping, no scoring.
"""

# Axis -> Industry -> Stock Representative List
# Logic: Simplified structural linkage for Phase 22B
AXIS_EXPOSURE_MAP = {
    "Policy:RATE": {
        "industry": "은행/보험",
        "logic": "금리 변동에 따른 순이자마진(NIM) 및 공정가치 변화 민감",
        "stocks": [
            {"ticker": "105560", "name": "KB금융", "exposure_type": "금리 수익", "risk_note": "가계 대출 규제 및 충당금 적립 부담"},
            {"ticker": "055550", "name": "신한지주", "exposure_type": "금리 수익", "risk_note": "부동산 PF 연체율 관리 리스크"}
        ]
    },
    "Liquidity:LIQUIDITY": {
        "industry": "성장주/반도체",
        "logic": "할인율 변화에 따른 밸류에이션 탄력성 및 유동성 집중형 업종",
        "stocks": [
            {"ticker": "000660", "name": "SK하이닉스", "exposure_type": "유동성/성장", "risk_note": "PER 멀티플 압축 및 HBM 경쟁 심화"},
            {"ticker": "042700", "name": "한미반도체", "exposure_type": "독점적 장비", "risk_note": "글로벌 IT 투자 축소 시 수주 공백"}
        ]
    },
    "SupplyChain:CHAIN": {
        "industry": "IT 장비/부품",
        "logic": "글로벌 공급망 재편 및 설비 투자(CAPEX) 사이클 연동",
        "stocks": [
            {"ticker": "066570", "name": "LG전자", "exposure_type": "전장/가전", "risk_note": "원자재 가격 및 물류비용 변동성"},
            {"ticker": "009150", "name": "삼성전기", "exposure_type": "MLCC/컴포넌트", "risk_note": "스마트폰 및 PC 수요 회복 지연"}
        ]
    },
    "Energy:ENERGY": {
        "industry": "이차전지/정유",
        "logic": "원자재 공급망 및 친환경 정책 기조에 따른 이익 변동",
        "stocks": [
            {"ticker": "373220", "name": "LG에너지솔루션", "exposure_type": "배터리 셀", "risk_note": "전기차 캐즘(Chasm) 및 리튬가 변동"},
            {"ticker": "096770", "name": "SK이노베이션", "exposure_type": "정유/배터리", "risk_note": "정제마진 하락 및 재무구조 부담"}
        ]
    },
    "Macro:INFLATION": {
        "industry": "필수소비재/유통",
        "logic": "가격 전가력(Pricing Power) 및 비용 상승에 따른 이익 방어력",
        "stocks": [
            {"ticker": "051900", "name": "LG생활건강", "exposure_type": "소비재", "risk_note": "중국 시장 회복 속도 및 마케팅비 증가"},
            {"ticker": "097950", "name": "CJ제일제당", "exposure_type": "식품/소재", "risk_note": "원재료 곡물가 변동 및 내수 부진"}
        ]
    }
}

DEFAULT_EXPOSURE = {
    "industry": "시장 전반",
    "logic": "특정 섹터 외 거시 지표 변화에 따른 포괄적 영향",
    "stocks": [
        {"ticker": "005930", "name": "삼성전자", "exposure_type": "시장 지향", "risk_note": "글로벌 매크로 환경 및 외국인 수급 변동성"}
    ]
}

def get_linkage_for_axis(axis_list):
    """
    Returns combined industry and stock list for a list of axis.
    """
    industries = []
    stocks = []
    
    if not axis_list:
        return [DEFAULT_EXPOSURE]

    for axis in axis_list:
        if axis in AXIS_EXPOSURE_MAP:
            mapping = AXIS_EXPOSURE_MAP[axis]
            industries.append({"industry": mapping["industry"], "logic": mapping["logic"]})
            stocks.extend(mapping["stocks"])
    
    if not industries:
        return [DEFAULT_EXPOSURE]
        
    # De-duplicate stocks by ticker
    seen = set()
    unique_stocks = []
    for s in stocks:
        if s["ticker"] not in seen:
            unique_stocks.append(s)
            seen.add(s["ticker"])
            
    return {
        "industry_exposure": industries,
        "stocks": unique_stocks
    }
