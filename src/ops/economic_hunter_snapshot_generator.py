import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

class EconomicHunterSnapshotGenerator:
    """
    Step 79: ECONOMIC_HUNTER_TOP1_SNAPSHOT_LAYER
    Generates a cognitive snapshot of the Top-1 Economic Hunter topic.
    """

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.logger = logging.getLogger("EconomicHunterSnapshotGenerator")
        self.engine_version = "v1.5.0-Hunter" # Example version

    def _load_json(self, path: Path) -> Dict:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except Exception as e:
            self.logger.error(f"Failed to load {path}: {e}")
            return {}

    def generate_snapshot(self) -> Optional[Path]:
        """
        Generate a snapshot file for today.
        """
        top1_path = self.base_dir / "data/ops/structural_top1_today.json"
        top1_data = self._load_json(top1_path)
        
        if not top1_data.get("top1_topics"):
            self.logger.warning("NO_TOP1_SNAPSHOT_TODAY")
            return None

        topic = top1_data["top1_topics"][0]
        original_card = topic.get("original_card", {})
        
        # ABSOLUTE RULE: Reject if topic_lock == False
        if not topic.get("topic_lock"):
            self.logger.warning("ECONOMIC_HUNTER_LOCK is FALSE. Skipping snapshot.")
            return None

        ymd = datetime.now().strftime("%Y-%m-%d")
        snapshot_dir = self.base_dir / "data/snapshots"
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        snapshot_path = snapshot_dir / f"{ymd}_top1_snapshot.md"

        # Data Extraction
        trigger = topic.get("video_intensity", {}).get("reason", "N/A")
        intensity = topic.get("video_intensity", {}).get("level", "N/A")
        rhythm = topic.get("video_rhythm", {}).get("rhythm_profile", "N/A")
        
        pre_structural = original_card.get("pre_structural_signal", {})
        anchor = pre_structural.get("temporal_anchor", "N/A")
        actor = pre_structural.get("trigger_actor", "N/A")
        rationale = pre_structural.get("rationale", "N/A")
        unresolved = pre_structural.get("unresolved_question", "N/A")
        
        # Snapshot Markdown Construction
        snapshot_content = f"""[ECONOMIC_HUNTER_TOP1_SNAPSHOT]
DATE: {ymd}
PIPELINE_VERSION: {self.engine_version}

[1. WHY NOW — 시간 강제성]
- Trigger Type: {topic.get('whynow_trigger', {}).get('type', 'N/A')}
- Timestamp / Deadline: {anchor}
- 지금 행동하지 않으면 사라지는 것: {rationale}

[2. WHO IS FORCED — 강제된 행위자]
- Actor: {actor}
- 권한 / 결정권의 성격: 시드 데이터 기반 구조적 결정권 보유
- 시간 압박의 원인: {trigger}

[3. WHAT IS BREAKING — 섹터가 아닌 ‘행위’]
- 깨지고 있는 것: {original_card.get('structure_type', 'N/A')} 기반 의사결정 체계
- 연쇄적으로 막히는 흐름: {unresolved}
- 시장이 아직 숫자로 못 본 이유: {pre_structural.get('escalation_path', {}).get('condition_to_upgrade_to_WHY_NOW', 'N/A')}

[4. MARKET BLIND SPOT]
- 아직 반영되지 않은 이유: 데이터 지연 및 정보 비대칭
- 데이터 공백 / 시차: Pre-Structural 단계의 초기 노이즈

[5. MENTIONABLE ASSETS]
- Asset 1: {original_card.get('dataset_id', 'N/A')}
  - 연결 논리: 구조적 변화의 직접 수혜/피해 주체
- Asset 2: Market Proxy
  - 연결 논리: 섹터 전반의 자금 배분 지표
- Asset 3: N/A
  - 연결 논리: (추가 관찰 필요)

[6. SYSTEM DECISION]
- ECONOMIC_HUNTER_LOCK: {topic.get('topic_lock')}
- VIDEO_INTENSITY: {intensity}
- RHYTHM_PROFILE: {rhythm}
"""
        
        snapshot_path.write_text(snapshot_content, encoding='utf-8')
        self.logger.info(f"Snapshot generated at {snapshot_path}")
        return snapshot_path
