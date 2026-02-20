from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from src.ops.structural_memory_engine import StructuralMemoryEngine

class SnapshotComparisonEngine:
    """
    Step 85: Compares today's snapshot with memory (D-1, D-7) to detect 'Flow'.
    """
    
    def __init__(self, memory_engine: StructuralMemoryEngine):
        self.memory = memory_engine
        
    def compare(self, today_date: str, today_snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates the 'Structural Delta'.
        """
        # Load D-1, D-7
        dt = datetime.strptime(today_date, "%Y-%m-%d")
        d1_date = (dt - timedelta(days=1)).strftime("%Y-%m-%d")
        d7_date = (dt - timedelta(days=7)).strftime("%Y-%m-%d")
        
        d1_snap = self.memory.load_snapshot(d1_date)
        d7_snap = self.memory.load_snapshot(d7_date)
        
        result = {
            "d1_date": d1_date,
            "d7_date": d7_date,
            "delta_status": "NEW_TOPIC", # Default
            "intensity_delta": "UNCHANGED",
            "entity_shifts": [],
            "repeat_count": 1
        }
        
        if not d1_snap:
            # No memory of yesterday -> Truly New or First Run
            result["delta_status"] = "NEW_TOPIC"
            return result
            
        # 1. Topic Comparison (Logic Block / Title)
        today_title = today_snapshot.get("top_signal", {}).get("title", "")
        d1_title = d1_snap.get("top_signal", {}).get("title", "")
        
        # Determine if it's the SAME topic (simple title check for now, could be logic_block ID)
        # Assuming title similarity or keyword overlap could be better, but strict equality for Version 1
        is_same_topic = (today_title == d1_title)
        
        if is_same_topic:
            result["delta_status"] = "RECURRING"
            result["repeat_count"] = 2 # At least 2nd day
             # Check D-2, D-3... in real implementation, but here simplify
             
             # 2. Intensity Delta
            today_int = today_snapshot.get("top_signal", {}).get("intensity", "FLASH")
            d1_int = d1_snap.get("top_signal", {}).get("intensity", "FLASH")
            
            int_map = {"FLASH": 1, "STRIKE": 2, "DEEP_HUNT": 3}
            diff = int_map.get(today_int, 1) - int_map.get(d1_int, 1)
            
            if diff > 0: result["intensity_delta"] = "INTENSIFIED"
            elif diff < 0: result["intensity_delta"] = "EASED"
            else: result["intensity_delta"] = "SUSTAINED"
            
            # 3. Entity Shifts
            # Detect upgrades in state (e.g. OBSERVE -> PRESSURE)
            d1_entities = {e["name"]: e for e in d1_snap.get("entities", [])}
            
            for curr_e in today_snapshot.get("entities", []):
                name = curr_e.get("name")
                curr_state = curr_e.get("state")
                
                if name in d1_entities:
                    prev_state = d1_entities[name].get("state")
                    if prev_state != curr_state:
                         result["entity_shifts"].append({
                             "name": name,
                             "from": prev_state,
                             "to": curr_state
                         })
                else:
                    result["entity_shifts"].append({
                        "name": name,
                        "type": "NEW_ENTITY"
                    })
                    
        else:
            result["delta_status"] = "NEW_TOPIC"
            # If topic changed but intensity is high, maybe note that?
            
        return result
