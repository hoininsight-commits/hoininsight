# src/validation/quality_gate.py
# HOIN Insight Pipeline Quality Gate (v1.1)

def validate_minimum_quality(data: dict) -> bool:
    """분석 결과물이 최소한의 통찰을 포함하고 있는지 검증"""
    if not data:
        return False
        
    # Phase 6 Task 7: 필수 필드 정의
    required_fields = ["topic_core_claim", "why_now", "one_line_summary"]
    
    for field in required_fields:
        if field not in data or not data[field]:
            print(f"  ❌ [QUALITY_GATE] Missing required field: {field}")
            return False
            
    # 글자 수 등 부가 조건 추가 (옵션)
    if len(str(data.get("why_now", ""))) < 20:
        print("  ❌ [QUALITY_GATE] 'why_now' explanation too short.")
        return False
        
    print("  ✅ [QUALITY_GATE] Minimum quality check passed.")
    return True
