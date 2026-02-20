import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

class EconomicHunterVideoRhythmLayer:
    """
    Step 78: ECONOMIC_HUNTER_VIDEO_RHYTHM_LAYER
    Decides the rhythm, tone, and tempo of the video based on Intensity Level.
    """

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.logger = logging.getLogger("EconomicHunterVideoRhythmLayer")

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

    def assign_rhythm(self) -> Dict[str, Any]:
        """
        Assign rhythm profile based on Intensity Level.
        """
        top1_path = self.base_dir / "data/ops/structural_top1_today.json"
        narrative_path = self.base_dir / "data/ops/issue_signal_narrative_today.json"
        
        top1_data = self._load_json(top1_path)
        narrative_data = self._load_json(narrative_path)
        
        if not top1_data.get("top1_topics") or not narrative_data.get("narrative"):
            self.logger.error("Missing required inputs for Rhythm Layer.")
            return {"status": "error", "reason": "Missing inputs"}

        topic = top1_data["top1_topics"][0]
        narrative = narrative_data["narrative"]

        # ABSOLUTE RULE 1: Only run if topic_lock == True
        if not topic.get("topic_lock"):
            return {"status": "skipped", "reason": "Topic not locked"}

        intensity = topic.get("video_intensity", {})
        intensity_level = intensity.get("level")

        rhythm_profile = None
        style_summary = ""

        # DECISION LOGIC (1:1 MAPPING)
        if intensity_level == "FLASH":
            rhythm_profile = "SHOCK_DRIVE"
            style_summary = "즉각적 결론 선제시, 짧은 호흡의 경고형 템포"
        elif intensity_level == "STRIKE":
            rhythm_profile = "STRUCTURE_FLOW"
            style_summary = "논리적 흐름과 분석적 확신을 담은 표준적 템포"
        elif intensity_level == "DEEP_HUNT":
            rhythm_profile = "DEEP_TRACE"
            style_summary = "심층적 연대기 추적과 신뢰 중심의 교육적 템포"

        # ABSOLUTE RULE 4: Reject if rhythm not determined
        if not rhythm_profile:
            self.logger.warning(f"Reject: Rhythm profile could not be determined for level: {intensity_level}")
            topic["is_rejected"] = True
            topic["rejection_reason"] = "Rhythm profile determination failed"
            self._save_json(top1_path, top1_data)
            return {"status": "rejected", "reason": "No rhythm mapping found"}

        # Result Injection
        rhythm_data = {
            "intensity_level": intensity_level,
            "rhythm_profile": rhythm_profile,
            "narrative_style": style_summary
        }
        topic["video_rhythm"] = rhythm_data
        narrative["video_rhythm"] = rhythm_data

        # Save Results
        self._save_json(top1_path, top1_data)
        self._save_json(narrative_path, narrative_data)
        
        self.logger.info(f"Video Rhythm Assigned: {rhythm_profile} for {intensity_level}")
        return rhythm_data
