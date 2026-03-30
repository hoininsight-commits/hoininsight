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
        impact_chain = impact_map.get("structural_impact_chain", [])
        
        # [STEP-C/D] Risk score is ahora a structured object
        risk_obj = brief_data.get("risk", {}).get("risk_score", 0.5)
        risk_score = risk_obj.get("value", 0.5) if isinstance(risk_obj, dict) else risk_obj
        
        if not stocks:
            print("[AllocationEngine] No stocks found for allocation.")
            return None
            
        # Create a lookup for structural data
        chain_map = {c["ticker"]: c for c in impact_chain} if impact_chain else {}

        # Prepare data for calculator
        stocks_data = []
        for s in stocks:
            ticker = s.get("ticker", "UNKNOWN")
            stock_name = s.get("stock", s.get("name", "UNKNOWN"))
            base_confidence = s.get("confidence", 0.5)
            
            # [STEP-E] Structural Weighting Adjustment
            # Try to match by ticker or name
            chain = chain_map.get(ticker) or next((v for v in chain_map.values() if v.get("name") == stock_name), None)
            
            if chain:
                # Directness multiplier
                multiplier = 1.0
                if chain["directness"] == "direct": multiplier = 1.3
                elif chain["directness"] == "proxy": multiplier = 0.8
                
                # Evidence density bonus
                evidence_count = len(chain.get("evidence_basis", []))
                bonus = min(evidence_count * 0.05, 0.2)
                
                adjusted_confidence = min((base_confidence * multiplier) + bonus, 1.0)
                print(f"[Allocation] Structural adjustment for {ticker}: {base_confidence} -> {adjusted_confidence}")
            else:
                adjusted_confidence = base_confidence * 0.5 # Penalty for missing structural chain
                print(f"[Allocation] ⚠️ Penalty for {ticker}: No structural chain found.")

            stocks_data.append({
                "ticker": ticker,
                "stock": s.get("stock", s.get("name", "UNKNOWN")),
                "confidence": adjusted_confidence,
                "risk_score": risk_score
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
