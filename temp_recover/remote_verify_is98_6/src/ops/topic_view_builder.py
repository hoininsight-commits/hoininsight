from __future__ import annotations
import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

class TopicViewBuilder:
    """
    Consolidates today's topic outputs into a single read-only view.
    Artifacts: topic_view_today.json, topic_view_today.md
    """

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.output_dir = base_dir / "data" / "ops"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def build_view(self, target_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Main runner for Topic View consolidation.
        """
        ymd = target_date or datetime.now().strftime("%Y-%m-%d")
        ymd_path = ymd.replace("-", "/")
        
        view = {
            "run_date": ymd,
            "sections": {
                "auto_approved": [],
                "ready": [],
                "shadow": [],
                "fact_first_shadow": []
            },
            "counts": { "auto_approved": 0, "ready": 0, "shadow": 0, "fact_first_shadow": 0 },
            "missing_inputs": []
        }
        
        # 1. Load Auto-Approved
        aa_path = self.output_dir / "auto_approved_today.json"
        if aa_path.exists():
            try:
                aa_data = json.loads(aa_path.read_text(encoding="utf-8"))
                view["sections"]["auto_approved"] = self._normalize_list(aa_data.get("approved_topics", []))
            except: pass
        else:
            view["missing_inputs"].append("auto_approved_today.json")

        # 2. Load READY Topics
        ready_path = self.base_dir / "data" / "topics" / "gate" / ymd_path / "topic_gate_output.json"
        if ready_path.exists():
            try:
                gate_data = json.loads(ready_path.read_text(encoding="utf-8"))
                ready_list = [t for t in gate_data.get("topics", []) if t.get("status") == "READY"]
                view["sections"]["ready"] = self._normalize_list(ready_list)
            except: pass
        else:
            view["missing_inputs"].append(f"gate/{ymd_path}/topic_gate_output.json")

        # 3. Load Shadow Candidates
        shadow_cand_path = self.output_dir / "shadow_candidates.json"
        if shadow_cand_path.exists():
            try:
                sc_data = json.loads(shadow_cand_path.read_text(encoding="utf-8"))
                view["sections"]["shadow"] = self._normalize_list(sc_data.get("candidates", []))
            except: pass
        else:
            view["missing_inputs"].append("shadow_candidates.json")

        # 4. Load Fact-First Shadows
        ff_path = self.base_dir / "data" / "topics" / "shadow_pool" / ymd_path / "fact_first.json"
        if ff_path.exists():
            try:
                ff_data = json.loads(ff_path.read_text(encoding="utf-8"))
                view["sections"]["fact_first_shadow"] = self._normalize_list(ff_data.get("topics", []))
            except: pass
        else:
            view["missing_inputs"].append(f"shadow_pool/{ymd_path}/fact_first.json")

        # Update Counts
        for key in view["sections"]:
            view["counts"][key] = len(view["sections"][key])
            
        # Save JSON
        json_file = self.output_dir / "topic_view_today.json"
        json_file.write_text(json.dumps(view, indent=2, ensure_ascii=False), encoding="utf-8")
        
        # Export Markdown
        self._export_markdown(view)
        
        return view

    def _normalize_list(self, raw_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ensures common fields for the view layer."""
        normalized = []
        for item in raw_list:
            normalized.append({
                "topic_id": item.get("topic_id") or item.get("id") or "unknown",
                "title": item.get("title") or item.get("fact_anchor") or "Untitled",
                "lane": item.get("lane") or item.get("topic_type") or "N/A",
                "level": item.get("level") or 0,
                "impact": item.get("impact") or "N/A",
                "why_now": item.get("why_now") or item.get("why_now_hint") or "(missing)",
                "evidence_count": len(item.get("evidence_refs", [])) if "evidence_refs" in item else 0,
                "structural_frame": item.get("structural_frame"),
                "links": item.get("links", {})
            })
        return normalized

    def _export_markdown(self, view: Dict[str, Any]):
        ymd = view["run_date"]
        md_file = self.output_dir / "topic_view_today.md"
        
        lines = [f"# 🧭 TODAY TOPIC VIEW - {ymd}", ""]
        
        # Summary
        c = view["counts"]
        lines.append(f"**SUMMARY**: 🛡️ AUTO-APPROVED={c['auto_approved']} | 🟢 READY={c['ready']} | 🌗 SHADOW={c['shadow']} | 🏹 FACT-FIRST={c['fact_first_shadow']}")
        lines.append("")
        
        # Sections
        sections_meta = [
            ("🛡️ AUTO-APPROVED", "auto_approved", "No AUTO-APPROVED topics today."),
            ("🟢 READY", "ready", "No READY topics today."),
            ("🌗 SHADOW", "shadow", "No SHADOW candidates today."),
            ("🏹 FACT-FIRST SHADOW", "fact_first_shadow", "No FACT-FIRST shadow topics today.")
        ]
        
        for title, key, Empty_msg in sections_meta:
            lines.append(f"## {title}")
            items = view["sections"][key]
            if not items:
                lines.append(Empty_msg)
                lines.append("")
                continue
                
            for item in items:
                lines.append(f"### {item['title']} (ID: {item['topic_id']})")
                lines.append(f"- **Tags**: Lane={item['lane']} | Level={item['level']} | Impact={item['impact']}")
                lines.append(f"- **WHY NOW**: {item['why_now']}")
                lines.append(f"- **Evidence**: {item['evidence_count']} references")
                if item["links"]:
                    links_str = ", ".join([f"[{k}]({v})" for k, v in item["links"].items()])
                    lines.append(f"- **Links**: {links_str}")
                lines.append("")
        
        # Missing Inputs
        if view["missing_inputs"]:
            lines.append("## ⚠️ DATA STATUS")
            lines.append("Following inputs were missing during generation:")
            for m in view["missing_inputs"]:
                lines.append(f"- {m}")
            lines.append("")

        md_file.write_text("\n".join(lines), encoding="utf-8")
        print(f"[TopicView] Exported markdown to {md_file}")

if __name__ == "__main__":
    builder = TopicViewBuilder(Path("."))
    builder.build_view()
