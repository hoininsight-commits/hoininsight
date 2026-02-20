"""
IS-95-4 Price Mechanism Interpreter
Interprets structural pricing power shifts.
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class PriceMechanismInterpreter:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent.parent
        self.collect_dir = self.base_dir / "data" / "collect"
        self.output_dir = self.base_dir / "data" / "decision"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_data(self):
        spreads = {}
        backlog = {}
        dependency = {}
        
        try:
            spreads = json.loads((self.collect_dir / "price_spread_indicators.json").read_text())
        except: pass
        try:
            backlog = json.loads((self.collect_dir / "order_backlog_utilization.json").read_text())
        except: pass
        try:
            dependency = json.loads((self.collect_dir / "buyer_dependency_index.json").read_text())
        except: pass
        
        return spreads, backlog, dependency

    def calculate_metrics(self, spreads, backlog, dependency) -> List[Dict[str, Any]]:
        metrics_list = []
        
        # Simplify: Combine data into a single context for MVP
        # In prod, this would loop through sectors/items
        
        # Logic: Find worst constraints
        max_spread = 0
        spread_ratio = 1.0
        s_margin = 0
        b_margin = 0
        
        if spreads.get("items"):
            item = spreads["items"][0] # Take first for MVP
            spread_ratio = item.get("spread_ratio", 1.0)
            s_margin = item.get("margin_proxy_supplier", 0)
            b_margin = item.get("margin_proxy_buyer", 0)
            
        backlog_yrs = 0
        util_rate = 0
        alloc_flag = False
        if backlog.get("items"):
            item = backlog["items"][0]
            backlog_yrs = item.get("backlog_ratio", 0)
            util_rate = item.get("capacity_utilization", 0)
            alloc_flag = item.get("allocation_flag", False)
            
        lock_in_score = 0
        if dependency.get("items"):
            item = dependency["items"][0]
            lock_in_score = item.get("top_supplier_concentration", 0) * 0.5
            if item.get("tech_lock_in_flag"): lock_in_score += 0.3
            if item.get("certification_required_flag"): lock_in_score += 0.2
            
        # 1. Price Rigidity Score
        rigidity_score = (spread_ratio * 0.4) + (min(backlog_yrs, 5)/5 * 0.1) + (util_rate * 0.5)
        # Cap at 1.0
        rigidity_score = min(rigidity_score, 1.0)
        
        # 2. Power Transfer
        transfer_delta = s_margin - b_margin
        
        # 3. Supply Inelasticity
        inelasticity = (backlog_yrs/5 * 0.2) + (0.5 if util_rate > 0.95 else 0) + (0.3 if alloc_flag else 0)
        inelasticity = min(inelasticity, 1.0)
        
        return [{
            "sector": spreads.get("sector", "UNKNOWN"),
            "rigidity_score": round(rigidity_score, 2),
            "power_transfer_delta": round(transfer_delta, 2),
            "inelasticity_score": round(inelasticity, 2),
            "buyer_lock_in": round(lock_in_score, 2),
            "allocation_flag": alloc_flag,
            "backlog_years": backlog_yrs
        }]

    def interpret(self):
        spreads, backlog, dependency = self.load_data()
        metrics_list = self.calculate_metrics(spreads, backlog, dependency)
        
        interpreter_results = []
        
        for m in metrics_list:
            # Trigger Conditions (ANY 2)
            c1 = m["rigidity_score"] >= 0.7
            c2 = m["backlog_years"] >= 2.0
            c3 = m["allocation_flag"] == True
            
            triggers = [c1, c2, c3]
            is_active = sum(triggers) >= 2
            
            if is_active:
                result = {
                    "interpretation_id": f"IS-95-4-{datetime.now().strftime('%Y%m%d')}-PRICE",
                    "as_of_date": datetime.now().strftime("%Y-%m-%d"),
                    "target_sector": m["sector"],
                    "interpretation_key": "PRICE_MECHANISM_SHIFT",
                    "confidence_score": 0.85 if sum(triggers)==3 else 0.75,
                    "evidence_tags": ["PRICE_RIGIDITY", "ALLOCATION_MARKET"],
                    "structural_narrative": "Price moves driven by structural rigidity and supplier authority transfer.",
                    "derived_metrics_snapshot": m,
                    "hypothesis_jump": {
                        "status": "READY",
                        "trigger_reason": "2+ Rigidity Factors Met"
                    },
                    "why_now": [
                        "Suppliers have gained 'Pricing Power' via Allocation",
                        "Buyers are functionally locked-in (Inelastic demand)"
                    ],
                    "risk": ["Regulatory Intervention", "Tech Substitution"]
                }
                interpreter_results.append(result)
                print(f"[PRICE_MECH] Triggered SHIFT for {m['sector']}")
        
        # Update interpretation_units.json
        out_file = self.output_dir / "interpretation_units.json"
        
        current_units = []
        if out_file.exists():
            try:
                content = out_file.read_text()
                current_units = json.loads(content) if content.strip() else []
                if isinstance(current_units, dict): current_units = [current_units]
            except: pass
            
        # Merge/Append
        # Remove old PRICE_MECHANISM_SHIFT entries to update
        current_units = [u for u in current_units if u.get("interpretation_key") != "PRICE_MECHANISM_SHIFT"]
        current_units.extend(interpreter_results)
        
        with open(out_file, "w") as f:
            json.dump(current_units, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    interpreter = PriceMechanismInterpreter()
    interpreter.interpret()
