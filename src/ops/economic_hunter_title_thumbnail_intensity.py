import json
import logging
from pathlib import Path
from typing import Dict, Any

class EconomicHunterTitleThumbnailIntensityLayer:
    """
    Step 79: ECONOMIC_HUNTER_TITLE_THUMBNAIL_INTENSITY_LAYER
    Determines the attack intensity for video titles and thumbnail messages.
    """

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.logger = logging.getLogger("EconomicHunterTitleThumbnailIntensityLayer")

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

    def assign_intensity(self) -> Dict[str, Any]:
        """
        Assign title and thumbnail intensity based on Video Intensity.
        """
        top1_path = self.base_dir / "data/ops/structural_top1_today.json"
        narrative_path = self.base_dir / "data/ops/issue_signal_narrative_today.json"
        
        top1_data = self._load_json(top1_path)
        narrative_data = self._load_json(narrative_path)
        
        if not top1_data.get("top1_topics") or not narrative_data.get("narrative"):
            self.logger.error("Missing required inputs for Title Intensity Layer.")
            return {"status": "error", "reason": "Missing inputs"}

        topic = top1_data["top1_topics"][0]
        narrative = narrative_data["narrative"]

        # ABSOLUTE RULE: Only run if topic_lock == True
        if not topic.get("topic_lock"):
            return {"status": "skipped", "reason": "Topic not locked"}

        v_intensity = topic.get("video_intensity", {})
        v_level = v_intensity.get("level")
        r_profile = topic.get("video_rhythm", {}).get("rhythm_profile")

        title_intensity = None
        rules_str = ""

        # DECISION LOGIC (1:1 MAPPING)
        if v_level == "FLASH":
            title_intensity = "TITLE_INTENSITY_FLASH"
            rules_str = "12자 내외, 긴급 키워드(지금, 오늘 등) 포함, 단어 3~5개 썸네일"
        elif v_level == "STRIKE":
            title_intensity = "TITLE_INTENSITY_STRIKE"
            rules_str = "15~18자, 원인-결과 구조, 단어 4~6개 썸네일"
        elif v_level == "DEEP_HUNT":
            title_intensity = "TITLE_INTENSITY_DEEP"
            rules_str = "18~25자, 질문/설명형, 단어 5~7개 개념 키워드 썸네일"

        # ABSOLUTE RULE: Reject if intensity not determined
        if not title_intensity:
            self.logger.warning(f"Reject: Title Intensity could not be determined for level: {v_level}")
            topic["is_rejected"] = True
            topic["rejection_reason"] = "Title Intensity determination failed"
            self._save_json(top1_path, top1_data)
            return {"status": "rejected", "reason": "No mapping found"}

        # Result Injection
        intensity_data = {
            "title_intensity": title_intensity,
            "video_intensity": v_level,
            "rhythm_profile": r_profile,
            "title_rule_applied": True,
            "rules_summary": rules_str
        }
        topic["title_thumbnail_intensity"] = intensity_data
        narrative["title_thumbnail_intensity"] = intensity_data

        # Save Results
        self._save_json(top1_path, top1_data)
        self._save_json(narrative_path, narrative_data)
        
        self.logger.info(f"Title/Thumbnail Intensity Assigned: {title_intensity}")
        return intensity_data
