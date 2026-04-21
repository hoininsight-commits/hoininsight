# src/content/script_generator.py
"""
[지시서 #087] Tier 기반 스크립트 생성기
분석 데이터를 각 등급에 맞는 톤의 원고로 변환
"""
import json
from src.content.tone_guide import TONE_GUIDE

def generate_tiered_script(data: dict, tier: str) -> str:
    """
    Tier 기반 스크립트 텍스트 생성
    """
    tone = TONE_GUIDE.get(tier, TONE_GUIDE["TIER_3"])
    
    # 데이터 매핑 (기존 pipeline 데이터 구조 대응)
    topic = data.get("topic", "주제 미정")
    claim = data.get("core_claim", topic)
    why_now = data.get("why_now", "시점 근거 분석 중")
    structural_truth = data.get("structural_truth", "구조적 근거 보완 필요")
    
    # 인과관계 체인 가공
    chain = data.get("level2_chain", [])
    chain_text = "\n".join([f"- {c}" for c in chain]) if chain else structural_truth

    script = f"""
[{tier} | {tone['style']}]
🚀 {tone['example']}

주제: {claim}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[WHY NOW: 시점의 근거]
{why_now}

[구조적 팩트 (Structural Truth)]
{chain_text}

[운영 가이드]
이 컨텐츠는 {tone['description']} 등급입니다.
운영 시 위 톤앤매너를 유지하여 채널의 신뢰도와 선제성을 동시에 확보하세요.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    return script.strip()
