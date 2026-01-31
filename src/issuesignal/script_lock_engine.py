from typing import Dict, Any, List, Optional, Tuple
import logging

logger = logging.getLogger("ScriptLockEngine")

class ScriptLockEngine:
    """
    IS-62: Locks the narrative into a strict 6-step 'Economic Hunter' structure.
    Enforces language rules (No 'possibility', Only 'inevitable').
    """

    FORBIDDEN_WORDS = ["가능성", "보인다", "추측", "전망", "될 수", "아마", "글쎄", "?"]
    MANDATORY_WORDS = ["필연", "결정", "해야 한다"]

    @staticmethod
    def generate(protagonist: Dict[str, Any], why_now: str, target_sector: str) -> Dict[str, str]:
        """
        Generates the 5-step locked script (IS-66 Editorial Mode).
        Returns a dict with 'long_form', 'shorts', 'one_liner'.
        """
        
        # Data Extraction
        fact_text = protagonist.get("fact_text", "")
        details = protagonist.get("details", {})
        action_type = details.get("action_type", "행동")
        company = details.get("company", "대상 기업")
        reasoning = protagonist.get("bottleneck_reason", "구조적 변화 확인 필요")
        
        # Step 1: DEFINITION (Signal & Anomaly)
        # "Subject has done Action." -> "What signal is detected now?"
        step1 = f"1. 정의 (Signal)\n지금 시장공급망 데이터에서 {company}의 {action_type}와 관련하여 평소와 다른 유의미한 이상 신호가 포착되었습니다. {fact_text}."

        # Step 2: SURFACE (Market Misread Template)
        # "The market interprets this as [Action Type]."
        step2 = f"2. 표면 해석 (Surface)\n현재 대부분의 언론과 시장 참여자들은 이를 단순한 {action_type} 이슈로 해석하고 넘어가는 분위기입니다."

        # Step 3: MISREAD (Rebuttal)
        # "But this is a misjudgment. The essence is [Reasoning]."
        step3 = f"3. 시장의 오해 (Misread)\n그러나 이는 데이터의 본질을 놓치고 있는 명백한 오판입니다. 단순한 이벤트가 아니라, 시장의 구조가 변화하고 있다는 시그널로 읽어야 합니다."

        # Step 4: STRUCTURAL FORCE (The Real Reason)
        # "The structural reason is [Reasoning] + [Why Now]."
        step4 = f"4. 구조적 강제 (Structural Force)\n실제로 움직이는 구조적 이유는 {reasoning}에 있습니다. {why_now}."

        # Step 5: CONCLUSION (Hunter Close)
        # "Therefore, expanding [Sector] is inevitable."
        step5 = f"5. 결론 (Conclusion)\n이 흐름은 되돌릴 수 없는 필연입니다. 지금 {target_sector} 섹터의 변화를 주시하고, 남들보다 한 발 앞서 대응해야 할 시점입니다."

        # Assembly
        full_script = f"{step1}\n\n{step2}\n\n{step3}\n\n{step4}\n\n{step5}"
        
        # Validation
        is_valid, error_msg = ScriptLockEngine.validate(full_script)
        if not is_valid:
            logger.error(f"Script Validation Failed: {error_msg}")
            full_script += f"\n\n[SYSTEM WARNING: Validation Failed - {error_msg}]"

        return {
            "long_form": full_script,
            "one_liner": f"{company}의 {action_type}: {target_sector} 섹터 변화는 필연입니다.",
            "shorts_ready": [
                f"[속보] {fact_text}",
                f"시장은 오판하고 있습니다. 본질은 {reasoning}입니다.",
                f"{why_now}",
                f"결론: {target_sector} 비중 확대는 필연입니다."
            ]
        }

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
