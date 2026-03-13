import json
import logging
from pathlib import Path
from datetime import datetime
from collections import Counter
from typing import List, Dict, Any
from src.memory.narrative_memory_store import NarrativeMemoryStore

class NarrativePatternDetector:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.store = NarrativeMemoryStore(base_dir)
        self.logger = logging.getLogger("PatternDetector")

    def run_analysis(self):
        history = self.store.load_history()
        if not history:
            self.logger.warning("No history to analyze.")
            return

        # 1. Topic Frequency
        titles = [h.get("title") for h in history if h.get("title")]
        title_counts = Counter(titles)
        frequent_topics = [{"title": t, "count": c} for t, c in title_counts.most_common(10)]

        # 2. Topic Intervals (Naive calculation)
        interval_map = {}
        for h in history:
            t = h.get("title")
            d = datetime.strptime(h["date"], "%Y-%m-%d")
            if t not in interval_map:
                interval_map[t] = []
            interval_map[t].append(d)

        recurring_patterns = []
        for title, dates in interval_map.items():
            if len(dates) < 2: continue
            dates.sort()
            intervals = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
            avg_interval = sum(intervals) / len(intervals)
            
            recurring_patterns.append({
                "title": title,
                "count": len(dates),
                "avg_interval_days": round(avg_interval, 1),
                "last_seen": dates[-1].strftime("%Y-%m-%d")
            })

        # 3. Emerging (Recently frequent)
        recent_threshold = 30 # last 30 days
        now = datetime.now()
        recent_history = [h for h in history if (now - datetime.strptime(h["date"], "%Y-%m-%d")).days <= recent_threshold]
        recent_titles = [h.get("title") for h in recent_history]
        recent_counts = Counter(recent_titles)
        emerging_topics = [{"title": t, "count": c} for t, c in recent_counts.most_common(5)]

        patterns = {
            "last_updated": datetime.now().isoformat(),
            "frequent_topics": frequent_topics,
            "recurring_patterns": recurring_patterns,
            "emerging_topics": emerging_topics,
            "total_records": len(history)
        }

        self.store.save_patterns(patterns)
        self.logger.info("Pattern analysis completed.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    detector = NarrativePatternDetector(Path("."))
    detector.run_analysis()
