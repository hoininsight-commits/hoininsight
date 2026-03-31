class PatternScorer:
    """
    Implements the scoring logic for patterns.
    Formula: score = (win_rate * 0.6) + (avg_return * 0.4)
    """
    
    @staticmethod
    def calculate_score(win_rate, avg_return):
        """
        Calculates the pattern score.
        """
        # win_rate is 0.0 to 1.0
        # avg_return is usually -0.1 to 0.1 (multiplied by weighting)
        # To make it comparable, we might need some scaling for avg_return.
        # But per instruction: score = (win_rate * 0.6) + (avg_return * 0.4)
        
        score = (win_rate * 0.6) + (avg_return * 0.4)
        return round(score, 4)

    @staticmethod
    def get_adjustment(score, threshold=0.5):
        """
        Calculates confidence adjustment based on score.
        IF pattern_score > threshold -> increase confidence
        IF pattern_score < threshold -> decrease confidence
        """
        # Linear mapping or threshold based?
        # Let's say: adjustment = (score - threshold) * 0.5 (scaled)
        # Instruction says: IF > threshold -> increase, IF < threshold -> decrease.
        
        adjustment = (score - threshold) * 0.4 # Scaling factor to keep it within +/- 0.2
        
        # SafetyMechanism: Clamp to [-0.2, 0.2]
        adjustment = max(-0.2, min(0.2, adjustment))
        
        return round(adjustment, 2)
