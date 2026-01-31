import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

class VideoCandidateSelector:
    """
    Step 65: Video Candidate Selection v1.0
    Selects top 1-2 'Video Candidates' from IssueSignal topics based on deterministic 4-point criteria.
    Read-Only: Does not modify engine scores or approval status.
    """
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.logger = logging.getLogger("VideoCandidateSelector")
        self.ymd = datetime.now().strftime("%Y-%m-%d")
        
    def _load_json(self, path: Path) -> Dict:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except Exception as e:
            self.logger.error(f"Failed to load {path}: {e}")
            return {}

    def _evaluate_candidate(self, card: Dict) -> Dict:
        """Evaluate a single IssueSignal card against 4 criteria."""
        
        score_details = []
        score = 0
        
        # Criteria A: Structure Clarity (Always True for IssueSignal)
        # Assuming if it is in IssueSignal list, it has structure.
        if card.get('structure_type') in ["STRUCTURAL_DAMAGE", "STRUCTURAL_REDEFINITION"]:
            score += 1
            score_details.append("STRUCTURAL_PATTERN_CLEAR")
            
        # Criteria B: Audience Relevance (Damage/Redefinition imply relevance)
        # Heuristic: All Structural items are relevant by definition of Step 63 rules.
        score += 1
        score_details.append("GENERAL_AUDIENCE_RELEVANT")
            
        # Criteria C: Time Sensitivity (Today's signal)
        # Implicitly true for this pipeline run
        score += 1
        score_details.append("TIME_SENSITIVE")
            
        # Criteria D: Scope/Extendibility (Drivers check)
        drivers = card.get('evidence_refs', {}).get('structural_drivers', [])
        if drivers and len(drivers) > 0:
            score += 1
            score_details.append(f"EXTENDIBLE_SCOPE({len(drivers)})")
            
        # Tie-breaker priority
        priority = 2 if card.get('structure_type') == "STRUCTURAL_DAMAGE" else 1
        
        return {
            "card": card,
            "score": score,
            "priority": priority,
            "details": score_details
        }

    def _generate_why_text(self, card: Dict) -> str:
        s_type = card.get('structure_type')
        title = card.get('title')
        
        if s_type == "STRUCTURAL_DAMAGE":
            return f"구조적 피해 관점에서 '{title}' 이슈는 시청자들에게 즉각적인 리스크 대응 필요성을 주기 때문에 선정"
        elif s_type == "STRUCTURAL_REDEFINITION":
            return f"구조적 재정의 관점에서 '{title}' 이슈는 시청자들에게 새로운 투자 기회를 제시하기 때문에 선정"
        else:
            return f"구조적 중요도가 높아 영상으로 다루기 적합함"

    def run(self):
        self.logger.info(f"Running VideoCandidateSelector for {self.ymd}...")
        
        # 1. Load IssueSignal Cards
        issues_path = self.base_dir / "data/ops/issuesignal_today.json"
        data = self._load_json(issues_path)
        cards = data.get('cards', [])
        
        if not cards:
            self.logger.warning("No IssueSignal cards found.")
            return

        # 2. Evaluate & Rank
        evaluated = []
        for c in cards:
            evaluated.append(self._evaluate_candidate(c))
            
        # Sort: Score Desc, Priority Desc
        evaluated.sort(key=lambda x: (x['score'], x['priority']), reverse=True)
        
        # 3. Select Top 2
        top_candidates = evaluated[:2]
        
        # 4. Format Output
        output_candidates = []
        for item in top_candidates:
            c = item['card']
            # Filter low scores? (Step 65-2: 2 or less excluded)
            if item['score'] <= 2:
                continue
                
            cand = {
                "topic_id": c.get('topic_id'),
                "title": c.get('title'),
                "signal_type": c.get('structure_type'),
                "importance": "HIGH" if item['score'] >= 4 else "MEDIUM",
                "why_selected": item['details'],
                "risk_note": c.get('evidence_refs', {}).get('risk_factor', ''),
                "why_video_natural": self._generate_why_text(c)
            }
            output_candidates.append(cand)
            
        # 5. Output JSON & MD
        out_json_path = self.base_dir / "data/ops/video_candidates_today.json"
        out_data = {
            "date": self.ymd,
            "candidates": output_candidates
        }
        out_json_path.write_text(json.dumps(out_data, indent=2, ensure_ascii=False), encoding='utf-8')
        
        # MD Output
        out_md_path = self.base_dir / "data/ops/video_candidates_today.md"
        md = f"# Video Candidates - {self.ymd}\n\n"
        if not output_candidates:
            md += "선정된 영상 후보 없음.\n"
        else:
            for c in output_candidates:
                md += f"## 🎥 {c['title']}\n"
                md += f"- **Why Video**: {c['why_video_natural']}\n"
                md += f"- **Criteria**: {', '.join(c['why_selected'])}\n"
                md += f"- **Importance**: {c['importance']}\n\n"
        
        out_md_path.write_text(md, encoding='utf-8')
        self.logger.info(f"Selected {len(output_candidates)} video candidates.")

if __name__ == "__main__":
    VideoCandidateSelector(Path(__file__).resolve().parent.parent.parent).run()
