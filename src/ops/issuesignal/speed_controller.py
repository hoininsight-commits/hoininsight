import time
from pathlib import Path
from typing import Dict, Any

class SpeedController:
    """
    (IS-12) Ensures content is produced within the 10-minute rule.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.start_time = None
        self.cache = {} # Simple in-memory narrative cache
        
    def start_timer(self):
        self.start_time = time.time()
        
    def stop_timer(self) -> float:
        """
        Returns duration in minutes.
        """
        if not self.start_time:
            return 0.0
        duration = (time.time() - self.start_time) / 60.0
        
        if duration > 10.0:
            print(f"[WARNING] Speed Rule Violated: {duration:.2f} mins (Target: <10 mins)")
        
        return duration

    def get_cached_narrative(self, key: str) -> str:
        return self.cache.get(key, "")

    def update_cache(self, key: str, value: str):
        self.cache[key] = value
