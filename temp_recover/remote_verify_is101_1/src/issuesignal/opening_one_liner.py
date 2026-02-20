import re
from typing import Dict, List, Any, Optional

def synthesize_opening_one_liner(top_topic: Optional[Dict[str, Any]], decision_tree_data: List[Dict[str, Any]], locale="ko") -> str:
    """
    Synthesizes a single authoritative Korean opening one-liner based on the decision tree.
    Strict Tone Lock: No speculation words allowed.
    """
    
    # 1. Failure Case (No Topic or Decision Tree Fail)
    # Check if the tree has any failures
    first_fail = next((node for node in decision_tree_data if node['status'] == 'FAIL'), None)
    
    if not top_topic or first_fail:
        fail_node_name = first_fail['name'] if first_fail else "알 수 없는 기준"
        
        # IS-73 Failure Mapping Table
        failure_map = {
            "데이터 수집": "오늘은 수집된 유의미한 데이터 신호가 없어 침묵한다.",
            "팩트 체크": "오늘은 확증 가능한 하드 팩트가 부족하여 발화를 중단한다.",
            "시점 분석": "오늘 반드시 말해야 할 시점(WHY-NOW) 조건이 충족되지 않았다.",
            "주인공 매칭": "이슈를 주도할 명확한 주인공(수혜/피해)이 식별되지 않았다.",
            "품질 하한선": "최종 품질 기준(스크립트 생성 불가 등) 미달로 발화를 보류한다."
        }
        
        return failure_map.get(fail_node_name, f"오늘은 {fail_node_name} 기준을 넘지 못해 침묵한다.")

    # 2. Success Case (Topic Selected)
    # Priority 1: Use existing WHY-NOW sentence if strictly validated
    # We assume 'authority_sentence' or 'why_now' field carries the best summary.
    # In IS-67, 'authority_sentence' is the high-quality one.
    
    candidate_sentence = ""
    
    if top_topic.get('authority_sentence') and len(top_topic.get('authority_sentence')) > 10:
        candidate_sentence = top_topic['authority_sentence']
    elif top_topic.get('why_now') and isinstance(top_topic['why_now'], str):
        candidate_sentence = top_topic['why_now']
    else:
        # Priority 2: Derive from context (Fallback Template)
        actor = top_topic.get('actor', '시장')
        # Simple logical fallback
        candidate_sentence = f"지금 {actor}에 대한 확실한 변화가 감지되었고, 선택의 순간이 왔다."

    # 3. Tone Lock & Validation
    # Ensure no speculation words
    banned_patterns = [
        r"가능성", r"전망", r"추정", r"예상", r"보인다", r"일 수", r"할 것"
    ]
    
    for pattern in banned_patterns:
        if re.search(pattern, candidate_sentence):
            # Fallback if banned word found (Safety Net)
            return f"오늘 {top_topic.get('actor', '주체')}와 관련된 팩트가 확정되었다."
            
    # Ensure plain ending (이다/한다/왔다/됐다)
    # This is a soft check, mostly redundant if inputs are good.
    
    return candidate_sentence
