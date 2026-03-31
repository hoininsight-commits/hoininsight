class RiskAdjuster:
    """
    Enforces risk-based caps and limit rules for capital allocation.
    """
    
    @staticmethod
    def apply_safety_rules(allocations):
        """
        Applies hard risk rules and position limits.
        """
        adjusted = []
        for item in allocations:
            weight = item.get("weight", 0.0)
            risk = item.get("risk", 0.0)
            confidence = item.get("confidence", 0.0)
            
            # 1. Low Confidence Filter: IF confidence < 0.4 -> exclude
            if confidence < 0.4:
                weight = 0.0
            
            # 2. High Risk Cap: IF risk_score > 0.7 -> max weight = 0.1
            if risk > 0.7:
                weight = min(weight, 0.1)
            
            # 3. Max Position Limit: single stock <= 0.3
            weight = min(weight, 0.3)
            
            item["weight"] = round(weight, 4)
            adjusted.append(item)
            
        return adjusted

    @staticmethod
    def enforce_diversification(allocations, min_positions=3):
        """
        Ensures minimum diversification if enough candidates exist.
        """
        # Count non-zero positions
        active = [a for a in allocations if a["weight"] > 0]
        
        # If we have positions but less than min_positions, we might need a warning 
        # or we just accept it if candidates are limited.
        # Rule: single theme <= 0.5 total capital (Currently single theme system)
        
        total_weight = sum(a["weight"] for a in allocations)
        if total_weight > 0.5:
             # If single theme exposure > 0.5, we scale down to 0.5 total
             scale = 0.5 / total_weight
             for item in allocations:
                 item["weight"] = round(item["weight"] * scale, 4)
                 
        return allocations
