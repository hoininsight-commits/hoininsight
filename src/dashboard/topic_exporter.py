import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from src.ops.human_interpretation_layer import HumanInterpretationLayer

class TopicExporter:
    """
    Step 85: Topic Exporter
    Mirrors engine-selected topics to static JSON for GitHub Pages dashboard.
    """

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.logger = logging.getLogger("TopicExporter")
        self.ymd = datetime.utcnow().strftime("%Y-%m-%d")
        self.export_root = base_dir / "docs/topics"
        self.export_items = self.export_root / "items"
        
        self.export_items.mkdir(parents=True, exist_ok=True)

    def _load_json(self, path: Path) -> Dict:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except Exception as e:
            self.logger.error(f"Failed to load {path}: {e}")
            return {}

    def run(self, target_date: str = None):
        ymd = target_date or self.ymd
        self.logger.info(f"Running TopicExporter for {ymd}...")

        # 1. Load Sources
        top1_path = self.base_dir / "data/ops/structural_top1_today.json"
        narrative_path = self.base_dir / "data/ops/issue_signal_narrative_today.json"
        
        # If running for past dates, we might need to look at archives
        if target_date and target_date != self.ymd:
            # Simple archive lookup for Step 85 demo
            archive_path = self.base_dir / f"data/ops/archive/issuesignal/{ymd}.json"
            if archive_path.exists():
                archive_data = self._load_json(archive_path)
                cards = archive_data.get('cards', [])
                if cards:
                    # Mock a top-1 if we are backfilling from archive
                    top1_topics = [{"original_card": cards[0], "title": cards[0].get('title'), "one_line_summary": cards[0].get('one_line_summary')}]
                else:
                    top1_topics = []
            else:
                top1_topics = []
        else:
            top1_data = self._load_json(top1_path)
            top1_topics = top1_data.get('top1_topics', [])

        narrative_data = self._load_json(narrative_path).get('narrative', {})
        if not narrative_data:
            narrative_data = {}

        if not top1_topics:
            self.logger.warning(f"No Top-1 topics found for {ymd}. Skipping export.")
            return

        # 2. Process Top-1
        top1 = top1_topics[0]
        orig = top1.get('original_card', {})
        
        # Build TopicCard v1
        # Summary 3 lines logic
        raw_summary = top1.get('one_line_summary', '')
        summary_lines = [raw_summary] if raw_summary else []
        # If summary is long, we could split it, but for now we keep as is or wrap
        
        why_now_trigger = narrative_data.get('whynow_trigger', {})
        evidence_ids = orig.get('evidence_refs', {}).get('source_ids', [])
        
        # Badges
        v_intensity = narrative_data.get('video_intensity', {})
        v_rhythm = narrative_data.get('video_rhythm', {})
        
        topic_card = {
            "topic_id": orig.get('topic_id', 'unknown'),
            "date": ymd,
            "rank": 1,
            "title": top1.get('title', 'Untitled Topic'),
            "summary": summary_lines,
            "why_now": {
                "type": why_now_trigger.get('type', 'Mechanism Activation'),
                "anchor": why_now_trigger.get('anchor', 'Detected Pattern'),
                "evidence": evidence_ids[:3] # Max 3 for summary
            },
            "badges": {
                "intensity": v_intensity.get('level', 'STRIKE'),
                "rhythm": v_rhythm.get('rhythm_profile', 'STRUCTURE_FLOW'),
                "scope": "MULTI" if len(evidence_ids) > 1 else "SINGLE",
                "lock": True,
                "rejected": narrative_data.get('is_rejected', False)
            },
            "entities": [], # Entity extraction removed to avoid mock data
            "body_md": self._generate_body_md(narrative_data),
            "source_refs": [str(top1_path.relative_to(self.base_dir))]
        }
        topic_card["human_interpretation"] = HumanInterpretationLayer.interpret(topic_card) # Step 89

        # Save Item
        item_filename = f"{ymd}__top1.json"
        item_path = self.export_items / item_filename
        item_path.write_text(json.dumps(topic_card, indent=2, ensure_ascii=False), encoding='utf-8')
        
        # 3. Update Index
        index_path = self.export_root / "index.json"
        index_data = self._load_json(index_path)
        if not isinstance(index_data, list):
            index_data = []
            
        # Update or add entry
        entry = {
            "date": ymd,
            "rank": 1,
            "title": topic_card["title"],
            "path": f"topics/items/{item_filename}",
            "intensity": topic_card["badges"]["intensity"],
            "scope": topic_card["badges"]["scope"],
            "why_now_type": topic_card["why_now"]["type"]
        }
        
        # Remove existing for same date
        index_data = [e for e in index_data if e["date"] != ymd]
        index_data.insert(0, entry) # Most recent first
        
        # Keep only top 30
        index_data = index_data[:30]
        
        index_path.write_text(json.dumps(index_data, indent=2, ensure_ascii=False), encoding='utf-8')
        self.logger.info(f"Exported Top-1 to {item_path} and updated index.")

    def _generate_body_md(self, narrative_data: Dict) -> str:
        if not narrative_data:
            return ""
        
        sections = narrative_data.get('sections', {})
        md = f"### 🏹 Economic Hunter Narrative\n\n"
        md += f"**Hook**: {sections.get('hook', 'N/A')}\n\n"
        md += f"**Tension**: {sections.get('tension', 'N/A')}\n\n"
        md += f"**Hunt**: {sections.get('hunt', 'N/A')}\n\n"
        md += f"**Action**: {sections.get('action', 'N/A')}\n"
        return md

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    exporter = TopicExporter(Path(__file__).resolve().parent.parent.parent)
    exporter.run()
