import json
import os
import pandas as pd
from pathlib import Path
from datetime import datetime

class MacroRegimeEngine:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.output_path = self.project_root / "data" / "ops" / "macro_regime.json"
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
            print(f"[MacroRegimeEngine] Error loading {category}/{filename}: {e}")
        return None

    def run_analysis(self):
        print("[MacroRegimeEngine] Analyzing Macro Regime...")
        
        cpi_data = self._get_latest_data("inflation", "cpi.csv")
        gdp_data = self._get_latest_data("macro", "gdp.csv")
        employment_data = self._get_latest_data("employment", "unemployment_rate.csv")
        
        regime = "MID_CYCLE"
        confidence = 0.6
        drivers = []
        
        inflation_status = "STABLE"
        if cpi_data is not None and not cpi_data.empty:
            if len(cpi_data) >= 2:
                cpi_curr = cpi_data.iloc[-1]['value']
                cpi_prev = cpi_data.iloc[-2]['value']
                if cpi_curr > 3.0: 
                    inflation_status = "HIGH"
                    drivers.append(f"Persistence in inflation (CPI: {cpi_curr}%)")
                if cpi_curr > cpi_prev: drivers.append("Inflation pressure increasing")

        growth_status = "STABLE"
        if gdp_data is not None and not gdp_data.empty:
            gdp_val = gdp_data.iloc[-1]['value']
            if gdp_val < 1.5: 
                growth_status = "SLOW"
                drivers.append(f"Sub-trend growth detected (GDP: {gdp_val}%)")
            elif gdp_val > 3.0:
                growth_status = "STRONG"
                drivers.append(f"Strong economic expansion (GDP: {gdp_val}%)")

        # Regime Mapping
        if inflation_status == "HIGH" and growth_status == "SLOW":
            regime = "LATE_CYCLE_TIGHTENING" # Stagflationary hint
        elif growth_status == "STRONG" and inflation_status == "STABLE":
            regime = "MID_CYCLE"
        elif growth_status == "STRONG" and inflation_status == "HIGH":
            regime = "LATE_CYCLE_TIGHTENING"
        elif growth_status == "SLOW" and inflation_status == "STABLE":
            regime = "DISINFLATION_SOFTENING"
        
        if employment_data is not None and not employment_data.empty:
            unemp_rate = employment_data.iloc[-1]['value']
            if unemp_rate > 5.0: drivers.append(f"Labor market loosening (Unemployment: {unemp_rate}%)")
            else: drivers.append(f"Tight labor market (Unemployment: {unemp_rate}%)")

        summary = f"Currently in {regime} regime. {', '.join(drivers)}."

        result = {
            "regime": regime,
            "confidence": confidence,
            "summary": summary,
            "drivers": drivers,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
            
        print(f"[MacroRegimeEngine] Analysis completed: {regime}")
        return result

if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent
    engine = MacroRegimeEngine(project_root)
    engine.run_analysis()
