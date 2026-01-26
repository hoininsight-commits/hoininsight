import json
import os
from pathlib import Path
from datetime import datetime

class DashboardManifest:
    """Generates a manifest file to point the dashboard to the latest run."""
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        # [Step 25-2] Standardize to data/dashboard/ for GitHub Pages deployment
        self.manifest_path = base_dir / "data" / "dashboard" / "latest_run.json"
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)

    def find_latest_run(self) -> str:
        """Finds the most recent YYYY-MM-DD run folder."""
        reports_root = self.base_dir / "data" / "reports"
        dates = []
        for y_dir in reports_root.glob("20*"):
            if not y_dir.is_dir(): continue
            for m_dir in y_dir.glob("??"):
                if not m_dir.is_dir(): continue
                for d_dir in m_dir.glob("??"):
                    if not d_dir.is_dir(): continue
                    dates.append(f"{y_dir.name}-{m_dir.name}-{d_dir.name}")
        
        return sorted(dates, reverse=True)[0] if dates else None

    def generate(self, ymd: str = None):
        """Creates latest_run.json. Auto-detects if ymd is None."""
        if not ymd:
            ymd = self.find_latest_run()
        
        if not ymd:
            print("No runs detected.")
            return

        year, month, day = ymd.split("-")
        rel_dir = f"data/reports/{year}/{month}/{day}"
        abs_dir = self.base_dir / rel_dir
        
        # Verify required files and log missing
        required = {
            "report_md": "daily_brief.md",
            "decision_md": "decision_dashboard.md", # Point to the new decision dashboard
            "daily_lock_json": "daily_lock.json"
        }
        
        paths = {}
        missing = []
        for key, filename in required.items():
            if (abs_dir / filename).exists():
                paths[key] = f"{rel_dir}/{filename}"
            else:
                missing.append(filename)

        # [Step 48] Index Script Skeleton
        script_path = None
        gate_dir = self.base_dir / "data" / "topics" / "gate" / ymd.replace("-", "/")
        if gate_dir.exists():
            scripts = list(gate_dir.glob("script_v1_*.md"))
            if scripts:
                # Pick the latest or just the first one if multiple
                script_file = sorted(scripts, key=os.path.getmtime, reverse=True)[0]
                script_path = str(script_file.relative_to(self.base_dir))

        # [Step 47.5] Index Fact-First Shadows
        fact_first_path = None
        ff_file = self.base_dir / "data" / "topics" / "shadow_pool" / ymd.replace("-", "/") / "fact_first.json"
        if ff_file.exists():
            fact_first_path = str(ff_file.relative_to(self.base_dir))

        # [Step 48] Index Fact Anchors
        fact_anchors_path = None
        fa_file = self.base_dir / "data" / "facts" / f"fact_anchors_{ymd.replace('-', '')}.json"
        if fa_file.exists():
            fact_anchors_path = str(fa_file.relative_to(self.base_dir))

        # [Step 50-51-52] Index Topic Seeds, Hypotheses, and View
        topic_seeds_path = "data/ops/topic_seeds.json"
        narrative_hypotheses_path = "data/ops/narrative_hypotheses.json"
        topic_view_md_path = "data/ops/topic_view_today.md"
        topic_view_json_path = "data/ops/topic_view_today.json"
        topic_quality_review_md_path = "data/ops/topic_quality_review_today.md"
        topic_quality_review_json_path = "data/ops/topic_quality_review_today.json"
        manifest_data = {
            "run_date": ymd,
            "run_ts": datetime.now().isoformat(),
            "report_md": paths.get("report_md"),
            "decision_md": paths.get("decision_md"), 
            "daily_lock": paths.get("daily_lock_json"),
            "script_md": script_path,
            "fact_first_shadow_json": fact_first_path,
            "fact_anchors_json": fact_anchors_path,
            "topic_seeds_json": topic_seeds_path,
            "narrative_hypotheses_json": narrative_hypotheses_path,
            "topic_view_md": topic_view_md_path,
            "topic_view_json": topic_view_json_path,
            "topic_quality_review_md": topic_quality_review_md_path,
            "topic_quality_review_json": topic_quality_review_json_path,
            "health_json": f"data/dashboard/health_today.json",
            "auto_priority_json": "data/ops/auto_priority_today.json",
            "auto_approved_json": "data/ops/auto_approved_today.json",
            "speak_bundle_md": f"data/ops/bundles/{year}/{month}/{day}/speak_bundle.md",
            "speak_bundle_json": f"data/ops/bundles/{year}/{month}/{day}/speak_bundle.json",
            "skeleton_index_json": f"data/ops/bundles/{year}/{month}/{day}/skeletons/skeleton_index.json",
            "missing": missing
        }
        
        self.manifest_path.write_text(json.dumps(manifest_data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Manifest generated: {self.manifest_path} for {ymd}")


if __name__ == "__main__":
    import sys
    # Use current working directory instead of hardcoded path for GitHub Actions compatibility
    base = Path.cwd()
    ymd = sys.argv[1] if len(sys.argv) > 1 else None
    DashboardManifest(base).generate(ymd)