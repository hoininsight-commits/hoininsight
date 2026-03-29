import json
from pathlib import Path
from datetime import datetime
from src.allocation.allocation_calculator import AllocationCalculator
from src.allocation.risk_adjuster import RiskAdjuster

class AllocationEngine:
    """
    Main engine for capital allocation.
    """
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.output_path = self.project_root / "data" / "allocation" / "capital_allocation.json"
        
    def run_allocation(self, brief_data):
        """
        Computes final allocation based on brief data.
        """
        print("[AllocationEngine] Running capital allocation...")
        
        impact_map = brief_data.get("impact_map", {})
        stocks = impact_map.get("mentionable_stocks", [])
        risk_score = brief_data.get("risk", {}).get("risk_score", 0.5)
        
        if not stocks:
            print("[AllocationEngine] No stocks found for allocation.")
            return None
            
        # Prepare data for calculator
        stocks_data = []
        for s in stocks:
            stocks_data.append({
                "ticker": s.get("ticker", "UNKNOWN"),
                "stock": s.get("stock", s.get("name", "UNKNOWN")),
                "confidence": s.get("confidence", 0.5),
                "risk_score": risk_score # Using theme-level risk as default
            })
            
        # 1. Calculate Base Weights
        base = AllocationCalculator.calculate_base_weights(stocks_data)
        
        # 2. First Normalization
        norm = AllocationCalculator.normalize_weights(base)
        
        # 3. Apply Risk Adjustments (Caps/Filters)
        adjusted = RiskAdjuster.apply_safety_rules(norm)
        
        # 4. Enforce Diversification (Theme limits)
        final_allocs = RiskAdjuster.enforce_diversification(adjusted)
        
        # Final output object
        total_exposure = round(sum(a["weight"] for a in final_allocs), 4)
        output = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "total_capital": 1.0,
            "theme_exposure": total_exposure,
            "allocations": final_allocs,
            "allocation_reason": f"Risk-adjusted optimization for {len(final_allocs)} stocks (Exposure: {total_exposure}).",
            "allocation_evidence": [f"risk_score={risk_score}", f"stock_count={len(stocks)}"],
            "metadata": {
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "engine": "AllocationEngine-v1.1"
            }
        }
        
        # Save output
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
            
        print(f"[AllocationEngine] Allocation saved: {len(final_allocs)} positions.")
        return output
