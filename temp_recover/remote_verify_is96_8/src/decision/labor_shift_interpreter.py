"""
Labor Shift Interpreter (IS-96-x)
Interprets data from Labor/Capex collectors to determine if "AI Labor Shift" theme is active.
Deterministic logic based on Confluence Rules >= 2.
"""

from pathlib import Path
import pandas as pd
import json
import os
from datetime import datetime

class LaborShiftInterpreter:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.collect_dir = self.base_dir / "data" / "collect"
        self.output_dir = self.base_dir / "data" / "decision"
        
    def load_metric(self, collector_name, filename):
        path = self.collect_dir / collector_name / "curated" / f"{filename}.json"
        if not path.exists():
            return None
        return pd.read_json(path, orient='records', convert_dates=['date'])

    def compute_metrics(self):
        metrics = {}
        
        # 1. Labor Shift Gap (Bachelors vs High School)
        unemp_bach = self.load_metric("labor_market_us", "unemp_bachelors")
        unemp_hs = self.load_metric("labor_market_us", "unemp_highschool")
        
        if unemp_bach is not None and unemp_hs is not None:
             # Get latest common date
             latest = unemp_bach.iloc[-1] # Assuming sorted
             latest_hs = unemp_hs.iloc[-1]
             metrics['labor_gap'] = latest['value'] - latest_hs['value']
             metrics['labor_gap_status'] = "narrowing" if metrics['labor_gap'] > -1.5 else "normal" # Threshold example
        
        # 2. Wage Premium
        wage_const = self.load_metric("labor_market_us", "wage_construction")
        wage_priv = self.load_metric("labor_market_us", "wage_total_private")
        
        if wage_const is not None and wage_priv is not None:
            # Simple YoY calc
            w_c_growth = wage_const['value'].pct_change(12).iloc[-1] * 100
            w_p_growth = wage_priv['value'].pct_change(12).iloc[-1] * 100
            metrics['wage_premium'] = w_c_growth - w_p_growth
        
        # 3. Capex Momentum
        capex = self.load_metric("datacenter_capex_pipeline_us", "const_spending_office") # Proxy
        if capex is not None:
            metrics['capex_momentum'] = capex['value'].pct_change(12).iloc[-1] * 100
            
        return metrics

    def interpret(self):
        metrics = self.compute_metrics()
        
        # Confluence Checks
        signals = []
        
        # Signal 1: Labor Statistics Shift
        if metrics.get('labor_gap', -99) > -1.5 or metrics.get('wage_premium', -99) > 1.0:
            signals.append("Labor Stats Shift (Gap Narrowing or Blue Collar Premium)")
            
        # Signal 2: Capex Expansion
        if metrics.get('capex_momentum', -99) > 15.0:
            signals.append(f"Capex Expansion (Momentum {metrics['capex_momentum']:.1f}%)")
            
        # Signal 3: Layoffs (Stub)
        # Check layoff file
        layoff_file = self.collect_dir / "layoffs_white_collar_us" / "latest_snapshot.json"
        if layoff_file.exists():
            with open(layoff_file) as f:
                ldata = json.load(f)
                if ldata.get("ai_attributed_layoff_count", 0) > 1000: # Threshold
                    signals.append("AI Layoffs Detected")

        # Confluence Decision
        is_active = len(signals) >= 2
        
        # Hypothesis Jump Logic (IS-96-x)
        # Rule: READY if reliability >= threshold (here count >= 2 implied)
        hypothesis_jump = {
             "status": "READY" if is_active else "HOLD",
             "trigger_reason": "Confluence met (>=2 inputs)" if is_active else "Insufficient signals (<2)",
             "independent_sources_count": len(signals)
        }

        result = {
            "theme": "AI Industrialization -> Labor Market Shift",
            "active": is_active,
            "hypothesis_jump": hypothesis_jump,
            "confluence_count": len(signals),
            "signals": signals,
            "metrics": metrics,
            "why_now": [
                "Physcial AI Buildout requires trades",
                "White collar automation reduces degree premium"
            ] if is_active else [],
            "risk": ["Capex Slowdown", "Regulation"]
        }
        
        
        # Save Unit
        self.output_dir.mkdir(parents=True, exist_ok=True)
        # Load existing output if any to append/update
        output_file = self.output_dir / "interpretation_units.json"
        units = []
        if output_file.exists():
            try:
                content = output_file.read_text()
                units = json.loads(content) if content.strip() else []
                if isinstance(units, dict): # Handle migration if needed
                     units = [units]
            except:
                units = []
        
        # Remove existing LABOR_SHIFT entry to update
        units = [u for u in units if u.get("interpretation_key") != "LABOR_MARKET_SHIFT"]
        
        # Format result as proper unit
        unit_entry = {
            "interpretation_id": f"IS-96-{datetime.now().strftime('%Y%m%d')}-LABOR",
            "as_of_date": datetime.now().strftime("%Y-%m-%d"),
            "target_sector": "PHYSICAL_AI_INFRA",
            "interpretation_key": "LABOR_MARKET_SHIFT",
            "confidence_score": 0.9 if is_active else 0.5,
            "evidence_tags": signals,
            "structural_narrative": "AI Industrialization driving labor shift (Blue collar premium / White collar freeze).",
            "derived_metrics_snapshot": metrics,
            "hypothesis_jump": hypothesis_jump,
            "why_now": result["why_now"],
            "risk": result["risk"]
        }
        
        units.append(unit_entry)
        
        with open(output_file, "w") as f:
            json.dump(units, f, indent=2, ensure_ascii=False)
            
        print(f"[INTERPRETER] Labor Shift Analysis: Active={is_active}, Signals={signals}")

if __name__ == "__main__":
    i = LaborShiftInterpreter()
    i.interpret()
