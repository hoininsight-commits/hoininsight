class AllocationCalculator:
    """
    Calculates base and normalized weights for portfolio allocation.
    Formula: base_weight = confidence * (1 - risk_score)
    """
    
    @staticmethod
    def calculate_base_weights(stocks_data):
        """
        Calculates base weights for a list of stocks.
        stocks_data: list of dicts with 'ticker', 'confidence', 'risk_score'
        """
        results = []
        for stock in stocks_data:
            confidence = stock.get("confidence", 0.0)
            risk_score = stock.get("risk_score", 0.0)
            
            # Formula: base_weight = confidence * (1 - risk_score)
            base_weight = confidence * (1 - risk_score)
            
            results.append({
                "ticker": stock["ticker"],
                "stock": stock.get("stock", stock["ticker"]),
                "base_weight": max(0.0, base_weight),
                "confidence": confidence,
                "risk": risk_score
            })
        return results

    @staticmethod
    def normalize_weights(base_weights, total_target=1.0):
        """
        Normalizes weights so they sum up to the target (e.g., 100%).
        """
        total_base = sum(item["base_weight"] for item in base_weights)
        if total_base == 0:
            return base_weights
            
        for item in base_weights:
            item["weight"] = round((item["base_weight"] / total_base) * total_target, 4)
            
        return base_weights
