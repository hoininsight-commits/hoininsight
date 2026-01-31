from typing import Dict, Any, List, Optional, Tuple
import logging

logger = logging.getLogger("ScriptLockEngine")

class ScriptLockEngine:
    """
    IS-62: Locks the narrative into a strict 6-step 'Economic Hunter' structure.
    Enforces language rules (No 'possibility', Only 'inevitable').
    """

    FORBIDDEN_WORDS = ["같습니다", "모릅니다", "생각됩니다", "가능성", "추측", "전망", "아마", "글쎄", "?"]
    MANDATORY_WORDS = ["필연", "결정", "해야 한다"]

    @staticmethod
    def generate(protagonist: Dict[str, Any], why_now: str, target_sector: str, evidence_pool: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        IS-67: Generates script WITH automated evidence binding.
        """
        company = protagonist.get("details", {}).get("company", "대상 기업")
        action_type = protagonist.get("details", {}).get("action_type", "행동")
        fact_text = protagonist.get("fact_text", "")
        reasoning = protagonist.get("bottleneck_reason", "구조적 변화")

        # 1. Bind Evidence
        bindings = ScriptLockEngine.bind_evidence(protagonist, evidence_pool)
        
        # Helper to get ref text
        def get_ref(block_key: str, default: str) -> str:
            ref = bindings.get(block_key)
            if not ref: return default
            return f" (근거: {ref['text'][:40]}...)"

        # Step 1: 정의
        step1_base = f"지금 {company}의 {action_type}와 관련하여 평소와 다른 유의미한 이상 신호가 데이터로 포착되었습니다. {fact_text}."
        step1 = f"1. 정의 (Signal)\n{step1_base}{get_ref('step1', ' [직접 근거 확인 중]')}"

        # Step 2: 표면 해석
        step2_base = f"언론과 시장은 이를 단순한 {action_type}로 보고 있으나, 이는 데이터 이면을 놓치고 있는 해석입니다."
        step2 = f"2. 표면 해석 (Surface)\n{step2_base}{get_ref('step2', '')}"

        # Step 3: 시장의 오해
        step3_base = f"시장은 현재 일시적 반응으로 오해하고 있지만, 본질은 {reasoning}의 시작입니다."
        step3 = f"3. 시장의 오해 (Misread)\n{step3_base}{get_ref('step3', '')}"

        # Step 4: 구조적 강제
        step4_base = f"구조적으로 {reasoning}이 강제될 수밖에 없는 환경입니다. {why_now}."
        step4 = f"4. 구조적 강제 (Structural Force)\n{step4_base}{get_ref('step4', ' [구조적 팩트 확인 중]')}"

        # Step 5: 결론
        step5_base = f"따라서 {target_sector} 섹터의 변화는 필연적입니다. 지금이 선제적 대응의 적기입니다."
        step5 = f"5. 결론 (Conclusion)\n{step5_base}{get_ref('step5', '')}"

        full_script = f"{step1}\n\n{step2}\n\n{step3}\n\n{step4}\n\n{step5}"
        
        # Validation
        is_valid, error_msg = ScriptLockEngine.validate(full_script)
        if not is_valid:
            return None # Fail generation for floor enforcement

        return {
            "long_form": full_script,
            "shorts_15s": f"[필연] {company} {action_type}! 팩트는 {reasoning}입니다. {target_sector}에 주목하십시오.",
            "shorts_30s": f"[데이터 이상신호] {fact_text}. 시장의 오해를 넘어 본질을 봐야 합니다. {why_now}. {target_sector}의 변화는 필연입니다.",
            "shorts_45s": f"1분 요약: {company} {action_type}의 진짜 의미. {reasoning}이라는 구조적 강제가 작동 중입니다. {why_now}. 따라서 {target_sector} 섹터 비중 확대는 필연적인 결정입니다.",
            "text_card": f"📌 {company} {action_type}\n- 원인: {reasoning}\n- 결론: {target_sector} 필연적 변화\n- 근거: {bindings.get('step1', {}).get('text', '데이터 참조')[:30]}",
            "one_liner": f"{company}: {target_sector} 변화의 필연성",
            "bindings": bindings
        }

    @staticmethod
    def bind_evidence(protagonist: Dict[str, Any], pool: List[Dict[str, Any]]) -> Dict[str, Dict]:
        """
        IS-67 Evidence Binding Logic
        """
        bindings = {}
        
        # Priority mapping
        # Step 1 (Definition): Trigger Quote or HardFact
        s1 = next((f for f in pool if f.get('type') == 'TRIGGER_QUOTE' or f.get('grade') == '✅증거'), None)
        if s1: bindings['step1'] = {"id": s1.get('id'), "text": s1.get('fact_text', s1.get('fact', ''))}
        
        # Step 2 (Surface): Headline / Common news
        s2 = next((f for f in pool if 'HINT' in f.get('type', '') or '뉴스' in f.get('fact_text', '')), None)
        if s2: bindings['step2'] = {"id": s2.get('id'), "text": s2.get('fact_text', '')}

        # Step 4 (Structural): CorpAction or Macro
        s4 = next((f for f in pool if f.get('type') == 'CORPORATE_ACTION' or f.get('type') == 'MACRO_FACT'), None)
        if s4: bindings['step4'] = {"id": s4.get('id'), "text": s4.get('fact_text', '')}

        # Step 5 (Conclusion): Kill Switch or Observer
        s5 = next((f for f in pool if 'KILL' in f.get('fact_text', '') or '관찰' in f.get('fact_text', '')), None)
        if s5: bindings['step5'] = {"id": s5.get('id'), "text": s5.get('fact_text', '')}

        return bindings

    @staticmethod
    def validate(script: str) -> Tuple[bool, str]:
        """
        Validates against Language Rules.
        """
        # Check Forbidden
        for word in ScriptLockEngine.FORBIDDEN_WORDS:
            if word in script:
                return False, f"Forbidden word detected: '{word}'"
        
        # Check Mandatory (At least one)
        # Actually logic says "Mandatory expressions: ...". 
        # Let's require at least one or strict check?
        # The prompt implies the script MUST contain strong language.
        # Our template puts "필연" in Step 6, "행동해야 합니다" in Step 6.
        # So it should pass.
        
        has_mandatory = any(word in script for word in ScriptLockEngine.MANDATORY_WORDS)
        if not has_mandatory:
            return False, "Missing mandatory strong language (필연, 결정, 해야 한다)."

        return True, "OK"
