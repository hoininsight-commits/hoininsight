# src/validation/quality_score_v2.py
# Quality Score v2: Precision Evaluation Layer ( 지시서 #079 )

QUALITY_WEIGHTS = {
    "field_completeness": 20,
    "logical_coherence": 20,
    "numerical_evidence": 15,
    "specificity": 15,
    "why_now_strength": 15,
    "structure_quality": 15
}

def score_field_completeness(data):
    """Task 2: 필드 완성도 (20점)"""
    required = [
        "topic_core_claim",
        "why_now",
        "structural_truth",
        "one_line_summary"
    ]
    present = sum(1 for f in required if data.get(f))
    return (present / len(required)) * 20

def score_logic(data):
    """Task 7: 논리 일관성 (20점)"""
    # 표면적 팩트와 구조적 진실이 모두 존재하는지 확인
    if data.get("surface_fact") and data.get("structural_truth"):
        return 20
    return 10

def score_numerical(data):
    """Task 3: 수치 기반 평가 (15점)"""
    text = str(data)
    if any(char.isdigit() for char in text):
        return 15
    return 0

def score_specificity(data):
    """Task 4: 구체성 평가 (15점)"""
    text = str(data)
    keywords = ["금리", "유동성", "Z-score", "채권", "수급", "포지션", "변동성"]
    count = sum(1 for k in keywords if k in text)
    return min(count * 5, 15)

def score_why_now(data):
    """Task 5: Why Now 강도 (15점)"""
    text = str(data.get("why_now", ""))
    if len(text) > 50:
        return 15
    elif len(text) > 20:
        return 10
    return 5

def score_structure(data):
    """Task 6: 구조 품질 (15점)"""
    keys = ["surface_fact", "structural_truth", "capital_flow"]
    present = sum(1 for k in keys if data.get(k))
    return (present / len(keys)) * 15

def normalize_score(score):
    """Task 9: Score Range 정규화 (40~95)"""
    if score > 95:
        return 95
    if score < 40:
        return 40
    return int(score)

def get_quality_grade(score):
    """Task 10: Grade 정의"""
    if score >= 85:
        return "HIGH"
    elif score >= 70:
        return "MEDIUM"
    elif score >= 55:
        return "LOW"
    else:
        return "FALLBACK"

def calculate_quality_score_v2(data: dict, is_fallback: bool = False):
    """Task 8: 최종 통합 점수 계산"""
    if not data:
        return 40
        
    score = 0
    score += score_field_completeness(data)
    score += score_logic(data)
    score += score_numerical(data)
    score += score_specificity(data)
    score += score_why_now(data)
    score += score_structure(data)

    # 🔥 fallback 패널티 (지시서 #079: 50점 상한선)
    if is_fallback or data.get("fallback_used"):
        score = min(score, 50)

    score = normalize_score(score)
    return score
