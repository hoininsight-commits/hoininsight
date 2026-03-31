class PatternExtractor:
    """
    Extracts high-level decision patterns from theme state and action.
    Target ID format: {THEME_STAGE}_{MOMENTUM}_{ACTION}
    """
    
    @staticmethod
    def extract_id(theme_stage, momentum, action):
        """
        Generates a unique pattern ID.
        """
        # Ensure standard uppercase naming
        stage = str(theme_stage).upper().replace(" ", "_")
        mom = str(momentum).upper().replace(" ", "_")
        act = str(action).upper().replace(" ", "_")
        
        return f"{stage}_{mom}_{act}"

    @staticmethod
    def get_pattern_from_brief(brief):
        """
        Extracts pattern components from the daily brief.
        """
        radar = brief.get("market_radar", {})
        decision = brief.get("investment_decision", {})
        
        stage = radar.get("evolution_stage", "UNKNOWN")
        momentum = radar.get("momentum_state", "UNKNOWN")
        
        # Action might be directly in decision or nested under "decision"
        action = decision.get("action")
        if not action and "decision" in decision:
            action = decision.get("decision", {}).get("action")
            
        if not action:
            action = "UNKNOWN"
            
        return PatternExtractor.extract_id(stage, momentum, action)
