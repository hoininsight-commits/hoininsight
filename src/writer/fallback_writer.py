# src/writer/fallback_writer.py
# HOIN Insight Gemini Control Layer - Writer Fallback Engine

def generate_fallback(signal: dict, analysis: dict) -> dict:
    """Gemini 장애 시 가동되는 룰 기반 텍스트 생성기"""
    topic = signal.get("topic", "시장")
    strength = signal.get("strength", 0)
    
    return {
        "topic_core_claim": f"{topic}에서 구조적 이상징후({strength}점) 발생",
        "why_now": "최근 데이터 변화가 임계치를 돌파하여 하드 필터를 발동시켰습니다.",
        "surface_fact": f"현재 {topic} 지표가 통계적 범위를 이탈한 상태입니다.",
        "structural_truth": "Flow 상태 변화와 자원 이탈이 겹치며 구조적 변동성이 확대되는 구간입니다.",
        "capital_flow": "스마트머니의 일시적 후퇴와 헤지 포지션 강화가 목격됩니다.",
        "primary_beneficiary": "현금 비중 확대 및 인버스/방어주 섹터",
        "risk_kill_switch": "주요 지표가 20일 이동평균선을 다시 상향 돌파할 경우 시나리오 무효",
        "one_line_summary": "현재는 지표의 과열 혹은 급락에 따른 구조적 변화 초입 구간입니다.",
        "is_fallback": True
    }

def format_fallback_as_md(fb_data: dict) -> str:
    """Fallback 데이터를 Markdown 형식으로 변환"""
    return f"""# [SYSTEM FALLBACK] HOIN Insight 지능형 브리핑

## 1. 구조적 클레임
{fb_data['topic_core_claim']}

## 2. 왜 지금인가? (Trigger)
{fb_data['why_now']}

## 3. 표면적 사실 (Fact)
{fb_data['surface_fact']}

## 4. 구조적 본질 (Structure)
{fb_data['structural_truth']}

## 5. 자금 흐름 (Flow)
{fb_data['capital_flow']}

## 6. 주요 수혜 섹터
{fb_data['primary_beneficiary']}

## 7. 리스크 킬스위치
{fb_data['risk_kill_switch']}

---
**요약**: {fb_data['one_line_summary']}
*(주의: 이 브리핑은 Gemini 장애로 인해 시스템 Fallback 엔진에 의해 생성되었습니다.)*
"""
