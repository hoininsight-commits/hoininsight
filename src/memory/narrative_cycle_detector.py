import json
import math
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from src.memory.narrative_memory_store import NarrativeMemoryStore

class NarrativeCycleDetector:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.store = NarrativeMemoryStore(base_dir)
        self.logger = logging.getLogger("CycleDetector")
        self.output_path = base_dir / "data" / "memory" / "narrative_cycles.json"

    def run_analysis(self):
        """Analyzes theme cycles from history."""
        history = self.store.load_history()
        if not history:
            self.logger.warning("No history to analyze cycles.")
            return

        # Group dates by theme
        theme_dates = {}
        for h in history:
            theme = h.get("theme")
            if not theme: continue
            date = datetime.strptime(h["date"], "%Y-%m-%d")
            if theme not in theme_dates:
                theme_dates[theme] = []
            theme_dates[theme].append(date)

        cycles = []
        now = datetime.now()

        for theme, dates in theme_dates.items():
            if len(dates) < 2:
                continue
            
            dates.sort()
            intervals = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
            
            # 1. Statistics
            avg_interval = sum(intervals) / len(intervals)
            # Std deviation
            variance = sum((x - avg_interval) ** 2 for x in intervals) / len(intervals)
            std_dev = math.sqrt(variance)
            
            # 2. Cycle Strength (Consistency)
            # Higher strength if std_dev is low compared to avg_interval
            # Penalty for low frequency
            base_strength = max(0, 1 - (std_dev / (avg_interval + 1)))
            freq_multiplier = min(1.0, len(dates) / 5.0)
            cycle_strength = round(base_strength * freq_multiplier, 2)

            # 3. Phase Calculation
            last_seen = dates[-1]
            days_since_last = (now - last_seen).days
            
            # Simplified Phase Logic
            if days_since_last < (avg_interval * 0.3):
                phase = "EARLY"
            elif days_since_last < (avg_interval * 0.7):
                phase = "MID"
            elif days_since_last < (avg_interval * 1.2):
                phase = "LATE"
            else:
                phase = "REACTIVATION"

            # 4. Next Expected Window
            expected_date = last_seen + timedelta(days=avg_interval)
            window_start = (expected_date - timedelta(days=3)).strftime("%Y-%m-%d")
            window_end = (expected_date + timedelta(days=3)).strftime("%Y-%m-%d")
            next_window = f"{window_start} ~ {window_end}"

            # 5. Confidence
            if len(dates) < 3:
                confidence = "LOW"
            elif cycle_strength > 0.7:
                confidence = "HIGH"
            else:
                confidence = "MEDIUM"

            cycles.append({
                "theme": theme,
                "frequency": len(dates),
                "avg_interval_days": round(avg_interval, 1),
                "interval_std": round(std_dev, 1),
                "cycle_strength": cycle_strength,
                "current_cycle_phase": phase,
                "next_expected_window": next_window,
                "cycle_confidence": confidence,
                "last_seen": last_seen.strftime("%Y-%m-%d")
            })

        # Sort by strength and frequency
        cycles.sort(key=lambda x: (x["cycle_strength"], x["frequency"]), reverse=True)

        try:
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            self.output_path.write_text(json.dumps(cycles, indent=2, ensure_ascii=False), encoding="utf-8")
            self.logger.info(f"Cycle analysis completed for {len(cycles)} themes.")
        except Exception as e:
            self.logger.error(f"Failed to save cycles: {e}")

        return cycles

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    detector = NarrativeCycleDetector(Path("."))
    detector.run_analysis()
