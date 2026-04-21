# src/validation/quality_score.py

def calculate_quality_score(data: dict) -> int:
    """분석 데이터의 품질을 수치화 (0-100)"""
    if not data:
        return 0
        
    score = 0

    # 1. 필수 필드 존재 여부 (각 20점, 총 60점)
    required = ["topic_core_claim", "why_now", "one_line_summary"]
    for f in required:
        if f in data and data[f] and len(str(data[f]).strip()) > 0:
            score += 20

    # 2. 내용의 구체성 (20점)
    # Why Now 섹션이 충분히 긴지 확인
    why_now = data.get("why_now", "")
    if len(why_now) > 30:
        score += 20
    elif len(why_now) > 10:
        score += 10

    # 3. 데이터 근거성 (20점)
    # 내용에 숫자가 포함되어 있는지 확인 (정량적 분석 여부)
    if any(char.isdigit() for char in str(data)):
        score += 20

    return score
