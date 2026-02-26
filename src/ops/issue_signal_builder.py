import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

class IssueSignalBuilder:
    """
    Step 64: IssueSignal Topic Card Builder
    Converts Step 63 'Structural Seeds' into operator-facing 'IssueSignal Cards'.
    Read-Only transformation for Dashboard display.
    """
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.logger = logging.getLogger("IssueSignalBuilder")
        self.ymd = datetime.now().strftime("%Y-%m-%d")
        
    def _load_json(self, path: Path) -> Dict:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except Exception as e:
            self.logger.error(f"Failed to load {path}: {e}")
            return {}

    def _build_card(self, seed: Dict) -> Dict:
        """Transform a structural seed into an IssueSignal card."""
        
        # 1. Dataset ID Extraction (Phase 17)
        source_id = seed.get('source_refs', [{}])[0].get('id', '')
        # Handle formats like cand_inflation_pce_fred_20260226 or inflation_pce_fred
        dataset_id = source_id.replace('cand_', '').split('_202')[0] if source_id else "unknown"

        # 2. Map Structure Type to KR
        seed_type = seed.get('seed_type', 'UNKNOWN')
        if seed_type == "STRUCTURAL_DAMAGE":
            structure_kr = "구조적 피해 (방어)"
        elif seed_type == "STRUCTURAL_REDEFINITION":
            structure_kr = "구조적 재정의 (공격)"
        else:
            structure_kr = "구조적 분석"

        # 2. Construct Natural Script
        # Combine summary parts into a coherent paragraph
        summary = seed.get('structure_summary', '').split('] ')[-1] # Remove [Title] prefix if present
        why_now = seed.get('why_now', '')
        misunderstanding = seed.get('market_misunderstanding', '')
        
        script_natural = (
            f"{summary}\n\n"
            f"지금 이 이슈를 주목해야 하는 이유는 {why_now}\n"
            f"시장은 단지 노이즈로 볼 수 있으나, 본질은 {misunderstanding}"
        )

        # 3. Rationale
        rationale = f"HOIN Engine 구조적 분석 결과, '{seed_type}' 유형의 패턴이 감지되었습니다. (드라이버: {', '.join(seed.get('structural_driver', []))})"

        return {
            "topic_id": seed.get('topic_seed_id'),
            "dataset_id": dataset_id,
            "topic_type": "ISSUE_SIGNAL",
            "structure_type": seed_type,
            "structure_card_type": structure_kr, # Display Label
            "title": seed.get('structure_summary', '').split('] ')[0].strip('['), # Extract title from summary "[Title] ..."
            "one_line_summary": summary,
            "importance_level": "보통", # Default logic, can be enhanced
            "intensity": seed.get('intensity', 50.0),
            "rationale_natural": rationale,
            "script_natural": script_natural,
            "evidence_refs": {
                "source_ids": [r['id'] for r in seed.get('source_refs', [])],
                "structural_drivers": seed.get('structural_driver', []),
                "risk_factor": seed.get('risk_side', '')
            }
        }

    def run(self):
        self.logger.info(f"Running IssueSignalBuilder for {self.ymd}...")
        
        # 1. Load Step 63 Output
        seeds_path = self.base_dir / "data/ops/structural_topic_seeds_today.json"
        seeds_data = self._load_json(seeds_path)
        seeds = seeds_data.get('seeds', [])
        
        # 2. Build Cards
        cards = [self._build_card(s) for s in seeds]
        
        # 3. Output JSON & MD
        out_json_path = self.base_dir / "data/ops/issuesignal_today.json"
        out_data = {
            "run_date": self.ymd,
            "count": len(cards),
            "cards": cards
        }
        out_json_path.write_text(json.dumps(out_data, indent=2, ensure_ascii=False), encoding='utf-8')
        
        # Markdown Generation
        out_md_path = self.base_dir / "data/ops/issuesignal_today.md"
        md_content = f"# IssueSignal Topic Cards - {self.ymd}\n\n"
        for c in cards:
            md_content += f"## {c['title']}\n"
            md_content += f"**유형**: {c['structure_card_type']}\n\n"
            md_content += f"**중요도**: {c['importance_level']}\n\n"
            md_content += f"**한 줄 요약**: {c['one_line_summary']}\n\n"
            md_content += "---\n[상세 보기]\n---\n"
            md_content += f"### 주제: {c['title']}\n"
            md_content += f"**자연어 상세 스크립트**:\n{c['script_natural']}\n\n"
            md_content += f"**선정 근거**:\n{c['rationale_natural']}\n\n"
            md_content += f"**근거 데이터**:\n- Drivers: {', '.join(c['evidence_refs']['structural_drivers'])}\n- Risk: {c['evidence_refs']['risk_factor']}\n\n"
            
        out_md_path.write_text(md_content, encoding='utf-8')
        
        # 4. Archive (Step 64-5)
        archive_dir = self.base_dir / "data/ops/archive/issuesignal"
        archive_dir.mkdir(parents=True, exist_ok=True)
        (archive_dir / f"{self.ymd}.json").write_text(json.dumps(out_data, indent=2, ensure_ascii=False), encoding='utf-8')
        (archive_dir / f"{self.ymd}.md").write_text(md_content, encoding='utf-8')
        
        self.logger.info(f"Generated {len(cards)} IssueSignal cards.")

if __name__ == "__main__":
    IssueSignalBuilder(Path(__file__).resolve().parent.parent.parent).run()
