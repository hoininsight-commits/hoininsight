import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

class MemoryEngine:
    """
    (IS-23) Prevents repetitive issuance of structurally identical triggers.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.memory_path = base_dir / "data" / "issuesignal" / "market_memory.json"
        self._ensure_storage()

    def _ensure_storage(self):
        if not self.memory_path.exists():
            self.memory_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.memory_path, "w", encoding="utf-8") as f:
                json.dump([], f)

    def check_duplication(self, new_trigger: Dict[str, Any]) -> tuple[bool, str]:
        """
        Checks if the new trigger is a structural duplicate.
        Returns (is_duplicate, reason).
        """
        new_hash = self._generate_hash_dict(new_trigger)
        memories = self._load_memories()
        now = datetime.now()

        for mem in memories:
            mem_time = datetime.fromisoformat(mem["timestamp"])
            age_days = (now - mem_time).days
            mem_hash = mem["hash"]

            overlap_score = self._calculate_overlap(new_hash, mem_hash)

            # 1. High Overlap (>= 70%) Block
            if overlap_score >= 0.7:
                if age_days < 21:
                    return True, f"STRUCTURAL DUPLICATION (Overlap: {overlap_score*100:.0f}%, Age: {age_days}d)"
                elif age_days < 45:
                    # Soft lock: Only if Destination or Irreversibility changes
                    if new_hash["destination"] == mem_hash["destination"] and \
                       new_hash["irreversibility"] == mem_hash["irreversibility"]:
                        return True, f"SOFT LOCK: High overlap without significant structural evolution (Age: {age_days}d)"

            # 2. Moderate Overlap (40-70%) Block
            elif 0.4 <= overlap_score < 0.7:
                if age_days < 21:
                    # Block unless Actor OR Destination changes
                    if new_hash["actor"] == mem_hash["actor"] and \
                       new_hash["destination"] == mem_hash["destination"]:
                        return True, f"REPETITIVE NARRATIVE: Actor and Destination unchanged (Overlap: {overlap_score*100:.0f}%)"

        return False, ""

    def record_issuance(self, trigger_data: Dict[str, Any]):
        """
        Records the issuance of a new trigger.
        """
        new_hash = self._generate_hash_dict(trigger_data)
        memories = self._load_memories()
        
        memories.append({
            "timestamp": datetime.now().isoformat(),
            "hash": new_hash,
            "issue_id": trigger_data.get("issue_id", "UNKNOWN")
        })
        
        # Keep memory concise (expire after 45 days)
        cutoff = datetime.now() - timedelta(days=45)
        memories = [m for m in memories if datetime.fromisoformat(m["timestamp"]) > cutoff]

        with open(self.memory_path, "w", encoding="utf-8") as f:
            json.dump(memories, f, indent=2, ensure_ascii=False)

    def _generate_hash_dict(self, trigger: Dict[str, Any]) -> Dict[str, str]:
        return {
            "root_cause": str(trigger.get("root_cause", "")).upper(),
            "actor": str(trigger.get("actor", "")).upper(),
            "destination": str(trigger.get("destination", "")).upper(),
            "irreversibility": "YES" if trigger.get("irreversible", False) else "NO"
        }

    def _calculate_overlap(self, hash1: Dict[str, str], hash2: Dict[str, str]) -> float:
        matches = 0
        keys = ["root_cause", "actor", "destination", "irreversibility"]
        for k in keys:
            if hash1[k] == hash2[k]:
                matches += 1
        return matches / len(keys)

    def _load_memories(self) -> List[Dict[str, Any]]:
        try:
            with open(self.memory_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
