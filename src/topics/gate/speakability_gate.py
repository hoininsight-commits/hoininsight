from typing import Any, Dict, List

class SpeakabilityGate:
    """
    IS-96-2: Speakability Gate
    Determines READY/HOLD/DROP status based on Interpretation Unit.
    """

    def evaluate(self, unit: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate speakability based on deterministic rules.
        """
        metrics = unit.get("derived_metrics_snapshot", {})
        pretext_score = metrics.get("pretext_score", 0.0)
        execution_gap = metrics.get("policy_execution_gap", 0.0)
        tags = unit.get("evidence_tags", [])
        confidence = unit.get("confidence_score", 0.0)
        why_now = unit.get("why_now_type", "")

        reasons = []
        
        # 1. DROP Logic (Fatal Gaps)
        if pretext_score < 0.70:
            reasons.append(f"Pretext score below threshold ({pretext_score} < 0.70)")
            return {"speakability_flag": "DROP", "speakability_reasons": reasons}
        
        if execution_gap > 0.50 and ("KR_POLICY" in tags or "US_POLICY" in tags):
            reasons.append(f"High policy execution gap detected ({execution_gap} > 0.50)")
            return {"speakability_flag": "DROP", "speakability_reasons": reasons}

        # 2. READY vs HOLD Logic
        is_verified = any(t in tags for t in ["EARNINGS_VERIFY", "KR_POLICY", "US_POLICY"])
        
        if pretext_score >= 0.85 and confidence >= 0.80 and is_verified and why_now:
            return {
                "speakability_flag": "READY",
                "speakability_reasons": [
                    "High pretext score and confidence",
                    "Fundamental/Policy execution verified",
                    f"Clear Why-now timing confirmed: {why_now}"
                ]
            }
        else:
            if not is_verified:
                reasons.append("Waiting for fundamental verification (Earnings/Policy execution)")
            if pretext_score < 0.85:
                reasons.append(f"Pretext strength is moderate ({pretext_score})")
            if confidence < 0.80:
                reasons.append(f"Confidence score is below READY threshold ({confidence})")
            if not why_now:
                reasons.append("Specific Why-now trigger type is missing")
            
            return {
                "speakability_flag": "HOLD",
                "speakability_reasons": reasons[:5]
            }

def run_gate(interpretation_unit: Dict[str, Any]) -> Dict[str, Any]:
    gate = SpeakabilityGate()
    return gate.evaluate(interpretation_unit)
