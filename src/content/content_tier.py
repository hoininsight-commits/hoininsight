# src/content/content_tier.py
"""
[지시서 #087] Content Tier System 정의
USE/REVIEW/DROP 판정을 컨텐츠 등급으로 변환
"""

CONTENT_TIERS = {
    "TIER_1": "HIGH_CONFIDENCE",   # 기존 USE (확정적 메인 컨텐츠)
    "TIER_2": "CONDITIONAL",       # 기존 REVIEW (보완적 조건 컨텐츠)
    "TIER_3": "EARLY_SIGNAL"       # 기존 DROP (탐지형 초기 신호)
}

def map_action_to_tier(action: str) -> str:
    if action == "USE":
        return "TIER_1"
    if action == "REVIEW":
        return "TIER_2"
    return "TIER_3" # DROP 및 기타 실패는 모두 초기 신호로 전환
