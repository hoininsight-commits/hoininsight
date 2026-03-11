import hashlib
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

class TrustLockEngine:
    """
    (IS-26) Final status gatekeeper. 
    Guarantees that a Decision Card is ready for human use without edits.
    """
    VAGUE_WORDS = ["가능성", "전망", "수 있다", "보인다", "예상"]
    FORCED_WORDS = ["해야", "불가피", "강제", "이동", "발생"]

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def evaluate(self, 
                 final_card: Dict[str, Any], 
                 is_fact_passed: bool, 
                 has_duplicate: bool) -> Tuple[str, List[str], Optional[str]]:
        """
        Evaluates the final card for trust readiness.
        Returns: (trust_state, fail_codes, signature)
        """
        fail_codes = []
        
        # 1. FACT INTEGRITY (IS-25)
        if not is_fact_passed:
            fail_codes.append("FACT_INTEGRITY_FAIL")

        # 2. STRUCTURAL COMPLETENESS
        required_fields = ["what", "why", "who", "where", "kill_switch"]
        if not all(field in final_card for field in required_fields):
            fail_codes.append("INCOMPLETE_STRUCTURE")

        # 3. ACTION CLARITY & NO VAGUE TERMS
        text_payload = str(final_card).lower()
        if any(vw in text_payload for vw in self.VAGUE_WORDS):
            fail_codes.append("VAGUE_EXPRESSION")
        
        # Check for forced verbs (at least one must exist in core narrative)
        if not any(fw in text_payload for fw in self.FORCED_WORDS):
            fail_codes.append("NO_FORCED_ACTION")

        # 4. NOVELTY GUARANTEE (IS-23)
        if has_duplicate:
            fail_codes.append("NOT_NOVEL")

        # 5. HUMAN READABILITY (Simulated complexity check)
        if len(final_card.get("why", "")) > 200: # Too long explanation
            fail_codes.append("LOW_READABILITY")

        # Determination
        if not fail_codes:
            signature = self._generate_signature(final_card)
            return "TRUST_LOCKED", [], signature
        
        # HOLD vs REJECT classification
        critical_fails = {"FACT_INTEGRITY_FAIL", "INCOMPLETE_STRUCTURE", "NOT_NOVEL"}
        if any(fc in critical_fails for fc in fail_codes):
            return "REJECT", fail_codes, None
            
        return "HOLD", fail_codes, None

    def _generate_signature(self, card: Dict[str, Any]) -> str:
        payload = json.dumps(card, sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()[:16]
