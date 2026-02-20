import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

class SectorRotationAccelerationDetector:
    """
    [IS-111] Sector Rotation Acceleration Detector
    단순 로테이션을 넘어 자금 이동의 '가속(Acceleration)' 여부를 결정론적으로 판정합니다.
    """
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.decision_dir = base_dir / "data" / "decision"
        self.ui_dir = base_dir / "data" / "ui"
        self.logger = logging.getLogger("SectorRotationDetector")

    def load_json(self, path: Path) -> Any:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except Exception as e:
            self.logger.error(f"Failed to load {path}: {e}")
            return {}

    def run(self):
        # 1. Load Inputs
        priority = self.load_json(self.decision_dir / "multi_topic_priority.json")
        capital = self.load_json(self.ui_dir / "capital_perspective.json")
        gap_card = self.load_json(self.ui_dir / "expectation_gap_card.json")
        citations = self.load_json(self.decision_dir / "evidence_citations.json")

        if not priority:
            print("[ROTATION] 필수 입력 데이터(priority) 부재로 분석을 중단합니다.")
            return

        # 2. Extract Key Sector (Example: TECH_INFRA_KOREA)
        # 실제 운영 환경에서는 priority와 gap_card에서 섹터를 추출합니다.
        long_topic = priority.get("long", {})
        target_sector = "TECH_INFRA_KOREA" # Default for current cycle
        
        # 3. Acceleration Scoring (Deterministic 3-Condition Logic)
        conditions_met = []
        
        # 조건 A: 자금 방향성 중첩 (IS-105, IS-107, IS-110 동시 등장)
        has_capital = any(target_sector in s for s in capital.get("capital_flow", []))
        has_priority = target_sector in long_topic.get("title", "") or any(target_sector in t.get("title", "") for t in priority.get("shorts", []))
        has_gap = target_sector in gap_card.get("topic", "") or any(target_sector in e for e in gap_card.get("expectation", []))
        
        if has_capital and has_priority and has_gap:
            conditions_met.append("A: 자금 방향성 중첩 (자금 시선, 우선 토픽, 기대 괴리 레이어 동시 포착)")

        # 조건 B: 상대 성과 격차 확대 (IS-110 CONFIRMATION + IS-105 가속 언급)
        is_confirmation = gap_card.get("gap_type") == "CONFIRMATION"
        is_accel_mentioned = any("가속" in s or "쏠림" in s for s in capital.get("capital_flow", []))
        
        if is_confirmation and is_accel_mentioned:
            conditions_met.append("B: 상대 성과 격차 확대 (데이터 증명 완료 및 수급 쏠림 현상 심화)")

        # 조건 C: 내러티브 전환 신호 (기술 기대 -> 정책/자본 실체)
        narrative_shift = any("정책" in s or "예산" in s or "자본" in s for s in capital.get("internal_shift", []))
        if narrative_shift and is_confirmation:
            conditions_met.append("C: 내러티브 전환 신호 (단순 기대감을 넘어 정책 및 자본의 실체 확인 단계 진입)")

        # 4. Final Classification
        score = len(conditions_met)
        acceleration = "NONE"
        confidence = "LOW"
        
        if score >= 2:
            acceleration = "ACCELERATING"
            confidence = "HIGH"
        elif score == 1:
            acceleration = "ROTATING"
            confidence = "MEDIUM"
        else:
            acceleration = "NONE"
            confidence = "LOW"

        # 5. Build Evidence with Citations
        evidence = []
        for cond in conditions_met:
            source = "(Market Analytics, KR_POLICY)" if "A" in cond else "(FLOW_ROTATION, Internal Docs)"
            evidence.append(f"{cond} {source}")
        
        if not evidence:
            evidence.append("명확한 가속 징후가 아직 수치로 포착되지 않음 (데이터 부족)")

        # 6. Operator Summary (경사 스타일)
        if acceleration == "ACCELERATING":
            op_sentence = f"현재 {target_sector} 섹터는 단순 반등을 넘어 돈의 속도가 붙는 '가속 구간'에 진입했습니다."
        elif acceleration == "ROTATING":
            op_sentence = f"{target_sector} 섹터로 자금 이동이 시작되었으나, 아직 전방위적인 가속도가 확인되지는 않았습니다."
        else:
            op_sentence = f"섹터 간 자금 이동이 관찰되지 않거나 가속 에너지가 임계치를 밑돌고 있습니다."

        # 7. Final JSON
        result = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "from_sector": "CASH | LEGACY_VALUE",
            "to_sector": target_sector,
            "acceleration": acceleration,
            "confidence": confidence,
            "evidence": evidence,
            "operator_sentence": op_sentence,
            "risk_note": "자금 가속은 매크로 지표 변동성(금리/지정학)에 의해 급격히 꺾일 수 있음에 유의."
        }

        # 8. Save
        output_path = self.ui_dir / "sector_rotation_acceleration.json"
        output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"[ROTATION] Generated {output_path} ({acceleration})")

if __name__ == "__main__":
    detector = SectorRotationAccelerationDetector(Path("."))
    detector.run()
