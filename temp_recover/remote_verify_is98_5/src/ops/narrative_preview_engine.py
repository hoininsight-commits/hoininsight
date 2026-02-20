import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

def load_json_file(path: Path) -> Optional[Dict[str, Any]]:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning(f"Error reading {path}: {e}")
    return None

class NarrativePreviewEngine:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        
    def generate_no_topic_preview(self, run_ymd: str) -> Dict[str, Any]:
        """Generate deterministic preview for NO_TOPIC state."""
        return {
            "run_date": run_ymd,
            "engine_state": "STEP_96_LOCKED",
            "topic_id": "NO_TOPIC",
            "selection_status": "NO_TOPIC",
            "comparison_alignment": "ALIGNED", # Default assumption if no input
            "divergence_type": "NO_TOPIC_ALIGNMENT",
            "title_candidates": [
                "오늘은 말할 주제가 없다", 
                "NO_TOPIC은 정상 상태다", 
                "오늘의 시장: 구조적 주제 부재"
            ],
            "script": {
                "opening": "오늘은 시장에서 강력한 구조적 신호가 발견되지 않았습니다.",
                "why_now": "특별한 트리거 없음.",
                "structure": "현재 시장은 과도기적 상태이거나 명확한 방향성이 부재함.",
                "caution": "무리한 진입 자제 요망.",
                "closing": "다음 신호를 기다리며 모니터링을 지속합니다."
            },
            "source_refs": [],
            "continuity_flag": True
        }

    def run(self, run_ymd: Optional[str] = None):
        if not run_ymd:
            try:
                from src.utils.target_date import get_target_ymd
                run_ymd = get_target_ymd()
            except ImportError:
                run_ymd = datetime.now().strftime("%Y-%m-%d")
                
        y, m, d = run_ymd.split("-")
        
        # Paths
        top1_path = self.base_dir / "data" / "ops" / "structural_top1_today.json"
        card_path = self.base_dir / "data" / "decision" / y / m / d / "final_decision_card.json"
        comparison_path = self.base_dir / "data" / "judgment_comparison" / y / m / d / "judgment_comparison_view.json"
        
        # Load Inputs
        top1 = load_json_file(top1_path)
        card = load_json_file(card_path)
        comparison = load_json_file(comparison_path)
        
        source_refs = []
        if top1_path.exists(): source_refs.append(str(top1_path))
        if card_path.exists(): source_refs.append(str(card_path))
        if comparison_path.exists(): source_refs.append(str(comparison_path))

        # Check Topic Existence
        # Priority: Comparison Topic > Card Topic > Top1 Topic
        topic_id = "NO_TOPIC"
        base_title = ""
        base_whynow = ""
        base_structure = ""
        base_caution = "확인 필요"
        
        if comparison and comparison.get("topic_id") not in [None, "NO_TOPIC"]:
            topic_id = comparison["topic_id"]
        elif card and card.get("topic_id"):
             topic_id = card["topic_id"]
        elif top1 and top1.get("top1_topics"):
             # top1_topics is usually a list
             if len(top1["top1_topics"]) > 0:
                 topic_id = top1["top1_topics"][0].get("id", "NO_TOPIC")
                 base_title = top1["top1_topics"][0].get("title", "")
                 base_whynow = top1["top1_topics"][0].get("why_now", "")

        # Refine Data
        if card and card.get("topic_id") == topic_id:
             base_title = card.get("title", base_title)
             base_whynow = card.get("why_now_rationale", base_whynow) or card.get("summary", base_whynow)
             if "metrics" in card: # Generic extraction
                 base_caution = card["metrics"].get("risk_factor", base_caution)
        
        # Determine Status fields from Comparison (preferred)
        selection_status = "NO_TOPIC"
        alignment = "ALIGNED"
        div_type = ""
        
        if comparison:
            selection_status = comparison.get("engine_side", {}).get("engine_decision", "NO_TOPIC")
            alignment = comparison.get("delta_interpretation", {}).get("alignment_status", "ALIGNED")
            div_type = comparison.get("delta_interpretation", {}).get("divergence_type", "")
        elif card:
            # Fallback
            is_locked = card.get("decision", {}).get("is_locked", False)
            selection_status = "LOCK" if is_locked else "PASS"
        
        if topic_id == "NO_TOPIC":
            preview = self.generate_no_topic_preview(run_ymd)
            # Carry over comparison logic if available for NO_TOPIC
            if comparison:
                 preview["comparison_alignment"] = alignment
                 preview["divergence_type"] = div_type
            preview["source_refs"] = source_refs
            self._write_outputs(preview, y, m, d)
            return preview

        # Build Titles determined deterministically
        titles = [
            f"{base_title} — 시장이 아직 반응하지 않는 진짜 이유",
            f"구조는 움직였는데, 지금은 아닌 이유: {base_title}",
            f"월가가 먼저 움직일 때 생기는 신호: {base_title}"
        ]
        
        # Build Script Structure
        script = {
            "opening": f"오늘 포착된 주제는 '{base_title}'입니다. 시장의 구조적 변화가 감지되었습니다.",
            "why_now": base_whynow[:200] if base_whynow else "명확한 트리거가 데이터상에 존재합니다.",
            "structure": "수급과 매크로 지표가 동시에 임계치를 넘어서고 있습니다." if not base_structure else base_structure,
            "caution": base_caution,
            "closing": "판단에 따라 대응 전략을 수립해야 합니다."
        }
        
        preview = {
            "run_date": run_ymd,
            "engine_state": "STEP_96_LOCKED",
            "topic_id": topic_id,
            "selection_status": selection_status,
            "comparison_alignment": alignment,
            "divergence_type": div_type,
            "title_candidates": titles,
            "script": script,
            "source_refs": source_refs,
            "continuity_flag": True
        }
        
        self._write_outputs(preview, y, m, d)
        return preview

    def _write_outputs(self, preview: Dict[str, Any], y: str, m: str, d: str):
        # JSON Output
        ops_dir = self.base_dir / "data" / "ops"
        ops_dir.mkdir(parents=True, exist_ok=True)
        (ops_dir / "narrative_preview_today.json").write_text(
            json.dumps(preview, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        
        # MD Output (Simple render)
        md_lines = [
            f"# Narrative Preview ({preview['run_date']})",
            f"**Topic**: {preview['topic_id']} | **Status**: {preview['selection_status']}",
            f"**Alignment**: {preview['comparison_alignment']} ({preview['divergence_type']})",
            "",
            "## 🎬 Title Candidates",
        ]
        for t in preview['title_candidates']:
            md_lines.append(f"- {t}")
            
        md_lines.append("\n## 📜 Script Preview")
        scr = preview['script']
        md_lines.append(f"**Opening**: {scr['opening']}")
        md_lines.append(f"**Why Now**: {scr['why_now']}")
        md_lines.append(f"**Structure**: {scr['structure']}")
        md_lines.append(f"**Caution**: {scr['caution']}")
        md_lines.append(f"**Closing**: {scr['closing']}")
        
        (ops_dir / "narrative_preview_today.md").write_text(
            "\n".join(md_lines), encoding="utf-8"
        )

def run_step100_narrative_preview(base_dir: Path = Path(".")):
    engine = NarrativePreviewEngine(base_dir)
    return engine.run()
