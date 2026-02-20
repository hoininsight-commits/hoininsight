import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple

class WhyNowEscalationLayer:
    """
    Step 75: WHY_NOW_ESCALATION_LAYER
    Automatically promotes Pre-Structural Signals to WHY_NOW Triggers.
    """
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.logger = logging.getLogger("WhyNowEscalationLayer")
        self.config = self._load_config()
        self.history_path = self.base_dir / "data/ops/ps_history.json"
        self.history = self._load_history()

    def _load_config(self) -> Dict:
        config_path = self.base_dir / "config/escalation_config.json"
        if config_path.exists():
            try:
                return json.loads(config_path.read_text(encoding='utf-8'))
            except:
                pass
        return {"narrative_pressure_threshold": 70, "history_retention_days": 7}

    def _load_history(self) -> List[Dict]:
        if self.history_path.exists():
            try:
                return json.loads(self.history_path.read_text(encoding='utf-8'))
            except:
                pass
        return []

    def _save_history(self):
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        # Keep only relevant history
        cutoff = datetime.now() - timedelta(days=self.config.get("history_retention_days", 7))
        self.history = [h for h in self.history if datetime.fromisoformat(h['detected_at']) > cutoff]
        self.history_path.write_text(json.dumps(self.history, indent=2, ensure_ascii=False), encoding='utf-8')

    def evaluate_signals(self, signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Evaluate and escalate Pre-Structural Signals.
        """
        now_str = datetime.now().isoformat()
        results = []
        
        for sig in signals:
            ps_data = sig.get("pre_structural_signal", {})
            if not ps_data:
                continue
                
            # Update history with this detection
            history_entry = {
                "dataset_id": sig.get("dataset_id"),
                "detected_at": now_str,
                "signal_type": ps_data.get("signal_type"),
                "rationale": ps_data.get("rationale"),
                "score": ps_data.get("narrative_pressure_score", 0)
            }
            self.history.append(history_entry)
            
            # Evaluate Conditions
            cond_a = self._check_time_compression(sig)
            cond_b = self._check_structural_lock(sig)
            cond_c = self._check_forced_decision(sig)
            cond_d = self._check_pressure_threshold(sig)
            
            active_conds = []
            if cond_a: active_conds.append("A")
            if cond_b: active_conds.append("B")
            if cond_c: active_conds.append("C")
            if cond_d: active_conds.append("D")
            
            if len(active_conds) >= 2:
                # ESCALATION
                trigger_id, trigger_name = self._map_trigger(active_conds)
                sig["escalation_status"] = "ESC_WHY_NOW"
                sig["escalation_info"] = {
                    "reason": f"Conditions {', '.join(active_conds)} met",
                    "trigger_id": trigger_id,
                    "trigger_name": trigger_name,
                    "timeline": self._get_timeline(sig.get("dataset_id"))
                }
                # Also inject why_now for WhyNowTriggerLayer/Narrator compatibility
                sig["why_now"] = f"Escalated from Pre-Structural Signal: {ps_data.get('rationale')}"
            else:
                sig["escalation_status"] = "HOLD_PRE_STRUCTURAL"
                
            results.append(sig)
            
        self._save_history()
        return results

    def _check_time_compression(self, sig: Dict) -> bool:
        ds_id = sig.get("dataset_id")
        window = self.config.get("history_retention_days", 7)
        cutoff = datetime.now() - timedelta(days=window)
        
        # Count occurrences of this dataset_id in history
        matches = [h for h in self.history if h['dataset_id'] == ds_id and datetime.fromisoformat(h['detected_at']) > cutoff]
        
        # Condition A: 2 or more times in 7 days
        return len(matches) >= 2

    def _check_structural_lock(self, sig: Dict) -> bool:
        entities = sig.get("pre_structural_signal", {}).get("related_entities", [])
        # Condition B: Clear entity target lock
        return len(entities) > 0

    def _check_forced_decision(self, sig: Dict) -> bool:
        ps_data = sig.get("pre_structural_signal", {})
        stype = ps_data.get("signal_type", "").lower()
        up_cond = ps_data.get("escalation_path", {}).get("condition_to_upgrade_to_WHY_NOW", "").lower()
        
        # Condition C: Deadline or forced action
        keywords = ["deadline", "만기", "시행", "결정", "발표", "vote", "decision", "effective"]
        return stype == "deadline" or any(kw in up_cond for kw in keywords)

    def _check_pressure_threshold(self, sig: Dict) -> bool:
        score = sig.get("pre_structural_signal", {}).get("narrative_pressure_score", 0)
        threshold = self.config.get("narrative_pressure_threshold", 70)
        # Condition D: High Pressure Score
        return score >= threshold

    def _map_trigger(self, conds: List[str]) -> Tuple[int, str]:
        if "A" in conds and "C" in conds:
            return 1, "Scheduled Catalyst Arrival"
        if "B" in conds and "C" in conds:
            return 2, "Mechanism Activation"
        if "A" in conds and "D" in conds:
            return 3, "Smart Money Divergence"
            
        # Default priority if multi-mapped or other 2-combos
        if "C" in conds: return 1, "Scheduled Catalyst Arrival"
        if "B" in conds: return 2, "Mechanism Activation"
        return 3, "Smart Money Divergence"

    def _get_timeline(self, ds_id: str) -> List[str]:
        matches = [h for h in self.history if h['dataset_id'] == ds_id]
        return [f"{h['detected_at'][:16]} (Score: {h['score']})" for h in matches]

if __name__ == "__main__":
    # Test script if needed
    pass
