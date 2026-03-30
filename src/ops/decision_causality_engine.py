import json
from pathlib import Path

class DecisionCausalityEngine:
    def __init__(self, project_root):
        self.project_root = Path(project_root)

    def build_causality_chain(self, core_theme, context, decision_value):
        """
        [STEP-D] Builds a 5-point structural causality chain.
        """
        mechanism = self._derive_mechanism(core_theme, context)
        structural_context = self._derive_structure(core_theme, context)
        trigger = self._derive_trigger(core_theme, context)
        decision_link = self._derive_decision_link(decision_value, mechanism, trigger)

        return {
            "theme": core_theme,
            "mechanism": mechanism,
            "structural_context": structural_context,
            "trigger": trigger,
            "decision_link": decision_link
        }

    def _derive_mechanism(self, theme, context):
        """
        Identifies the underlying engine/economic mechanism.
        """
        # Rule-based mapping for major themes
        if "Power" in theme or "Energy" in theme:
            return "Infrastructure bottleneck due to exponential AI compute demand"
        if "Evolution" in theme or "Frontier" in theme:
            return "Paradigm shift in software productivity and hardware optimization"
        
        # Fallback from context
        momentum = context.get("momentum", "STABLE")
        return f"Structural {momentum} shift in {theme} value chain"

    def _derive_structure(self, theme, context):
        """
        Defines the high-level supply/demand or structural conflict.
        """
        stage = context.get("stage", "UNKNOWN")
        if stage == "EXPANSION":
            return "Market demand is accelerating faster than capacity can be added"
        if stage == "PEAK":
            return "Structural equilibrium reached; risk of oversupply or exhaustion increases"
        
        return f"Early-stage structural formation within the {theme} ecosystem"

    def _derive_trigger(self, theme, context):
        """
        Identifies the immediate catalyst (WHY NOW).
        """
        why_now = context.get("why_now", "")
        if why_now:
            # Clean up or truncate locked narrative if too long
            return why_now[:100] + "..." if len(why_now) > 100 else why_now
        
        pressure = context.get("pressure_score", 0)
        return f"Narrative pressure spike (Score: {pressure}) indicates immediate relevance"

    def _derive_decision_link(self, value, mechanism, trigger):
        """
        Explicitly links the structural chain to the final decision value.
        """
        if value == "WATCH":
            return f"{mechanism} remains uncertain; awaiting confirmation from {trigger} to commit capital."
        if value in ["ACCUMULATE", "EARLY_ENTRY"]:
            return f"{trigger} validates the {mechanism}; initiating exposure based on structural tailwinds."
        if value == "HOLD":
            return f"{mechanism} is in progress; maintaining position as structural trend persists."
        
        return f"Decision {value} aligned with structural {mechanism} analysis."
