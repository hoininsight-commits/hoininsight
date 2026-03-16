import json
import os
import pandas as pd
from pathlib import Path
from datetime import datetime

class RiskEngine:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.output_path = self.project_root / "data" / "ops" / "risk_state.json"
        self.fred_base = self.project_root / "data" / "raw" / "fred"

    def _get_latest_data(self, category, filename):
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
            print(f"[RiskEngine] Error loading {category}/{filename}: {e}")
        return None

    def run_analysis(self):
        print("[RiskEngine] Analyzing Market Risk Stance...")
        
        hy_spread_data = self._get_latest_data("credit", "hy_spread.csv")
        stress_data = self._get_latest_data("credit", "financial_stress.csv")
        
        # VIX logic - I'll check anomalies directory for VIX
        vix_score = 15 # Default
        try:
            vix_f = self.project_root / "data" / "features" / "anomalies" / datetime.now().strftime("%Y") / datetime.now().strftime("%m") / datetime.now().strftime("%d") / "risk_vix_index_stooq.json"
            if not vix_f.exists():
                 # Look for any day in March
                 march_days = sorted(list((self.project_root / "data" / "features" / "anomalies" / "2026" / "03").glob("*")), reverse=True)
                 if march_days:
                     vix_f = march_days[0] / "risk_vix_index_stooq.json"
            
            if vix_f.exists():
                with open(vix_f, "r") as f:
                    v_data = json.load(f)
                    vix_score = v_data.get("latest_value", 15)
        except: pass

        state = "NEUTRAL"
        score = 50
        drivers = []
        
        if vix_score > 20:
            score += 20
            drivers.append(f"Elevated volatility (VIX: {vix_score})")
        elif vix_score < 14:
            score -= 10
            drivers.append("Low equity market volatility")

        if hy_spread_data is not None and not hy_spread_data.empty:
            spread = hy_spread_data.iloc[-1]['value']
            if spread > 4.5:
                score += 20
                drivers.append(f"Wide credit spreads (HY: {spread}%)")
            elif spread < 3.5:
                score -= 10
                drivers.append("Tight credit conditions")

        if stress_data is not None and not stress_data.empty:
            stress_val = stress_data.iloc[-1]['value']
            if stress_val > 0:
                score += 10
                drivers.append(f"Rising financial stress index ({stress_val})")

        score = min(max(score, 0), 100)
        
        if score > 60: state = "RISK_OFF"
        elif score < 40: state = "RISK_ON"
        else: state = "NEUTRAL"

        result = {
            "state": state,
            "score": score,
            "summary": f"Market stance is {state}. {', '.join(drivers)}.",
            "drivers": drivers,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
            
        print(f"[RiskEngine] Analysis completed: {state}")
        return result

if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent
    engine = RiskEngine(project_root)
    engine.run_analysis()
