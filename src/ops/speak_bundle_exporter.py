import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class SpeakBundleExporter:
    """
    Step 45: Speak Pack Export Bundle v1.0.
    Packages auto-approved topics for production.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def run(self, ymd: str, cards: List[Dict], auto_approved_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates speak_bundle.json and speak_bundle.md.
        """
        approved_ids_map = {a["topic_id"]: a for a in auto_approved_data.get("auto_approved", [])}
        bundle_topics = []
        
        # Filter cards that are auto-approved
        for c in cards:
            tid = c.get("topic_id")
            if tid in approved_ids_map:
                aa_info = approved_ids_map[tid]
                
                # Extract Speak Pack
                sp = c.get("speak_pack", {})
                
                # Extract Evidence Refs
                refs = []
                for node in c.get("evidence_nodes", []):
                    # In our system, evidence nodes usually have publisher/url
                    refs.append({
                        "publisher": node.get("publisher", "Unknown"),
                        "url": node.get("url", "#"),
                        "label": node.get("title", "Reference")
                    })

                topic_entry = {
                    "topic_id": tid,
                    "title": c.get("title"),
                    "lane": "FACT" if c.get("is_fact_driven") else "ANOMALY",
                    "impact_tag": c.get("impact_window"),
                    "narration_level": c.get("level", 1),
                    "speak_pack": {
                        "one_liner": sp.get("one_liner", "N/A"),
                        "numbers": sp.get("numbers", []),
                        "watch_next": sp.get("watch_next", []),
                        "risk_note": sp.get("risk_note", "None")
                    },
                    "evidence_refs": refs,
                    "quality_status": "READY", # Context implies these are READY
                    "auto_approval_reason": aa_info.get("approval_reason", []),
                    "missing_assets": self._check_missing_assets(c)
                }
                bundle_topics.append(topic_entry)

        # 1. Output directory
        y, m, d = ymd.split("-")
        bundle_dir = self.base_dir / "data" / "ops" / "bundles" / y / m / d
        bundle_dir.mkdir(parents=True, exist_ok=True)

        # 2. JSON Export
        bundle_json = {
            "run_date": ymd,
            "bundle_id": f"{ymd.replace('-', '')}_autoapproved_v1",
            "topics": bundle_topics,
            "count": len(bundle_topics)
        }
        json_path = bundle_dir / "speak_bundle.json"
        json_path.write_text(json.dumps(bundle_json, indent=2, ensure_ascii=False), encoding="utf-8")

        # 3. Markdown Export
        md_content = self._generate_markdown(bundle_json)
        md_path = bundle_dir / "speak_bundle.md"
        md_path.write_text(md_content, encoding="utf-8")

        return {
            "json_path": str(json_path.relative_to(self.base_dir)),
            "md_path": str(md_path.relative_to(self.base_dir)),
            "count": len(bundle_topics)
        }

    def _check_missing_assets(self, card: Dict) -> List[str]:
        missing = []
        sp = card.get("speak_pack", {})
        if not sp.get("one_liner") or sp.get("one_liner") == "TBD":
            missing.append("ONE_LINER")
        if not sp.get("numbers"):
            # Not strictly "missing" per requirements but noted
            pass
        if not card.get("evidence_nodes"):
            missing.append("EVIDENCE_REFS")
        return missing

    def _generate_markdown(self, bundle: Dict) -> str:
        lines = [f"# 📦 HOIN SPEAK BUNDLE | {bundle['run_date']}\n"]
        lines.append(f"**Bundle ID**: `{bundle['bundle_id']}`\n")
        lines.append(f"**Topics**: {bundle['count']}건 자동 승인됨\n")
        lines.append("---\n")

        if bundle["count"] == 0:
            lines.append("_No topics met strict auto-approval conditions today._")
            return "\n".join(lines)

        for t in bundle["topics"]:
            lines.append(f"## {t['title']}")
            lines.append(f"- **Impact**: {t['impact_tag']} | **Level**: {t['narration_level']}")
            
            sp = t["speak_pack"]
            lines.append(f"\n### 🎙️ SPEAK PACK")
            lines.append(f"> **One-Liner**: {sp['one_liner']}")
            
            nums = sp["numbers"]
            if nums:
                lines.append(f"> **Numbers**: " + ", ".join([str(n) for n in nums]))
            else:
                lines.append(f"> **Numbers**: (no numeric evidence)")
                
            lines.append(f"> **Risk Note**: {sp['risk_note']}")
            
            lines.append(f"\n### 🔗 EVIDENCE")
            if not t["evidence_refs"]:
                lines.append("- _No external references found._")
            else:
                for ref in t["evidence_refs"]:
                    lines.append(f"- [{ref['publisher']}] [{ref['label']}]({ref['url']})")
                    
            lines.append(f"\n### 📺 WATCH NEXT")
            for w in sp["watch_next"]:
                lines.append(f"- {w}")
                
            missing = t.get("missing_assets", [])
            if missing:
                lines.append(f"\n> ⚠️ **Missing Assets**: {', '.join(missing)}")
                
            lines.append("\n---\n")

        return "\n".join(lines)
