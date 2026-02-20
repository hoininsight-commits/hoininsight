import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

class CapitalPerspectiveNarrator:
    """
    [IS-105] CAPITAL_PERSPECTIVE_NARRATOR
    Generates rule-based narratives for capital flows and internal shifts.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.decision_dir = base_dir / "data" / "decision"
        self.ui_dir = base_dir / "data" / "ui"
        self.export_dir = base_dir / "exports"
        self.export_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger("CapitalPerspectiveNarrator")

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
        units = self.load_json(self.decision_dir / "interpretation_units.json")
        citations = self.load_json(self.decision_dir / "evidence_citations.json")
        hero_lock = self.load_json(self.decision_dir / "hero_topic_lock.json")
        hero_summary = self.load_json(self.ui_dir / "hero_summary.json")

        if not isinstance(units, list): units = []
        if not isinstance(citations, list): citations = []

        # 2. Build Mapping of Citations for Easy Access
        citation_map = {c.get("topic_id"): c.get("citations", []) for c in citations}

        # 3. Generate Content
        # We focus on the current main topic or top unit
        main_topic_id = hero_lock.get("topic_id")
        if not main_topic_id and units:
            main_topic_id = units[0].get("interpretation_id")

        target_unit = next((u for u in units if u.get("interpretation_id") == main_topic_id), units[0] if units else {})
        topic_citations = citation_map.get(main_topic_id, [])

        # Extraction logic for strict schema
        capital_flow = self._generate_capital_flow(target_unit, topic_citations)
        internal_shift = self._generate_internal_shift(target_unit, topic_citations)
        why_now = self._generate_why_now(target_unit)

        perspective = {
            "headline": "돈이 사라진 게 아니라, 이동하고 있다",
            "core_statement": "이번 이슈는 단순한 자금 이탈이 아니라 구조적 자본 재배치 과정입니다.",
            "capital_flow": capital_flow,
            "internal_shift": internal_shift,
            "why_now_capital": why_now,
            "risk_note": "자본 이동은 되돌림이 빠를 수 있으며 단기 변동성은 확대될 수 있음"
        }

        # 4. Save Assets
        output_path = self.ui_dir / "capital_perspective.json"
        output_path.write_text(json.dumps(perspective, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"[NARRATOR] Generated {output_path}")

        # 5. Export Scripts
        self._export_scripts(perspective)

    def _generate_capital_flow(self, unit: Dict, citations: List) -> List[str]:
        flows = []
        tags = unit.get("evidence_tags", [])
        sector = unit.get("target_sector", "핵심 섹터")

        # Rules based on tags and citations
        if "FLOW_ROTATION" in tags:
            # Look for numbers in citations or derivations
            val = unit.get("derived_metrics_snapshot", {}).get("pretext_score", "0.8")
            flows.append(f"외국인은 {sector} 관련 자산을 재배치하며 수급 강도 {val} 수준의 변동을 보이고 있음 (거래소 데이터)")
        
        if "CAPITAL_STRUCTURE" in tags or "US_MA_RUMOR" in tags:
            flows.append(f"M&A 및 구조 개편에 따른 자본 구조 재편이 수급 집중을 유도 중 (공시 및 마켓 데이터)")

        # Fallback if empty to ensure schema compliance but avoid "undefined"
        if not flows:
            flows.append(f"현재 {sector} 시장에서 특정 지점으로 자금 쏠림 현상이 관찰되고 있음 (Derived Data)")

        return flows

    def _generate_internal_shift(self, unit: Dict, citations: List) -> List[str]:
        shifts = []
        tags = unit.get("evidence_tags", [])
        
        if "EARNINGS_VERIFY" in tags:
            shifts.append("단순 이익률 하락이 아닌 내부 R&D 및 인프라 투자로 인한 회계적 착시 가능성 존재")
        
        if unit.get("interpretation_id") == "bb57fa02-f8b1-468d-aaf9-11a8466185b6":
            shifts.append("정책 예산 집행에 따른 공공 부문 매출이 민간 부문 이익으로 전이되는 과정 확인")

        if not shifts:
            shifts.append("기업 내부의 자본 배분 우선순위가 구조적 성장 동력 확보로 이동 중")

        return shifts

    def _generate_why_now(self, unit: Dict) -> List[str]:
        why = []
        why_type = unit.get("why_now_type", "State-driven")
        date = unit.get("as_of_date", datetime.now().strftime("%Y-%m-%d"))

        why.append(f"기준 시점({date}) 전후로 매크로 지표와 수급 전환점이 맞물림")
        if why_type == "Schedule-driven":
            why.append("주요 일정(실적/정책) 발표를 앞두고 선제적 포지션 조정 가속")
        
        return why

    def _export_scripts(self, p: Dict):
        # 1. Shorts: Foreigner Perspective
        s1 = f"제목: 외국인은 왜 여기서 팔고 저기로 갔나\n내용: {p['capital_flow'][0]}\n관점: {p['core_statement']}"
        (self.export_dir / "final_script_capital_shorts_1.txt").write_text(s1, encoding='utf-8')

        # 2. Shorts: Corporate Perspective
        s2 = f"제목: 이익률 착시는 실패가 아니다\n내용: {p['internal_shift'][0]}\n관점: 자금은 사라진 게 아니라 내부에서 돌고 있습니다."
        (self.export_dir / "final_script_capital_shorts_2.txt").write_text(s2, encoding='utf-8')

        # 3. Shorts: Market Perspective
        s3 = f"제목: 돈은 빠진 게 아니라 방향을 바꿨다\n내용: {p['headline']}\n관점: {p['why_now_capital'][0]}"
        (self.export_dir / "final_script_capital_shorts_3.txt").write_text(s3, encoding='utf-8')

        # 4. Long Script
        long = f"# [Long-form] {p['headline']}\n\n## 코어 내러티브\n{p['core_statement']}\n\n## 자본 이동 현황\n"
        long += "\n".join([f"- {i}" for i in p['capital_flow']])
        long += "\n\n## 내부 수급 변화\n"
        long += "\n".join([f"- {i}" for i in p['internal_shift']])
        long += f"\n\n## 리스크 관리\n{p['risk_note']}"
        (self.export_dir / "final_script_capital_long.txt").write_text(long, encoding='utf-8')
        print(f"[NARRATOR] Exported scripts to {self.export_dir}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    narrator = CapitalPerspectiveNarrator(Path("."))
    narrator.run()
