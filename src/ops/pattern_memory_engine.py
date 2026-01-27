from typing import Dict, Any, List, Optional
import json
import hashlib
from pathlib import Path
from datetime import datetime

class PatternMemoryEngine:
    """
    Step 88: Pattern Memory & Replay Engine.
    Stores detected patterns and retrieves historical similar cases.
    """
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.memory_dir = base_dir / "data" / "pattern_memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.memory_dir / "pattern_index.json"
        
    def save_pattern(self, 
                     pattern_id: str, 
                     pattern_data: Dict[str, Any],
                     context: Dict[str, Any]) -> Path:
        """
        Saves a detected pattern to memory.
        """
        # Load existing index
        index = self._load_index()
        
        # Check if pattern already exists
        if pattern_id in index:
            # Update last_seen
            existing_file = self.memory_dir / f"pattern_{pattern_id}.json"
            existing = json.loads(existing_file.read_text(encoding="utf-8"))
            existing["last_seen_at"] = datetime.utcnow().isoformat() + "Z"
            existing["occurrence_count"] = existing.get("occurrence_count", 1) + 1
            existing_file.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")
            return existing_file
        
        # Create new pattern memory
        memory = {
            "pattern_id": pattern_id,
            "first_detected_at": datetime.utcnow().isoformat() + "Z",
            "last_seen_at": datetime.utcnow().isoformat() + "Z",
            "occurrence_count": 1,
            "trigger_type": context.get("trigger", "UNKNOWN"),
            "structural_features": pattern_data.get("signals", []),
            "market_context": pattern_data.get("narrative", ""),
            "outcome_summary": {
                "sector_movement": "TBD (First occurrence)",
                "volatility": "TBD",
                "result_type": "Neutral"
            },
            "reference_date_range": context.get("date", "")
        }
        
        # Save to file
        file_path = self.memory_dir / f"pattern_{pattern_id}.json"
        file_path.write_text(json.dumps(memory, indent=2, ensure_ascii=False), encoding="utf-8")
        
        # Update index
        index[pattern_id] = {
            "first_seen": memory["first_detected_at"],
            "file": f"pattern_{pattern_id}.json"
        }
        self._save_index(index)
        
        return file_path

    def replay(self, current_pattern: Dict[str, Any]) -> Dict[str, Any]:
        """
        Finds historical similar patterns and returns replay block.
        """
        index = self._load_index()
        
        if not index:
            return {
                "replay_found": False,
                "similar_cases": [],
                "common_points": "No historical patterns in memory.",
                "differences": ""
            }
        
        # Extract current pattern signature
        current_features = set(current_pattern.get("signals", []))
        current_type = current_pattern.get("pattern_type", "")
        
        similar_cases = []
        
        for pattern_id, meta in index.items():
            file_path = self.memory_dir / meta["file"]
            if not file_path.exists():
                continue
                
            historical = json.loads(file_path.read_text(encoding="utf-8"))
            hist_features = set(historical.get("structural_features", []))
            
            # Similarity check: at least 2 common features OR same pattern type
            common_features = current_features & hist_features
            
            if len(common_features) >= 2 or (current_type and current_type in pattern_id):
                similar_cases.append({
                    "pattern_id": pattern_id,
                    "first_seen": historical["first_detected_at"],
                    "common_features": list(common_features),
                    "outcome": historical.get("outcome_summary", {})
                })
        
        if not similar_cases:
            return {
                "replay_found": False,
                "similar_cases": [],
                "common_points": "This pattern configuration is new.",
                "differences": ""
            }
        
        # Sort by occurrence count (if available) or date
        similar_cases = sorted(similar_cases, key=lambda x: x["first_seen"], reverse=True)[:3]
        
        # Generate summary
        common_points = f"Similar pattern detected {len(similar_cases)} time(s) in history."
        differences = "Current context may differ in timing or intensity."
        
        return {
            "replay_found": True,
            "similar_cases": similar_cases,
            "common_points": common_points,
            "differences": differences
        }

    def _load_index(self) -> Dict[str, Any]:
        if not self.index_file.exists():
            return {}
        try:
            return json.loads(self.index_file.read_text(encoding="utf-8"))
        except:
            return {}
    
    def _save_index(self, index: Dict[str, Any]):
        self.index_file.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")
