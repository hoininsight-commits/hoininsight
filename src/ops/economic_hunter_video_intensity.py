import json
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

class EconomicHunterVideoIntensityLayer:
    """
    Step 77: ECONOMIC_HUNTER_VIDEO_INTENSITY_LAYER
    Determines the production intensity level for locked Economic Hunter topics.
    """

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.logger = logging.getLogger("EconomicHunterVideoIntensityLayer")

    def _load_json(self, path: Path) -> Dict:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except Exception as e:
            self.logger.error(f"Failed to load {path}: {e}")
            return {}

    def _save_json(self, path: Path, data: Dict):
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')

    def decide_intensity(self) -> Dict[str, Any]:
        """
        Evaluate and decide the Video Intensity Level.
        """
        # 1. Load Inputs
        top1_path = self.base_dir / "data/ops/structural_top1_today.json"
        narrative_path = self.base_dir / "data/ops/issue_signal_narrative_today.json"
        
        top1_data = self._load_json(top1_path)
        narrative_data = self._load_json(narrative_path)
        
        if not top1_data.get("top1_topics") or not narrative_data.get("narrative"):
            self.logger.error("Missing required inputs.")
            return {"status": "error", "reason": "Missing inputs"}

        topic = top1_data["top1_topics"][0]
        narrative = narrative_data["narrative"]

        # ABSOLUTE RULE 1: Only run if topic_lock == True
        if not topic.get("topic_lock"):
            self.logger.info("Topic not locked. Skipping intensity decision.")
            return {"status": "skipped", "reason": "Topic not locked"}

        # Extraction of logic variables
        original_card = topic.get("original_card", {})
        ps_signal = original_card.get("pre_structural_signal", {})
        whynow_trigger = narrative.get("whynow_trigger", {})
        
        trigger_id = whynow_trigger.get("id", 0)
        days_to_event = self._extract_days_to_event(ps_signal.get("temporal_anchor", ""))
        entities_count = len(ps_signal.get("related_entities", []))
        structure_type = original_card.get("structure_type", "")
        # For DEEP_HUNT detection of history
        has_history = self._check_signal_accumulation(original_card.get("dataset_id"))

        intensity_level = None
        reason = ""

        # DECISION LOGIC (DETERMINISTIC IF/ELSE ONLY)
        
        # LEVEL 1 — FLASH
        if (trigger_id in [1, 2]) and (days_to_event is not None and days_to_event <= 7):
            intensity_level = "FLASH"
            reason = f"Highly urgent trigger (ID:{trigger_id}) with tight deadline ({days_to_event}d)"
        
        # LEVEL 2 — STRIKE
        elif (trigger_id > 0) and (structure_type in ["STRUCTURAL_DAMAGE", "STRUCTURAL_REDEFINITION"]) and (entities_count >= 2):
            intensity_level = "STRIKE"
            reason = f"Confirmed structural shift ({structure_type}) involving {entities_count} entities"
            
        # LEVEL 3 — DEEP_HUNT
        elif (trigger_id > 0) and (has_history) and (intensity_level is None):
            intensity_level = "DEEP_HUNT"
            reason = f"Pre-Structural Signal accumulation detected with high structural persistence"

        # ABSOLUTE RULE 2: Reject if level not determined
        if not intensity_level:
            self.logger.warning("Reject: Could not determine Video Intensity Level.")
            topic["is_rejected"] = True
            topic["rejection_reason"] = "Could not determine Video Intensity Level"
            self._save_json(top1_path, top1_data)
            return {"status": "rejected", "reason": "No level determined"}

        # Result Injection
        topic["video_intensity"] = {
            "level": intensity_level,
            "reason": reason
        }
        # For narrative binding later
        narrative["video_intensity"] = topic["video_intensity"]

        # Save results
        self._save_json(top1_path, top1_data)
        self._save_json(narrative_path, narrative_data)
        
        self.logger.info(f"Video Intensity Determined: {intensity_level} ({reason})")
        return topic["video_intensity"]

    def _extract_days_to_event(self, anchor: str) -> Optional[int]:
        """Extracts numeric days from anchor text or ISO dates"""
        if not anchor: return None
        # Look for YYYY-MM-DD
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', anchor)
        if date_match:
            try:
                target_date = datetime.strptime(date_match.group(1), "%Y-%m-%d")
                delta = (target_date - datetime.now()).days
                return delta if delta >= 0 else 0
            except:
                pass
        
        # Look for "D-X"
        d_match = re.search(r'D-(\d+)', anchor, re.IGNORECASE)
        if d_match:
            return int(d_match.group(1))
            
        return None

    def _check_signal_accumulation(self, dataset_id: str) -> bool:
        """Checks if there's significant accumulation in ps_history.json"""
        history_path = self.base_dir / "data/ops/ps_history.json"
        if not history_path.exists(): return False
        try:
            history = json.loads(history_path.read_text(encoding='utf-8'))
            matches = [h for h in history if h.get("dataset_id") == dataset_id]
            return len(matches) >= 3 # 3+ detections over history suggests DEEP_HUNT potential
        except:
            return False
