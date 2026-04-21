# src/validation/quality_feedback.py
# Quality Feedback Loop: Failure Reason Extraction ( 지시서 #080 )

import json
from datetime import datetime
from pathlib import Path

FEEDBACK_LOG_DIR = Path("data/feedback")
FEEDBACK_LOG_DIR.mkdir(parents=True, exist_ok=True)
FEEDBACK_LOG_PATH = FEEDBACK_LOG_DIR / "quality_feedback_log.json"

def extract_failure_reasons(data, score):
    """Task 1: 점수 분석 및 실패 원인 추출"""
    reasons = []
    
    # 1. 수치 근거 부족
    if not any(char.isdigit() for char in str(data)):
        reasons.append("NO_NUMERICAL_EVIDENCE")
        
    # 2. Why Now 섹션 부실
    why_now = data.get("why_now", "")
    if len(str(why_now)) < 20:
        reasons.append("WEAK_WHY_NOW")
        
    # 3. 구조적 진실 누락
    if not data.get("structural_truth"):
        reasons.append("MISSING_STRUCTURE")
        
    # 4. 표면적 팩트 누락
    if not data.get("surface_fact"):
        reasons.append("MISSING_FACT")
        
    return reasons

def save_feedback(log_entry):
    """Task 2 & 3: Feedback 로그 저장"""
    logs = []
    if FEEDBACK_LOG_PATH.exists():
        try:
            logs = json.loads(FEEDBACK_LOG_PATH.read_text())
        except:
            pass
            
    logs.append(log_entry)
    
    # 최근 50개까지만 유지
    logs = logs[-50:]
    
    FEEDBACK_LOG_PATH.write_text(json.dumps(logs, ensure_ascii=False, indent=2))

def decide_action(score):
    """Phase 4 Task 6: 행동 정책 정의"""
    if score >= 85:
        return "USE"
    elif score >= 70:
        return "REVIEW"
    elif score >= 55:
        return "IMPROVE"
    else:
        return "REGENERATE"
