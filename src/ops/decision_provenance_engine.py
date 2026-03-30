import json
from datetime import datetime

class DecisionProvenanceEngine:
    def __init__(self, project_root):
        self.project_root = project_root

    @staticmethod
    def wrap_decision_field(value, source, reason="", evidence=None, causality=None):
        """
        Wraps a raw decision value with mandatory provenance metadata.
        """
        return {
            "value": value,
            "source": source, # engine | fallback | repaired
            "reason": reason,
            "evidence": evidence or [],
            "causality": causality or {}
        }

    @staticmethod
    def get_default(field):
        """
        Returns hardcoded fallback values for mandatory decision fields.
        """
        defaults = {
            "action": "WATCH",
            "timing": "WAIT",
            "confidence": 0.25,
            "risk": "MEDIUM",
            "allocation": 0.0,
            "conviction": 25
        }
        return defaults.get(field)

    def build_decision_provenance(self, decision_raw, context):
        """
        Converts a flat decision dictionary into a structured provenance map.
        """
        result = {}
        fields = ["action", "timing", "confidence", "risk", "allocation", "conviction"]

        for field in fields:
            val = decision_raw.get(field)
            
            # Localize source detection
            if val is None or val == 0 and field in ["confidence", "conviction"]:
                result[field] = self.wrap_decision_field(
                    self.get_default(field),
                    "fallback",
                    f"Missing or zero {field} → fallback applied",
                    []
                )
            else:
                # Default assume engine for now, pipeline can override
                source = decision_raw.get(f"{field}_source", "engine")
                reason = decision_raw.get(f"{field}_reason", self._derive_reason(field, context))
                evidence = decision_raw.get(f"{field}_evidence", self._derive_evidence(field, context))
                
                result[field] = self.wrap_decision_field(val, source, reason, evidence)

        return result

    def _derive_reason(self, field, context):
        """
        Auto-generates a reason string from context if engine didn't provide one.
        """
        stage = context.get("stage", "UNKNOWN")
        momentum = context.get("momentum", "UNKNOWN")
        return f"Derived from {stage} stage and {momentum} momentum."

    def _derive_evidence(self, field, context):
        """
        Collects relevant indicator values as evidence.
        """
        evidence = []
        if "pressure_score" in context:
            evidence.append(f"Topic Pressure: {context['pressure_score']}")
        if "risk_score" in context:
            evidence.append(f"Risk Score: {context['risk_score']}")
        return evidence

    def compute_decision_integrity(self, decision):
        """
        Calculates the trust ratio based on fallback usage.
        """
        total = len(decision)
        fallback_count = sum(1 for v in decision.values() if v.get("source") == "fallback")
        
        ratio = fallback_count / total if total > 0 else 1.0
        
        if ratio <= 0.2:
            status = "STABLE"
        elif ratio <= 0.5:
            status = "DEGRADED"
        else:
            status = "LOW_TRUST"

        return {
            "engine_fields": total - fallback_count,
            "fallback_fields": fallback_count,
            "fallback_ratio": round(ratio, 2),
            "status": status,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def build_evidence_chain(self, core_theme, context, decision_provenance):
        """
        Creates a deep evidence record for the Decision Audit Trail.
        """
        return {
            "core_theme": core_theme,
            "why_now": context.get("why_now", []),
            "inputs": {
                "stage": context.get("stage"),
                "momentum": context.get("momentum"),
                "pressure_score": context.get("pressure_score"),
                "risk_score": context.get("risk_score")
            },
            "decision": decision_provenance,
            "fallback_used": any(v["source"] == "fallback" for v in decision_provenance.values()),
            "fallback_fields": [
                k for k, v in decision_provenance.items()
                if v["source"] == "fallback"
            ],
            "audit_timestamp": datetime.now().isoformat()
        }
