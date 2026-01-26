from __future__ import annotations
import json
import os
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

class TopicConsoleBuilder:
    """
    Step 55: Aggregates topic-level data, evidence anchors, and script previews
    into a unified review console (JSON + MD).
    Deterministic and read-only.
    """

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.output_json = base_dir / "data" / "ops" / "topic_console_today.json"
        self.output_md = base_dir / "data" / "ops" / "topic_console_today.md"
        self.output_json.parent.mkdir(parents=True, exist_ok=True)

    def run(self, ymd: str) -> Dict[str, Any]:
        """
        Builds the topic console for the given date.
        """
        # 1. Load Inputs
        view_data = self._load_json(self.base_dir / "data" / "ops" / "topic_view_today.json")
        quality_data = self._load_json(self.base_dir / "data" / "ops" / "topic_quality_review_today.json")
        speak_data = self._load_json(self.base_dir / "data" / "ops" / "topic_speakability_today.json")
        auto_approved = self._load_json(self.base_dir / "data" / "ops" / "auto_approved_today.json")
        
        bundle_path = self.base_dir / "data" / "ops" / "bundles" / ymd.replace("-", "/") / "speak_bundle.json"
        bundle_data = self._load_json(bundle_path)

        # 2. Map Lookups
        quality_map = {t["topic_id"]: t for t in quality_data.get("topics", [])}
        speak_map = {v["topic_id"]: v for v in speak_data.get("verdicts", [])}
        aa_ids = {t["topic_id"] for t in auto_approved.get("auto_approved", []) if "topic_id" in t}
        
        # Bundle mapping (supports topic_id or title)
        bundle_topics = bundle_data.get("topics", [])
        
        # [Step 55-1] Script Discovery
        gate_dir = self.base_dir / "data" / "topics" / "gate" / ymd.replace("-", "/")
        scripts = list(gate_dir.glob("script_v1_*.md")) if gate_dir.exists() else []

        # 3. Consolidation per Topic (Order from View or Quality Review)
        # We follow the order of 'topics' in Quality Review, as it's often the priority list for review.
        all_topics = quality_data.get("topics", [])
        if not all_topics and view_data.get("sections"):
            # Fallback to view sections if quality review missed some or is empty
            seen = set()
            for sect in view_data["sections"].values():
                for t in sect:
                    tid = t.get("topic_id")
                    if tid and tid not in seen:
                        all_topics.append(t)
                        seen.add(tid)

        console_topics = []
        for t in all_topics:
            topic_id = t.get("topic_id", "unknown")
            title = t.get("title", "Untitled")
            
            # Strict Join Logic
            q = quality_map.get(topic_id, {})
            s = speak_map.get(topic_id, {})
            
            # Seek script for this topic
            script_md_path = None
            found_script = False
            for script_p in scripts:
                # Script filenames are usually script_v1_gate_{short_hash}.md
                # We check content for topic_id or title if metadata is inside? 
                # Actually, the name contains the hash of the topic.
                # If we don't have the hash, we might need to check if the short_hash is in topic object.
                # For Step 55, let's look for the topic_id in the script content as a fallback.
                try:
                    content = script_p.read_text(encoding="utf-8")
                    if topic_id in content:
                        script_md_path = str(script_p.relative_to(self.base_dir))
                        found_script = True
                        break
                except: pass

            # Seek Bundle info
            bundle_ref = next((b for b in bundle_topics if b.get("topic_id") == topic_id), None)

            console_topic = {
                "topic_id": topic_id,
                "title": title,
                "lane": t.get("lane") or "ANOMALY",
                "status": t.get("status") or "READY",
                "speakability": s.get("speakability", "UNKNOWN"),
                "auto_approved": topic_id in aa_ids,
                "selection_rationale": t.get("selection_rationale") or t.get("rationale"),
                "fact_anchors": t.get("fact_anchors") or q.get("fact_anchors") or [],
                "evidence_refs": t.get("evidence_refs") or [],
                "script_assets": {
                    "script_md_path": script_md_path,
                    "speak_bundle_md_path": str(bundle_path.with_suffix(".md").relative_to(self.base_dir)) if bundle_ref else None,
                    "missing_assets": []
                },
                "debug_join": {
                    "matched_by": "topic_id",
                    "missing_fields": []
                }
            }
            
            if not script_md_path:
                console_topic["script_assets"]["missing_assets"].append("script_md")
            if not bundle_ref:
                console_topic["script_assets"]["missing_assets"].append("speak_bundle")

            console_topics.append(console_topic)

        output = {
            "run_date": ymd,
            "topics": console_topics
        }

        # 4. Save Artifacts
        self.output_json.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
        self._export_markdown(output)

        return output

    def _load_json(self, path: Path) -> Dict[str, Any]:
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except: pass
        return {}

    def _export_markdown(self, data: Dict[str, Any]):
        ymd = data["run_date"]
        lines = [f"# TOPIC CONSOLE (RUN_DATE: {ymd})", ""]
        
        for t in data["topics"]:
            badges = []
            badges.append(f"LANE:{t['lane']}")
            badges.append(f"STATUS:{t['status']}")
            badges.append(f"SPEAK:{t['speakability']}")
            if t['auto_approved']: badges.append("AUTO_APPROVED✅")
            
            lines.append(f"## {t['title']} ({t['topic_id']})")
            lines.append(f"**Badges**: {' | '.join(badges)}")
            lines.append("")

            # 1) Why selected
            lines.append("### 1) Why Selected")
            rat = t.get("selection_rationale")
            if isinstance(rat, dict):
                for k, v in rat.items():
                    lines.append(f"- **{k}**: {v}")
            elif isinstance(rat, str):
                lines.append(f"- {rat}")
            else:
                lines.append("- (missing rationale)")
            lines.append("")

            # 2) Fact Anchors & Evidence
            lines.append("### 2) Fact Anchors & Evidence")
            anchors = t.get("fact_anchors", [])
            if anchors:
                for a in anchors[:5]:
                    lines.append(f"- [{a.get('type','FACT')}] {a.get('text','(no text)')} ({a.get('source','unknown')})")
            else:
                lines.append("- (none)")
            
            refs = t.get("evidence_refs", [])
            if refs:
                for r in refs:
                    lines.append(f"- {r.get('publisher','Source')}: {r.get('url','#')}")
            else:
                lines.append("- (no evidence refs)")
            lines.append("")

            # 3) Script / Speak Material
            lines.append("### 3) Script / Speak Material")
            script_p = t["script_assets"].get("script_md_path")
            if script_p:
                lines.append(f"- **Script**: [{script_p}]({script_p})")
                try:
                    preview_path = self.base_dir / script_p
                    content_lines = preview_path.read_text(encoding="utf-8").splitlines()
                    preview = "\n".join(content_lines[:10])
                    lines.append("```markdown")
                    lines.append(preview)
                    if len(content_lines) > 10: lines.append("...")
                    lines.append("```")
                except:
                    lines.append("- (preview failed)")
            else:
                lines.append("- (no script generated yet)")

            bundle_p = t["script_assets"].get("speak_bundle_md_path")
            if bundle_p:
                lines.append(f"- **Speak Bundle**: [{bundle_p}]({bundle_p})")
            
            missing = t["script_assets"].get("missing_assets", [])
            if missing:
                lines.append(f"- **Missing**: {', '.join(missing)}")
            
            lines.append("")
            lines.append("---")
            lines.append("")

        self.output_md.write_text("\n".join(lines), encoding="utf-8")

if __name__ == "__main__":
    b = TopicConsoleBuilder(Path("."))
    b.run(datetime.now().strftime("%Y-%m-%d"))
