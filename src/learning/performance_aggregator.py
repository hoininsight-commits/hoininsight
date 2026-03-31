import json
from pathlib import Path

class PerformanceAggregator:
    """
    Aggregates historical win/loss and returns from execution logs.
    """
    
    @staticmethod
    def aggregate_by_pattern(execution_log, performance_report):
        """
        Groups performance metrics by pattern ID.
        """
        # Create a map of ticker -> metrics from performance report
        perf_map = {}
        for p in performance_report:
            ticker = p.get("ticker")
            if ticker:
                perf_map[ticker] = {
                    "pnl": p.get("pnl", 0.0),
                    "status": p.get("status", "DRAW")
                }
        
        patterns = {}
        
        for entry in execution_log:
            # We need theme_stage and momentum from some historical source or reconstruction
            # For simplicity, we assume the log now contains these or we use the pattern_id
            # if it was already stored. 
            # In the first version of log, these might be missing. 
            # Let's assume the log will be updated to include 'pattern_id' or we reconstruct.
            
            # Reconstruction logic for existing log entries if possible
            # But wait, execution_log.json currently has: date, theme, stock, ticker, action, entry_price, status
            # It lacks evolution_stage and momentum_state!
            
            pattern_id = entry.get("pattern_id")
            if not pattern_id:
                continue
                
            ticker = entry.get("ticker")
            metrics = perf_map.get(ticker, {})
            
            pnl = metrics.get("pnl", 0.0)
            status = metrics.get("status", "DRAW")
            
            if pattern_id not in patterns:
                patterns[pattern_id] = {
                    "count": 0,
                    "wins": 0,
                    "total_return": 0.0,
                    "returns": []
                }
            
            p = patterns[pattern_id]
            p["count"] += 1
            if status == "WIN":
                p["wins"] += 1
            p["total_return"] += pnl
            p["returns"].append(pnl)
            
        # Final calculation
        summary = {}
        for pid, data in patterns.items():
            count = data["count"]
            win_rate = data["wins"] / count if count > 0 else 0
            avg_return = data["total_return"] / count if count > 0 else 0
            
            # Max drawdown calculation
            max_dd = 0
            if data["returns"]:
                max_dd = min(data["returns"]) # Simple logic: worst single trade
            
            summary[pid] = {
                "pattern_id": pid,
                "count": count,
                "win_rate": win_rate,
                "avg_return": avg_return,
                "max_drawdown": max_dd
            }
            
        return summary
