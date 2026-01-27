import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

class IssueSignalNarrativeBuilder:
    """
    Step 67: Issue Signal Narrative Builder
    Transforms the 'Structural Top-1' topic into a human-readable narrative (Script Draft).
    Deterministic, Template-based.
    """
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.logger = logging.getLogger("IssueSignalNarrativeBuilder")
        self.ymd = datetime.utcnow().strftime("%Y-%m-%d")
        
    def _load_json(self, path: Path) -> Dict:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except Exception as e:
            self.logger.error(f"Failed to load {path}: {e}")
            return {}

    def run(self):
        self.logger.info(f"Running IssueSignalNarrativeBuilder for {self.ymd}...")
        
        # 1. Load Structural Top-1
        top1_path = self.base_dir / "data/ops/structural_top1_today.json"
        top1_data = self._load_json(top1_path)
        
        top1_list = top1_data.get('top1_topics', [])
        if not top1_list:
            self.logger.warning("No Top-1 topic found. Skipping narrative generation.")
            self._write_empty_result()
            return

        top1 = top1_list[0]
        original_card = top1.get('original_card', {})
        
        # 2. Extract Fields
        title = top1.get('title', 'Untitled')
        summary = top1.get('one_line_summary', '')
        why_now = top1.get('why_now', '')
        
        evidence = original_card.get('evidence_refs', {})
        drivers = evidence.get('structural_drivers', [])
        risk = evidence.get('risk_factor', '확인 필요')
        
        # 3. Generate Narrative (Deterministic Templates)
        
        # 3.1 Opening Hook
        # "지금 시장이 이 이슈를 [Title Key Noun] 관점에서 다시 주목하는 이유입니다."
        # Simple extraction of first noun is hard without NLP, so use generic hook.
        opening_hook = f"지금 시장이 '{title}' 이슈를 구조적 관점에서 다시 주목하는 이유입니다."

        # 3.2 Core Story
        # "기존에는 [Old Perspective]로 여겨졌으나, 이제는 [New Structure]로 정의가 바뀌고 있습니다."
        # We don't have "Old Perspective" field strictly, but we can use summary.
        # Template: "[Summary] 흐름은 단순한 일회성 이슈가 아닙니다. ..."
        core_story = (
            f"'{summary}' 흐름은 단순한 일회성 이슈가 아닙니다. "
            f"기존의 시장 인식과 달리, 현재의 변화는 구조적인 재정의(Structural Redefinition) 단계로 진입하고 있습니다. "
            f"이러한 변화는 업의 본질이 바뀌고 있음을 시사합니다."
        )

        # 3.3 Risk Note
        risk_note = f"구조적 변화는 명확하지만, '{risk}' 부분은 여전히 검증이 필요한 핵심 변수입니다."

        # 4. Construct Output Object
        narrative = {
            "topic_id": original_card.get('topic_id'),
            "title": title,
            "narrative_type": "STRUCTURAL_REDEFINITION",
            "opening_hook": opening_hook,
            "core_story": core_story,
            "why_now": why_now,
            "key_drivers": drivers,
            "risk_note": risk_note,
            "source_basis": ["STRUCTURAL_SEED", "ISSUE_SIGNAL"],
            "confidence": "STRUCTURE_BASED"
        }
        
        # 5. Output JSON & MD
        out_json_path = self.base_dir / "data/ops/issue_signal_narrative_today.json"
        out_data = {
            "run_date": self.ymd,
            "narrative": narrative
        }
        out_json_path.write_text(json.dumps(out_data, indent=2, ensure_ascii=False), encoding='utf-8')
        
        # Markdown Output
        out_md_path = self.base_dir / "data/ops/issue_signal_narrative_today.md"
        md = f"# 🟣 오늘의 이슈시그널 TOP-1 Narrative\n\n"
        md += f"## 제목\n{title}\n\n"
        md += f"## 한 줄 요약\n{opening_hook}\n\n"
        md += f"## 구조적 이야기\n{core_story}\n\n"
        md += f"## 왜 지금인가\n{why_now}\n\n"
        md += f"## 핵심 근거\n"
        for d in drivers:
            md += f"- {d}\n"
        md += f"\n## 리스크\n{risk_note}\n"
        
        out_md_path.write_text(md, encoding='utf-8')
        self.logger.info(f"Generated narrative for {title}")

    def _write_empty_result(self):
        out_json_path = self.base_dir / "data/ops/issue_signal_narrative_today.json"
        out_json_path.write_text(json.dumps({"run_date": self.ymd, "narrative": None}, indent=2), encoding='utf-8')
        
        out_md_path = self.base_dir / "data/ops/issue_signal_narrative_today.md"
        out_md_path.write_text("# 오늘의 이슈시그널 TOP-1\n\n- 내러티브 생성 대상 없음.", encoding='utf-8')

if __name__ == "__main__":
    IssueSignalNarrativeBuilder(Path(__file__).resolve().parent.parent.parent).run()
