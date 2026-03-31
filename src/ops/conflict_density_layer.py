#!/usr/bin/env python3
import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any
from src.ops.conflict_pair_map import get_conflict_candidate

class ConflictDensityLayer:
    """
    Phase 22C: Conflict Density Upgrade Layer
    Enhances topic text density for conflict detection without changing scores.
    No-Behavior-Change: Pure structural enrichment.
    """

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.logger = logging.getLogger("ConflictDensity")
        self.ymd_dash = datetime.now().strftime("%Y-%m-%d")

    def _load_json(self, path: Path) -> Any:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except Exception as e:
            self.logger.error(f"Failed to load {path}: {e}")
            return {}

    def _generate_density_text(self, topic: Dict, decision_card: Dict) -> Dict:
        ds_id = topic.get("dataset_id")
        axes = topic.get("axis", [])
        causal_chain = topic.get("causal_chain", {})
        
        # 1. Axis Combination
        combined_axes = list(axes)
        if len(combined_axes) < 2:
            # Try to supplement from decision/why_now
            why_now = decision_card.get("why_now_type", "Macro")
            if why_now not in combined_axes:
                combined_axes.append(why_now)

        # 2. Structured Paragraph (min 3 lines)
        a_axis = combined_axes[0] if len(combined_axes) > 0 else "Analysis"
        b_axis = combined_axes[1] if len(combined_axes) > 1 else "Market"
        
        summary_text = f"{a_axis} 차원의 시그널과 {b_axis} 차원의 시장 반응이 결합되어 분석 밀도가 보강되었습니다."
        
        paragraph = [
            f"A축({a_axis}): {causal_chain.get('cause', '감지된 구조적 변화')}에 따른 정책적/기술적 압력이 작용하고 있습니다.",
            f"B축({b_axis}): {causal_chain.get('market_consequence', '시장의 실질적 반응')}이(가) 자본 흐름의 변화를 유도하고 있습니다.",
            f"시장반응: 엔진은 현재 {causal_chain.get('structural_shift', 'HOIN_ANOMALY')} 기반의 이상징후를 추적 중입니다.",
            f"상충 가능 지점: 지표상의 긍정적 신호와 실질적 유동성/리스크 선호도 사이의 괴리 여부가 핵심 감시 포인트입니다."
        ]

        # 3. Contradiction Pair Suggestion
        pairs = get_conflict_candidate(ds_id, combined_axes, causal_chain)

        return {
            "summary": summary_text,
            "structured_paragraph": paragraph,
            "contradiction_pairs": pairs
        }

    def run(self):
        self.logger.info(f"Running Conflict Density Layer for {self.ymd_dash}...")
        
        # 1. Load Inputs
        narrative_path = self.base_dir / "data/ops/narrative_intelligence_v2.json"
        narrative_data = self._load_json(narrative_path)
        narrative_topics = narrative_data.get("topics", [])

        decision_path = self.base_dir / "data/decision/today.json" # Fallback to today.json
        if not (self.base_dir / "data/decision/today.json").exists():
             # Try ymd path if today.json is missing in data/decision
             kst_path = datetime.now().strftime("%Y/%m/%d")
             decision_path = self.base_dir / f"data/decision/{kst_path}/final_decision_card.json"
        
        decision_card = self._load_json(decision_path)
        if isinstance(decision_card, list):
            decision_card = decision_card[0] if decision_card else {}

        # 2. Process Topics
        processed_topics = []
        for topic in narrative_topics:
            density = self._generate_density_text(topic, decision_card)
            
            processed_topics.append({
                "dataset_id": topic.get("dataset_id"),
                "title": topic.get("title"),
                "axes": density.get("axes", topic.get("axis", [])), # Ensure axes list
                "inputs_used": {
                    "narrative_present": True,
                    "decision_present": bool(decision_card),
                    "video_candidate": False
                },
                "density_text": density
            })

        # 3. Output Pack
        pack = {
            "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "date_kst": self.ymd_dash,
            "topics": processed_topics
        }

        out_path = self.base_dir / "data/ops/conflict_density_pack.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(pack, indent=2, ensure_ascii=False), encoding='utf-8')
        
        self.logger.info(f"Successfully generated conflict density pack with {len(processed_topics)} topics.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ConflictDensityLayer(Path(".")).run()
