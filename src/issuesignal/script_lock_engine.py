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
        Generates the 6-step locked script.
        Returns a dict with 'long_form', 'shorts', 'one_liner'.
        """
        
        # Data Extraction
        fact_text = protagonist.get("fact_text", "")
        details = protagonist.get("details", {})
        action_type = details.get("action_type", "ACT")
        company = details.get("company", "Target")
        reasoning = protagonist.get("bottleneck_reason", "")
        
        # Step 1: DEFINITION (Declaration)
        # "Subject has done Action."
        step1 = f"1. 정의 (Declaration)\n{fact_text}."

        # Step 2: SURFACE (Market Misread Template)
        # "The market interprets this as [Action Type]."
        step2 = f"2. 표면 해석 (Surface)\n시장은 이를 {company}의 단순한 {action_type} 행동으로 해석하고 있습니다."

        # Step 3: MISREAD (Rebuttal)
        # "But this is a misjudgment. The essence is [Reasoning]."
        step3 = f"3. 시장의 오해 (Misread)\n그러나 이는 명백한 오판입니다. 본질은 {reasoning}에 있습니다."

        # Step 4: FORCED MOVE (Structural Bottleneck)
        # From IS-60 Bottleneck Reason
        step4 = f"4. 구조적 강제 (Forced Move)\n이 기업은 구조적 병목을 장악했습니다. 경쟁사가 절대 따라올 수 없는 독점적 지위가 확보되었습니다."

        # Step 5: WHY NOW (Time Lock)
        # From IS-61 Why Now
        step5 = f"5. WHY NOW (Time Lock)\n{why_now}"

        # Step 6: CONCLUSION (Hunter Close)
        # "Therefore, expanding [Sector] is inevitable."
        step6 = f"6. 결론 (Hunter Close)\n따라서 {target_sector} 섹터에 대한 비중 확대는 필연입니다. 지금 즉시 행동해야 합니다."

        # Assembly
        full_script = f"{step1}\n\n{step2}\n\n{step3}\n\n{step4}\n\n{step5}\n\n{step6}"
        
        # Validation
        is_valid, error_msg = ScriptLockEngine.validate(full_script)
        if not is_valid:
            logger.error(f"Script Validation Failed: {error_msg}")
            # In strict mode, we might return an error or a fallback. 
            # For IS-62, we return the script but log the error heavily, 
            # or we could attempt to fix it. 
            # Given the template is hardcoded to be valid, this is mostly for safety against dynamic inputs.
            full_script += f"\n\n[SYSTEM WARNING: Validation Failed - {error_msg}]"

        return {
            "long_form": full_script,
            "one_liner": f"{company}의 {action_type}: {target_sector} 섹터 비중 확대는 필연입니다.",
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
