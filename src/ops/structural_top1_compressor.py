import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Set

class StructuralTop1Compressor:
    """
    Step 66: Structural Redefinition Top-1 Compressor
    Selects ONE representative topic for 'STRUCTURAL_REDEFINITION' structure.
    Deterministic, Non-numeric.
    """
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.logger = logging.getLogger("StructuralTop1Compressor")
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
        self.logger.info(f"Running StructuralTop1Compressor for {self.ymd}...")
        
        # 1. Load IssueSignal Cards
        issues_path = self.base_dir / "data/ops/issuesignal_today.json"
        data = self._load_json(issues_path)
        cards = data.get('cards', [])
        
        # 2. Filter Redefinition Topics
        redef_cards = [c for c in cards if c.get('structure_type') == 'STRUCTURAL_REDEFINITION']
        
        if not redef_cards:
            self._write_empty_result()
            return

        # 3. Select Top-1 (Deterministic Rule)
        # Rule 1: Evidence Count (Scope)
        # Rule 2: Title Length (Clarity - avoid too short/long)
        # Rule 3: Importance Level (High > Medium)
        
        ranked = sorted(redef_cards, key=lambda c: (
            1 if c.get('importance_level') == '높음' else 0, # Priority 1: Importance
            len(c.get('evidence_refs', {}).get('source_ids', [])), # Priority 2: Evidence Count
            -abs(40 - len(c.get('title', ''))), # Priority 3: Title length close to 40 chars (sweet spot)
            c.get('title', '') # Priority 4: Alphabetical stability
        ), reverse=True)
        
        top1 = ranked[0]
        excluded = [{"topic_id": c.get('topic_id'), "reason": "Lower priority in structural group"} for c in ranked[1:]]

        # 4. Format Output
        output_top1 = {
            "structure_type": "STRUCTURAL_REDEFINITION",
            "title": top1.get('title'),
            "one_line_summary": top1.get('one_line_summary'),
            "why_now": top1.get('script_natural', '').split('\n')[0], # First line of script usually serves as hook
            "full_script": top1.get('script_natural'),
            "rationale": top1.get('rationale_natural'),
            "excluded_candidates": excluded,
            "original_card": top1
        }
        
        # 5. Write JSON
        out_json_path = self.base_dir / "data/ops/structural_top1_today.json"
        out_data = {
            "run_date": self.ymd,
            "top1_topics": [output_top1],
            "errors": []
        }
        out_json_path.write_text(json.dumps(out_data, indent=2, ensure_ascii=False), encoding='utf-8')
        
        # 6. Write MD
        out_md_path = self.base_dir / "data/ops/structural_top1_today.md"
        md = f"# 오늘의 구조 재정의 TOP 1 - {self.ymd}\n\n"
        md += f"## 🟣 {top1.get('title')}\n"
        md += f"- **구조 유형**: 구조적 재정의 (공격)\n"
        md += f"- **한 줄 요약**: {top1.get('one_line_summary')}\n"
        md += f"- **왜 지금인가**: {output_top1['why_now']}\n\n"
        
        if excluded:
            md += "### 이 구조에서 제외된 후보들\n"
            for ex in excluded:
                md += f"- {ex['topic_id']}: {ex['reason']}\n"
        else:
            md += "### 단독 후보 선정 (경합 없음)\n"
            
        out_md_path.write_text(md, encoding='utf-8')
        self.logger.info(f"Selected Top-1: {top1.get('title')}")

    def _write_empty_result(self):
        out_json_path = self.base_dir / "data/ops/structural_top1_today.json"
        out_data = {
            "run_date": self.ymd,
            "top1_topics": [],
            "errors": ["No STRUCTURAL_REDEFINITION topics found"]
        }
        out_json_path.write_text(json.dumps(out_data, indent=2, ensure_ascii=False), encoding='utf-8')
        
        out_md_path = self.base_dir / "data/ops/structural_top1_today.md"
        out_md_path.write_text("# 오늘의 구조 재정의 TOP 1\n\n- 해당 유형의 토픽이 감지되지 않았습니다.", encoding='utf-8')

if __name__ == "__main__":
    StructuralTop1Compressor(Path(__file__).resolve().parent.parent.parent).run()
