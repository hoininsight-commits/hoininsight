import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to sys.path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from src.prediction.liquidity_engine import LiquidityEngine
from src.prediction.macro_regime_engine import MacroRegimeEngine
from src.prediction.risk_engine import RiskEngine
from src.prediction.structural_shift_engine import StructuralShiftEngine

class PredictionRunner:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.output_path = self.project_root / "data" / "ops" / "market_prediction_benchmark.json"

    def run_all(self):
        print("\n" + "="*50)
        print("HOIN Market Prediction Benchmark Engine")
        print("="*50)
        
        # 1. Liquidity Engine
        le = LiquidityEngine(self.project_root)
        liquidity_res = le.run_analysis()
        
        # 2. Macro Regime Engine
        me = MacroRegimeEngine(self.project_root)
        macro_res = me.run_analysis()
        
        # 3. Risk Engine
        re = RiskEngine(self.project_root)
        risk_res = re.run_analysis()
        
        # 4. Structural Shift Engine
        se = StructuralShiftEngine(self.project_root)
        structural_res = se.run_analysis()
        
        # Benchmark Summary Logic
        market_state = f"{liquidity_res['state']} LIQUIDITY + {risk_res['state']} + {macro_res['regime']}"
        if structural_res['active_shifts']:
            market_state += f" + {structural_res['active_shifts'][0]['theme']}"
            
        benchmark_summary = {
            "market_state": market_state,
            "focus": list(set(liquidity_res['drivers'] + risk_res['drivers'] + macro_res['drivers']))[:5]
        }
        
        final_result = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "liquidity": liquidity_res,
            "macro_regime": macro_res,
            "risk": risk_res,
            "structural_shift": structural_res,
            "benchmark_summary": benchmark_summary,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(final_result, f, indent=2, ensure_ascii=False)
            
        print("\n" + "="*50)
        print(f"BENCHMARK COMPLETED: {market_state}")
        print("="*50 + "\n")
        return final_result

if __name__ == "__main__":
    runner = PredictionRunner(project_root)
    runner.run_all()
