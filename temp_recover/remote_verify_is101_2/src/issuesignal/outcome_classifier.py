from typing import Dict, Any, Optional

class OutcomeClassifier:
    """
    IS-43: POST_OUTCOME_CLASSIFIER
    Classifies signal outcomes based on market timing and narrative validity.
    """

    CLASSIFICATION_MAP = {
        "ON_TIME": "정확",
        "EARLY": "너무 빠름",
        "LATE": "너무 늦음",
        "OVERSTATED": "과도함",
        "SILENCE_CORRECT": "침묵이 옳았음"
    }

    def classify_outcome(self, signal: Dict[str, Any], market_reaction: Dict[str, Any]) -> str:
        """
        Logic to determine the outcome tag.
        market_reaction keys: time_diff_hours, volatility_level, direction_match (bool)
        """
        status = signal.get("status")
        
        if status == "SILENT":
            # If nothing happened in the window, silence was correct
            if market_reaction.get("volatility_level") == "LOW":
                return self.CLASSIFICATION_MAP["SILENCE_CORRECT"]
            return "침묵 오류 (무시된 신호가 발생함)"

        # For READY signals
        time_diff = market_reaction.get("time_diff_hours", 0)
        direction = market_reaction.get("direction_match", False)
        volatility = market_reaction.get("volatility_level", "LOW")

        if not direction:
            return "예측 실패"

        if time_diff < 12:
            return self.CLASSIFICATION_MAP["ON_TIME"]
        elif time_diff < 48:
            return self.CLASSIFICATION_MAP["ON_TIME"]
        elif time_diff < 168:
            return self.CLASSIFICATION_MAP["EARLY"]
        
        if volatility == "LOW":
            return self.CLASSIFICATION_MAP["OVERSTATED"]

        return self.CLASSIFICATION_MAP["LATE"]
