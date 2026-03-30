import json
from pathlib import Path
from datetime import datetime, timedelta

class OutcomeValidationEngine:
    """
    [STEP-F] Decision -> Outcome Validation Loop
    Tracks actual performance and classifies outcomes using a structured taxonomy.
    """
    
    FAILURE_TAXONOMY = [
        "THEME_WRONG",
        "THEME_RIGHT_DECISION_WRONG",
        "THEME_RIGHT_STOCK_WRONG",
        "TIMING_WRONG",
        "ALLOCATION_WRONG",
        "CAUSALITY_MISMATCH",
        "SUCCESS"
    ]

    def __init__(self, project_root):
        self.project_root = Path(project_root)

    def evaluate_outcome(self, run_data, market_data):
        """
        Evaluates a single run against market outcomes.
        """
        eval_result = {
            "theme_correct": self._check_theme_validity(run_data, market_data),
            "decision_effective": self._check_decision_effectiveness(run_data, market_data),
            "allocation_effective": self._check_allocation_performance(run_data, market_data),
            "hit_ratio": self._compute_hit_ratio(run_data, market_data)
        }

        eval_result["failure_type"] = self._classify_failure(eval_result)
        return eval_result

    def _check_theme_validity(self, run_data, market_data):
        """
        Checks if the core theme was actually the dominant market narrative.
        """
        # Logic: If market benchmark mentions the theme or industry, it's valid.
        theme = run_data.get("core_theme", "").lower()
        market_narrative = market_data.get("dominant_narrative", "").lower()
        if theme in market_narrative:
            return True
        
        # Proxy: If benchmark returns are positive for the sector
        return market_data.get("theme_realized", False)

    def _check_decision_effectiveness(self, run_data, market_data):
        """
        Checks if the Action (WATCH/HOLD/ACCUMULATE) was the right move.
        """
        decision = run_data.get("investment_decision", {}).get("action", {}).get("value", "WATCH")
        market_return = market_data.get("benchmark_return", 0.0)
        
        if decision in ["ACCUMULATE", "EARLY_ENTRY"] and market_return > 0.005:
            return True
        if decision == "WATCH" and abs(market_return) < 0.005:
            return True
        if decision == "HOLD" and market_return >= 0:
            return True
            
        return False

    def _check_allocation_performance(self, run_data, market_data):
        """
        Checks if the top weighted stocks outperformed the benchmark.
        """
        top_stocks_return = market_data.get("top_stocks_return", 0.0)
        benchmark_return = market_data.get("benchmark_return", 0.0)
        return top_stocks_return > benchmark_return

    def _compute_hit_ratio(self, run_data, market_data):
        """
        Computes how many impact_chain stocks actually performed.
        """
        impact_chain = run_data.get("impact_chain", [])
        if not impact_chain: return 0.0
        
        hits = 0
        stock_performance = market_data.get("stock_performance", {})
        
        for stock in impact_chain:
            ticker = stock.get("ticker")
            if stock_performance.get(ticker, 0.0) > 0:
                hits += 1
                
        return round(hits / len(impact_chain), 2)

    def _classify_failure(self, eval_res):
        """
        Determines the failure type based on evaluation metrics.
        """
        if not eval_res["theme_correct"]:
            return "THEME_WRONG"
        if not eval_res["decision_effective"]:
            return "THEME_RIGHT_DECISION_WRONG"
        if eval_res["hit_ratio"] < 0.4:
            return "THEME_RIGHT_STOCK_WRONG"
        if not eval_res["allocation_effective"]:
            return "ALLOCATION_WRONG"
            
        return "SUCCESS"

    def update_summary(self, ledger_entries):
        """
        Generates rolling 7d/30d performance summaries.
        """
        if not ledger_entries: return {}
        
        def calculate_stats(entries):
            count = len(entries)
            if count == 0: return {}
            
            theme_acc = sum(1 for e in entries if e["evaluation"]["theme_correct"]) / count
            dec_acc = sum(1 for e in entries if e["evaluation"]["decision_effective"]) / count
            hit_ratio_avg = sum(e["evaluation"]["hit_ratio"] for e in entries) / count
            
            return {
                "theme_accuracy": round(theme_acc, 2),
                "decision_accuracy": round(dec_acc, 2),
                "hit_ratio_avg": round(hit_ratio_avg, 2),
                "sample_size": count
            }

        # Simplified: Just last 7 entries for 7d for demo
        last_7 = ledger_entries[-7:]
        last_30 = ledger_entries[-30:]
        
        return {
            "last_7d": calculate_stats(last_7),
            "last_30d": calculate_stats(last_30),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
