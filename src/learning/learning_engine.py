import json
import os
from pathlib import Path
from datetime import datetime

from src.learning.pattern_extractor import PatternExtractor
from src.learning.performance_aggregator import PerformanceAggregator
from src.learning.pattern_scorer import PatternScorer

class LearningEngine:
    """
    Coordinates the learning process.
    """
    
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.memory_path = self.project_root / "data" / "learning" / "pattern_memory.json"
        self.summary_path = self.project_root / "data" / "learning" / "pattern_summary.json"
        self.log_path = self.project_root / "data" / "operator" / "execution_log.json"
        self.perf_path = self.project_root / "data" / "operator" / "performance_report.json"
        
        # Ensure directories exist
        self.memory_path.parent.mkdir(parents=True, exist_ok=True)

    def load_data(self, path):
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return [] if "log" in str(path) or "report" in str(path) else {}
        return [] if "log" in str(path) or "report" in str(path) else {}

    def run_update(self):
        """
        Updates pattern memory and summary from historical logs.
        """
        print("[LearningEngine] Updating pattern knowledge...")
        
        logs = self.load_data(self.log_path)
        perf_report = self.load_data(self.perf_path)
        
        if not logs:
            print("[LearningEngine] ⚠️ No execution logs found. Skipping update.")
            return

        # 1. Aggregate performance by pattern
        summary_data = PerformanceAggregator.aggregate_by_pattern(logs, perf_report)
        
        # 2. Score patterns
        for pid, data in summary_data.items():
            score = PatternScorer.calculate_score(data["win_rate"], data["avg_return"])
            data["score"] = score
        
        # 3. Save memory (persistent history if needed, but summary is the current state)
        with open(self.memory_path, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)
            
        # 4. Save summary for quick access by decision engine
        with open(self.summary_path, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)
            
        print(f"[LearningEngine] Success: Updated {len(summary_data)} patterns.")

    def get_adjustment_for_pattern(self, pattern_id):
        """
        Retrieves learning adjustment for a specific pattern.
        """
        summary = self.load_data(self.summary_path)
        if not isinstance(summary, dict):
            return 0.0
            
        pattern_data = summary.get(pattern_id)
        if not pattern_data:
            return 0.0
            
        # Safety Mechanism: Minimum sample size
        if pattern_data.get("count", 0) < 5:
            return 0.0
            
        score = pattern_data.get("score", 0.5)
        return PatternScorer.get_adjustment(score)
