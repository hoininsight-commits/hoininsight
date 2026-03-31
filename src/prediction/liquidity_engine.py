import json
import os
import pandas as pd
from pathlib import Path
from datetime import datetime

class LiquidityEngine:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.output_path = self.project_root / "data" / "ops" / "liquidity_state.json"
        self.fred_base = self.project_root / "data" / "raw" / "fred"

    def _get_latest_data(self, category, filename):
        # Search for the most recent date directory
        try:
            year_dirs = sorted([d for d in (self.fred_base / category).iterdir() if d.is_dir()], reverse=True)
            if not year_dirs: return None
            month_dirs = sorted([d for d in year_dirs[0].iterdir() if d.is_dir()], reverse=True)
            if not month_dirs: return None
            day_dirs = sorted([d for d in month_dirs[0].iterdir() if d.is_dir()], reverse=True)
            if not day_dirs: return None
            
            for day_dir in day_dirs:
                target_file = day_dir / filename
                if target_file.exists():
                    return pd.read_csv(target_file)
        except Exception as e:
            print(f"[LiquidityEngine] Error loading {category}/{filename}: {e}")
        return None

    def run_analysis(self):
        print("[LiquidityEngine] Analyzing Market Liquidity...")
        
        fed_funds = self._get_latest_data("rates", "fed_funds_rate.csv")
        m2_data = self._get_latest_data("money_supply", "m2.csv")
        dxy_data = None # Could add later if needed
        
        # Heuristic Logic
        # Default to NEUTRAL
        state = "NEUTRAL"
        score = 50
        drivers = []
        
        if fed_funds is not None and not fed_funds.empty:
            latest_rate = fed_funds.iloc[-1]['value']
            if latest_rate > 4.5:
                state = "TIGHTENING"
                score += 20
                drivers.append("high policy rate (Fed Funds > 4.5%)")
            elif latest_rate < 2.5:
                state = "EASING"
                score -= 20
                drivers.append("accommodative policy rate")

        if m2_data is not None and not m2_data.empty:
            # Check for M2 growth/contraction
            if len(m2_data) >= 2:
                m2_prev = m2_data.iloc[-2]['value']
                m2_curr = m2_data.iloc[-1]['value']
                if m2_curr < m2_prev:
                    state = "TIGHTENING"
                    score += 10
                    drivers.append("M2 money supply contraction")
                else:
                    drivers.append("M2 money supply stable/expanding")

        # Cap score
        score = min(max(score, 0), 100)
        
        if score > 60: state = "TIGHTENING"
        elif score < 40: state = "EASING"
        else: state = "NEUTRAL"

        summary = f"Market liquidity is {state} with a score of {score}. Drivers include {', '.join(drivers)}."

        result = {
            "state": state,
            "score": score,
            "summary": summary,
            "drivers": drivers,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
            
        print(f"[LiquidityEngine] Analysis completed: {state}")
        return result

if __name__ == "__main__":
    # For testing
    project_root = Path(__file__).parent.parent.parent
    engine = LiquidityEngine(project_root)
    engine.run_analysis()
