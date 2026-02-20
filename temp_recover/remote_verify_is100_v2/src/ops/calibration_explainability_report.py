from __future__ import annotations
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

class CalibrationExplainabilityReport:
    """
    Step 58: Calibration Explainability Report.
    Consolidates Step 56 (Quality Logs) and Step 57 (Preference Overlay)
    to explain human judgment vs engine patterns.
    """

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def run(self, ymd: str) -> Dict[str, Any]:
        """Runs the report generation."""
        year, month, day = ymd.split("-")
        report_dir = self.base_dir / "data" / "ops" / "calibration" / year / month / day
        report_dir.mkdir(parents=True, exist_ok=True)

        # 1. Load Inputs
        overlay_data = self._load_json(self.base_dir / "data" / "ops" / "human_pref_overlay_today.json")
        view_data = self._load_json(self.base_dir / "data" / "ops" / "topic_view_today.json")
        signature_data = self._load_json(self.base_dir / "data" / "ops" / "human_pref_signature_30d.json")
        
        # Load human labels from JSONL (latest per topic for today)
        human_labels = self._load_today_labels(ymd)
        
        errors = []
        if not overlay_data: errors.append("Missing human_pref_overlay_today.json")
        if not view_data: errors.append("Missing topic_view_today.json")
        
        # 2. Matchmaking
        mismatch_cases = []
        all_topic_ids = set(human_labels.keys()) | set(overlay_data.get("overlays", {}).keys())
        
        # Titles lookup from view
        title_map = {}
        for sect in view_data.get("sections", {}).values():
            for t in sect:
                title_map[t["topic_id"]] = t.get("title", "Untitled")

        label_counts = {"STRONG": 0, "BORDERLINE": 0, "WEAK": 0, "UNLABELED": 0}
        
        topic_lines = []
        for tid in sorted(all_topic_ids):
            label = human_labels.get(tid)
            if label: label_counts[label] += 1
            else: label_counts["UNLABELED"] += 1
            
            overlay = overlay_data.get("overlays", {}).get(tid, {})
            bucket = overlay.get("overlay_bucket", "INSUFFICIENT_HISTORY")
            
            # Detect Mismatch
            mismatch = False
            why = []
            if label == "STRONG" and bucket == "HUMAN_LIKELY_WEAK":
                mismatch = True
                missing = ", ".join(overlay.get("missing_traits", []))
                why.append(f"Human rated STRONG despite missing {missing}")
            elif label == "WEAK" and bucket == "HUMAN_LIKELY_STRONG":
                mismatch = True
                matched = ", ".join(overlay.get("matched_traits", []))
                why.append(f"Human rated WEAK though matches {matched}")
            
            if mismatch:
                mismatch_cases.append({
                    "topic_id": tid,
                    "title": title_map.get(tid, "Unknown"),
                    "human_label": label,
                    "overlay": bucket,
                    "why": why
                })
            
            topic_lines.append({
                "topic_id": tid,
                "title": title_map.get(tid, "Unknown"),
                "label": label or "NONE",
                "overlay": bucket,
                "matched": overlay.get("matched_traits", []),
                "missing": overlay.get("missing_traits", [])
            })

        # 3. Final Report Data
        report_json = {
            "run_date": ymd,
            "label_counts": label_counts,
            "overlay_counts": overlay_data.get("summary", {}),
            "mismatch_cases": mismatch_cases,
            "top_drivers": {
                "strong": list(signature_data.get("traits", {}).get("lane", {}).keys()), # Convert to list
                "weak": [] # We didn't calc weak traits specifically in signature
            },
            "topic_details": topic_lines,
            "errors": errors
        }

        # Save JSON
        json_path = report_dir / "calibration_review_today.json"
        json_path.write_text(json.dumps(report_json, indent=2, ensure_ascii=False), encoding="utf-8")
        
        # Save MD
        self._export_markdown(report_json, report_dir / "calibration_review_today.md")

        return report_json

    def _load_today_labels(self, ymd: str) -> Dict[str, str]:
        labels = {}
        log_file = self.base_dir / "data" / "ops" / "topic_quality_log.jsonl"
        if not log_file.exists(): return labels
        
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip(): continue
                try:
                    record = json.loads(line)
                    if record.get("run_date") == ymd:
                        labels[record["topic_id"]] = record["verdict"]
                except: continue
        return labels

    def _load_json(self, path: Path) -> Dict:
        if path.exists():
            try: return json.loads(path.read_text(encoding="utf-8"))
            except: pass
        return {}

    def _export_markdown(self, data: Dict[str, Any], path: Path):
        lines = [f"# CALIBRATION REVIEW - {data['run_date']}", ""]
        
        # 1) Today Summary
        lines.append("## 📊 Today Summary")
        lc = data["label_counts"]
        lines.append(f"**Human Labels**: STRONG={lc['STRONG']} | BORDERLINE={lc['BORDERLINE']} | WEAK={lc['WEAK']} | UNLABELED={lc['UNLABELED']}")
        oc = data["overlay_counts"]
        if oc:
            lines.append(f"**Overlay Predictions**: LIKELY_STRONG={oc.get('HUMAN_LIKELY_STRONG',0)} | UNCERTAIN={oc.get('HUMAN_UNCERTAIN',0)} | LIKELY_WEAK={oc.get('HUMAN_LIKELY_WEAK',0)}")
        lines.append("")

        # 2) Mismatch Watchlist
        lines.append("## 🔍 Mismatch Watchlist")
        if not data["mismatch_cases"]:
            lines.append("_No major mismatches detected today._")
        else:
            for m in data["mismatch_cases"][:5]:
                lines.append(f"- **{m['title']}** ({m['topic_id']})")
                lines.append(f"  - Label: {m['human_label']} | Overlay: {m['overlay']}")
                lines.append(f"  - WHY: {m['why'][0] if m['why'] else 'N/A'}")
        lines.append("")

        # 3) Driver Traits
        lines.append("## 🎯 Top STRONG Driver Traits (Last 30d)")
        drivers = data["top_drivers"]["strong"]
        if drivers:
            lines.append(", ".join([f"`{d}`" for d in drivers]))
        else:
            lines.append("_Insufficient history._")
        lines.append("")

        # 4) Per-Topic Mini Lines
        lines.append("## 📑 All Topics Detail")
        lines.append("| Title | Human Label | Overlay | Matched | Missing |")
        lines.append("|---|---|---|---|---|")
        for t in data["topic_details"]:
            matched_str = ", ".join(t["matched"][:3])
            missing_str = ", ".join(t["missing"][:3])
            lines.append(f"| {t['title']} | {t['label']} | {t['overlay']} | {matched_str} | {missing_str} |")
        
        path.write_text("\n".join(lines), encoding="utf-8")
