# src/analyst/fallback_analyst.py
# HOIN Insight Rule-based Analyst Fallback (v1.1)

def generate_fallback_analysis(signal: dict) -> dict:
    """Gemini 장애 시 정형 데이터를 기반으로 최소한의 분석 구조 생성"""
    topic = signal.get("topic", "시장")
    strength = signal.get("strength", 0)
    
    return {
        "topic_core_claim": f"{topic}에서 구조적 이상징후({strength}점) 감지",
        "one_line_summary": "현재는 지표의 과열 혹은 급발진에 따른 구조적 변화 초입 구간입니다.",
        "why_now": "최근 데이터 변화가 통계적 임계치를 초과하여 하드 필터를 발동시켰습니다.",
        "surface_fact": "주요 지표에서 최근 90일 내 발견되지 않았던 통계적 이상치가 발생했습니다.",
        "structural_truth": "단순 가격 변동을 넘어선 자금 흐름의 가속화가 감지되는 초기 국면입니다.",
        "capital_flow": "스마트머니의 방향성 불확실성이 증가하고 있으며, 위험 관리 포지션이 구축되고 있습니다.",
        "primary_beneficiary": "전술적 현금 비중 확대 및 인버스/방어주 섹터에 대한 관심이 필요한 시점입니다.",
        "risk_kill_switch": "주요 지수의 Z-score가 정상 범위(±0.5)로 회귀할 경우 이 가설은 무효화됩니다.",
        "market_state": {
            "risk_appetite": "혼조",
            "hedging_activity": "증가",
            "conviction": "낮음"
        },
        "is_fallback": True
    }
