
import json
from pathlib import Path

class AnomalyOverlay:
    """[TASK #088] ANOMALY OVERLAY
    '정상 흐름 vs 실제 데이터' 비교하여 anomaly 여부 판단
    """
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def overlay_facts(self, interpretations: list, all_data: dict) -> list:
        market_stats = all_data.get("market", {}).get("data", {}).get("multi_period_stats", {})
        results = []
        
        # Asset mapping
        asset_map = {
            "oil": "wti_oil",
            "equity": "sp500",
            "vix": "vix",
            "gold": "gold",
            "dollar": "dxy",
            "bond_yield": "us10y",
            "commodity": "wti_oil" # Default commodity to oil for simplicity
        }
        
        for interp in interpretations:
            expected = interp.get("normal_flow", {}).get("expected_reactions", [])
            actual_summary = {}
            mismatches = []
            
            for exp in expected:
                asset_key = asset_map.get(exp["asset"])
                if not asset_key or asset_key not in market_stats:
                    continue
                
                stats = market_stats[asset_key]
                change = stats.get("chg_5d", 0) or 0 # Using 5d change for more stability
                actual_dir = "UP" if change > 0.1 else "DOWN" if change < -0.1 else "FLAT"
                
                actual_summary[exp["asset"]] = actual_dir
                
                if exp["direction"] != actual_dir:
                    mismatches.append(exp["asset"])
            
            # Anomaly Score: (mismatch count / expected count)
            anomaly_score = len(mismatches) / len(expected) if expected else 0
            
            overlay_res = {
                "event": interp["event"],
                "expected": {e["asset"]: e["direction"] for e in expected},
                "actual": actual_summary,
                "mismatch": mismatches,
                "anomaly_score": round(anomaly_score, 2),
                "is_anomaly": anomaly_score > 0.3
            }
            results.append(overlay_res)
            
        # 결과 저장
        save_path = self.output_dir / "anomaly_results.json"
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        return results
