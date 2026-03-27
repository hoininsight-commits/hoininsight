import json
import os
from datetime import datetime
from pathlib import Path

class ExecutionTracker:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.log_path = self.project_root / "data" / "operator" / "execution_log.json"
        
    def _load(self, path):
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def track_execution(self, pattern_id=None):
        print("[ExecutionTracker] Logging daily execution...")
        
        decision = self._load(self.project_root / "data" / "operator" / "investment_decision.json")
        impact = self._load(self.project_root / "data" / "story" / "impact_mentionables.json")
        prices = self._load(self.project_root / "data" / "market" / "price_snapshot.json")
        
        if not decision or not impact or not prices:
            print("⚠️ Missing input data for tracking (Decision/Impact/Prices)")
            return
            
        today = datetime.now().strftime("%Y-%m-%d")
        theme = decision.get("theme", "N/A")
        action = decision.get("decision", {}).get("action", "WATCH")
        
        # Load existing log or init empty list
        current_log = self._load(self.log_path) or []
        
        new_entries = []
        for stock in impact.get("mentionable_stocks", []):
            stock_name = stock.get("stock") or stock.get("name")
            ticker = stock.get("ticker") or stock_name
            price = prices.get(stock_name, {}).get("close")
            
            new_entries.append({
                "date": today,
                "theme": theme,
                "pattern_id": pattern_id,
                "stock": stock_name,
                "ticker": ticker,
                "action": action,
                "entry_price": price,
                "status": "OPEN"
            })
            
        # Deduplicate: Only one entry per stock per day for the same theme
        existing_keys = {(e["date"], e["stock"], e["theme"]) for e in current_log}
        for entry in new_entries:
            if (entry["date"], entry["stock"], entry["theme"]) not in existing_keys:
                current_log.append(entry)
                
        with open(self.log_path, "w", encoding="utf-8") as f:
            json.dump(current_log, f, indent=2, ensure_ascii=False)
            
        print(f"[ExecutionTracker] Log updated: {len(current_log)} total entries.")

if __name__ == "__main__":
    # Test run
    root = Path(__file__).resolve().parent.parent.parent
    tracker = ExecutionTracker(root)
    tracker.track_execution()
