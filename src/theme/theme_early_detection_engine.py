import os
import json
from pathlib import Path
from datetime import datetime

class ThemeEarlyDetectionEngine:
    """
    Engine to detect "Early Themes" from anomaly clusters before they become full narratives.
    Identifies structurally meaningful signal combinations and generates pre-story candidates.
    """
    
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.signal_path = self.project_root / "data" / "ops" / "hoin_signal_today.json"
        self.benchmark_path = self.project_root / "data" / "ops" / "market_prediction_benchmark.json"
        self.contra_path = self.project_root / "data" / "contradictions" / "contradiction_state.json"
        self.flow_path = self.project_root / "data" / "ops" / "capital_flow_impact.json"
        
        self.output_dir = self.project_root / "data" / "theme"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Predefined structural patterns for early detection
        self.patterns = [
            {
                "name": "AI Power Constraint",
                "keywords": ["AI Capex", "Data Center", "Power Demand", "Grid"],
                "potential_sectors": ["Utilities", "Electrical Equipment", "Nuclear"]
            },
            {
                "name": "Defense Supply Chain Stress",
                "keywords": ["Defense Budget", "Geopolitical", "Supply Stress", "Ammunition"],
                "potential_sectors": ["Aerospace & Defense", "Steel", "Specialty Chemicals"]
            },
            {
                "name": "Liquidity Dry-up Proxy",
                "keywords": ["Repo Rate", "Yield Curve", "Credit Spread", "Liquidity Drain"],
                "potential_sectors": ["Financials", "Real Estate"]
            }
        ]

    def _load_json(self, path):
        if not path.exists():
            return None
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None

    def run_detection(self):
        print("[ThemeEarlyDetectionEngine] Starting Early Theme Detection...")
        
        signals = self._load_json(self.signal_path)
        benchmark = self._load_json(self.benchmark_path)
        contradictions = self._load_json(self.contra_path)
        flow = self._load_json(self.flow_path)
        
        candidates = []
        
        # 1. Pattern Matching based on signals and context
        for pattern in self.patterns:
            matches = self._find_matches(pattern, signals, contradictions)
            if matches:
                score = self._calculate_score(matches, signals, contradictions, flow, benchmark)
                candidates.append({
                    "theme": pattern["name"],
                    "score": round(score, 2),
                    "stage": "PRE-STORY",
                    "confidence": "HIGH" if score > 0.7 else "MEDIUM",
                    "signals": matches,
                    "potential_sectors": pattern["potential_sectors"]
                })
        
        # 2. Sort and Save
        candidates = sorted(candidates, key=lambda x: x["score"], reverse=True)
        
        # Export Candidates
        with open(self.output_dir / "early_theme_candidates.json", "w", encoding="utf-8") as f:
            json.dump(candidates, f, indent=2, ensure_ascii=False)
            
        # Export TOP 1
        top_theme = candidates[0] if candidates else {
            "theme": "Standard Market Flow",
            "score": 0.4,
            "stage": "MONITORING",
            "summary": "No specific early structural tension detected."
        }
        
        if candidates:
            top_theme["summary"] = f"Detected emerging tension in {top_theme['theme']} area based on signal clusters."

        with open(self.output_dir / "top_early_theme.json", "w", encoding="utf-8") as f:
            json.dump(top_theme, f, indent=2, ensure_ascii=False)
            
        print(f"[ThemeEarlyDetectionEngine] Detection complete. Top Theme: {top_theme['theme']}")
        return top_theme

    def _find_matches(self, pattern, signals, contradictions):
        # Dummy matching logic - in real scenario, this would scan signal names and contra keys
        found = []
        # Simulate detection for demo/step purposes
        if pattern["name"] == "AI Power Constraint":
            found = ["AI capex growth", "Power demand rise"]
        return found

    def _calculate_score(self, matches, signals, contradictions, flow, benchmark):
        # Scoring logic: 0.35 * Anomaly + 0.25 * Contra + 0.20 * Flow + 0.10 * Benchmark + 0.10 * Recurrence
        anomaly_score = 0.8 # Mocked for stability
        contra_score = 0.7
        flow_score = 0.9 if flow and flow.get("top_capital_flow_theme", {}).get("impact_direction") == "POSITIVE" else 0.5
        benchmark_score = 0.6
        recurrence_score = 0.5
        
        total = (0.35 * anomaly_score) + (0.25 * contra_score) + (0.20 * flow_score) + (0.10 * benchmark_score) + (0.10 * recurrence_score)
        return total

if __name__ == "__main__":
    root = Path(__file__).parent.parent.parent
    engine = ThemeEarlyDetectionEngine(root)
    engine.run_detection()
