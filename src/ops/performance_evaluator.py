import json
from pathlib import Path

class PerformanceEvaluator:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.log_path = self.project_root / "data" / "operator" / "execution_log.json"
        self.report_path = self.project_root / "data" / "operator" / "performance_report.json"
        
    def _load(self, path):
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def evaluate_performance(self):
        print("[PerformanceEvaluator] Calculating PnL...")
        
        log = self._load(self.log_path)
        prices = self._load(self.project_root / "data" / "market" / "price_snapshot.json")
        
        if not log or not prices:
            print("⚠️ Skipping evaluation: No log or price data available.")
            return []
            
        results = []
        for entry in log:
            stock_name = entry["stock"]
            current_price = prices.get(stock_name, {}).get("close")
            entry_price = entry.get("entry_price")
            
            if current_price is None or entry_price is None:
                continue
                
            pnl = (current_price - entry_price) / entry_price
            
            results.append({
                "date": entry["date"],
                "stock": stock_name,
                "ticker": entry.get("ticker"),
                "pnl": round(pnl, 4),
                "status": "WIN" if pnl >= 0 else "LOSS"
            })
            
        with open(self.report_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
            
        print(f"[PerformanceEvaluator] Report saved: {len(results)} items.")
        return results

if __name__ == "__main__":
    # Test run
    root = Path(__file__).resolve().parent.parent.parent
    evaluator = PerformanceEvaluator(root)
    evaluator.evaluate_performance()
