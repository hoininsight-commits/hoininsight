# src/validation/quality_validation.py
# Validation Hardening Layer (지시서 #083)

VALIDATION_CHECKS = [
    "numerical_consistency",   # 숫자 논리 일관성
    "causal_validity",         # 인과관계 성립 여부 (강화)
    "claim_evidence_alignment",# 주장 vs 근거 일치성 (신규)
    "hallucination_check",     # 환각 탐지 (신규)
]

# Task 2 — 숫자 정확성 검증 (강화)
def validate_numerical_consistency(data):
    text = str(data)
    # 숫자 존재 + 길이 기준 (150자 이상)
    if any(char.isdigit() for char in text) and len(text) > 150:
        return 1
    return 0

# Task 3 — 인과관계 정합성 강화
def validate_causal_chain(data):
    # Analyst의 결과물에서 핵심 계층이 있는지 확인
    if isinstance(data, dict):
        fact = data.get("surface_fact", "")
        truth = data.get("structural_truth", "")
        if fact and truth:
            # 최소 길이 20자 이상으로 정합성 강화
            if len(str(fact)) > 20 and len(str(truth)) > 20:
                return 1
    return 0

# Task 4 — 주장 vs 근거 일치성 검증 (신규)
def validate_claim_evidence_alignment(data):
    if not isinstance(data, dict): return 0
    claim = data.get("topic_core_claim", "")
    truth = data.get("structural_truth", "")

    if claim and truth:
        # 주요 주장이 있고, 그것을 뒷받침하는 TRUTH가 구체적(30자 이상)일 때
        if len(str(claim)) > 10 and len(str(truth)) > 30:
            return 1
    return 0

# Task 5 — 환각(Hallucination) 간접 탐지 (신규)
def validate_hallucination_risk(data):
    text = str(data)
    # 너무 짧거나 너무 일반적(100자 미만)이면 위험 신호
    if len(text) < 100:
        return 0
    return 1

# Task 6 — Validation Score 전면 재구성 (v2)
def calculate_validation_score_v2(data):
    score = 0
    score += validate_numerical_consistency(data)
    score += validate_causal_chain(data)
    score += validate_claim_evidence_alignment(data)
    score += validate_hallucination_risk(data)
    return score  # 0~4

# Task 1 — Trust 기준 강화
def calculate_score_trust(quality_score, validation_score):
    # 🔥 가장 보수적인 신뢰도 등급 기준
    if quality_score >= 85 and validation_score <= 2:
        return "LOW_TRUST"

    if validation_score == 4:
        return "HIGH_TRUST"

    if validation_score == 3:
        return "MEDIUM_TRUST"

    return "LOW_TRUST"

# Task 7 — 행동 정책 강화 (보수화)
def decide_action(quality_score, validation_score, score_trust):
    if score_trust == "LOW_TRUST":
        return "REGENERATE"

    if score_trust == "MEDIUM_TRUST":
        return "REVIEW"

    # HIGH_TRUST라도 점수가 80점 미만이면 인간의 검토가 필요함
    if score_trust == "HIGH_TRUST" and quality_score < 80:
        return "REVIEW"

    return "USE"

# Task 8 — Failure Reasons 추출
def extract_validation_reasons(data):
    reasons = []

    if not validate_numerical_consistency(data):
        reasons.append("WEAK_NUMERICAL_EVIDENCE")

    if not validate_causal_chain(data):
        reasons.append("WEAK_CAUSAL_CHAIN")

    if not validate_claim_evidence_alignment(data):
        reasons.append("CLAIM_MISMATCH")

    # 환각 위험은 데이터가 너무 짧을 때 발생
    if not validate_hallucination_risk(data):
        reasons.append("SHORT_CONTENT_RISK")

    return reasons
