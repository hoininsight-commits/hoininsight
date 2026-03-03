#!/usr/bin/env python3
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

class VideoScriptIntelligenceLayer:
    """
    Phase 22A: Script Intelligence Layer
    Transforms video candidates into structured scripts for production.
    """

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.logger = logging.getLogger("VideoScriptIntelligence")
        self.ymd_dash = datetime.now().strftime("%Y-%m-%d")
        self.ymd_path = datetime.now().strftime("%Y/%m/%d")

    def _load_json(self, path: Path) -> Any:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except Exception as e:
            self.logger.error(f"Failed to load {path}: {e}")
            return {}

    def _generate_script(self, candidate: Dict, narrative_topics: List[Dict], decision_card: Dict) -> Dict:
        ds_id = candidate.get("dataset_id")
        title = candidate.get("title", "Unknown Topic")
        
        narrative = next((t for t in narrative_topics if t.get("dataset_id") == ds_id), {})
        causal = narrative.get("causal_chain", {})
        if not causal:
            causal = decision_card.get("causal_chain", {})

        hook = f"여러분, 지금 시장이 {title.split(':')[-1].strip()}에 ‘다시’ 반응하는 이유가 있습니다."
        if narrative.get("conflict_flag"):
            hook = f"지금 {title.split(':')[-1].strip()}를 둘러싸고 시장의 해석이 충돌하고 있습니다. 본질을 보셔야 합니다."

        summary = narrative.get("summary_3_line", "")
        if summary and isinstance(summary, str):
            summary_lines = [line.strip() for line in summary.split('\n') if line.strip()][:3]
        else:
            summary_lines = [
                f"구조적 원인: {causal.get('structural_shift', 'HOIN_ANOMALY')} 감지",
                f"자본 흐름: {causal.get('market_consequence', 'Monitoring friction')}",
                f"리스크 포인트: 지표 발표 일정에 따른 실질 반응 여부 추가 검증 필요"
            ]
        
        evidence_refs = narrative.get("evidence_refs", {})
        evidence_bullets = []
        if evidence_refs:
            drivers = evidence_refs.get("structural_drivers", [])
            risk = evidence_refs.get("risk_factor", "N/A")
            if drivers:
                evidence_bullets.append(f"구조적 드라이버: {', '.join(drivers)}")
            evidence_bullets.append(f"주요 리스크: {risk}")
        else:
            evidence_bullets.append("엔진 데이터셋 기반 이상징후 포착")

        mentionables = []
        if "inflation" in ds_id or "rates" in ds_id:
            mentionables.append({"ticker": "KB금융", "reason": "금리 민감주", "risk": "순이자마진(NIM) 정점 우려"})
            mentionables.append({"ticker": "신한지주", "reason": "배당 매력", "risk": "부동산 PF 리스크"})
        
        return {
            "hook": hook,
            "one_min_summary_3lines": summary_lines,
            "causal_chain": causal,
            "evidence_bullets": evidence_bullets,
            "mentionables": mentionables,
            "closing": "정리하면, 지금은 ‘수치’가 아니라 ‘반응’이 바뀌는 구간입니다. HOIN Insight였습니다."
        }

    def run(self):
        self.logger.info(f"Generating Video Script Pack for {self.ymd_dash}...")
        pool_path = self.base_dir / "data_outputs/ops/video_candidate_pool.json"
        pool_data = self._load_json(pool_path)
        candidates = pool_data.get("top_candidates", [])

        narrative_path = self.base_dir / "data/ops/narrative_intelligence_v2.json"
        narrative_data = self._load_json(narrative_path)
        narrative_topics = narrative_data.get("topics", [])

        decision_path = self.base_dir / f"data/decision/{self.ymd_path}/final_decision_card.json"
        decision_card = self._load_json(decision_path)

        script_candidates = []
        for cand in candidates:
            script_data = self._generate_script(cand, narrative_topics, decision_card)
            full_cand = cand.copy()
            full_cand["script"] = script_data
            script_candidates.append(full_cand)

        pack = {
            "generated_at": datetime.now().isoformat() + "Z",
            "date_kst": self.ymd_dash,
            "candidates": script_candidates
        }

        json_out = self.base_dir / "data_outputs/ops/video_script_pack.json"
        json_out.parent.mkdir(parents=True, exist_ok=True)
        json_out.write_text(json.dumps(pack, indent=2, ensure_ascii=False), encoding='utf-8')

        md_content = f"# HOIN Insight Video Script Pack ({self.ymd_dash})\n\n"
        for i, cand in enumerate(script_candidates, 1):
            s = cand["script"]
            md_content += f"## 후보 {i}: {cand['title']}\n"
            md_content += f"- **Stats**: Intensity {cand['intensity']} | Narrative {cand['narrative_score']} | Video {cand['video_score']}\n"
            md_content += f"- **Type**: {cand['why_now_type']}\n\n"
            md_content += f"### [Hook]\n> {s['hook']}\n\n"
            md_content += f"### [1분 요약]\n"
            for line in s['one_min_summary_3lines']:
                md_content += f"- {line}\n"
            md_content += "\n### [인과 사슬]\n"
            md_content += f"- 원인: {s['causal_chain'].get('cause', 'N/A')}\n"
            md_content += f"- 구조적 변화: {s['causal_chain'].get('structural_shift', 'N/A')}\n"
            md_content += f"- 시장 결과: {s['causal_chain'].get('market_consequence', 'N/A')}\n\n"
            md_content += f"### [핵심 근거]\n"
            for b in s['evidence_bullets']:
                md_content += f"- {b}\n"
            md_content += "\n### [언급 가능 종목]\n"
            for m in s['mentionables']:
                md_content += f"- **{m['ticker']}**: {m['reason']} (리스크: {m['risk']})\n"
            md_content += "\n### [Closing]\n> {s['closing']}\n\n---\n\n"

        md_out = self.base_dir / "data_outputs/ops/video_script_pack.md"
        md_out.write_text(md_content, encoding='utf-8')
        self.logger.info(f"Successfully generated script pack with {len(script_candidates)} candidates.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    VideoScriptIntelligenceLayer(Path(".")).run()
