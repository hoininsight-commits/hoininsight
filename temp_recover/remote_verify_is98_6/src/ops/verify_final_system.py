
import json
from pathlib import Path
from src.reporters.decision_dashboard import DecisionDashboard

def verify_system():
    project_root = Path(".")
    dash = DecisionDashboard(project_root)
    ymd = "2026-01-24"
    
    print(f"--- Verifying System for {ymd} ---")
    
    # 1. Build Data
    print("[1] Building Dashboard Data...")
    data = dash.build_dashboard_data(ymd)
    print(f"    Summary: {data['summary']}")
    
    # 2. Render Markdown
    print("[2] Rendering Markdown...")
    md = dash.render_markdown(data)
    
    # Check for hardening features
    if "🚫 WHY NO SPEAK" in md or "## 🎬 TODAY" in md:
        print("    OK: Dashboard headers found.")
    if "🎯 RECOMMENDED FOR TODAY" in md:
        print("    OK: Recommender logic found.")
    if "SCRIPT QUALITY" in md:
        print("    OK: Quality counters found.")
        
    # 3. Save Snapshot
    print("[3] Saving Daily Lock...")
    lock_path = dash.save_snapshot(ymd, data)
    print(f"    OK: Saved to {lock_path}")
    
    # 4. Write Final Markdown to data/validation_run for review
    out_path = project_root / "data" / "validation_run" / ymd / "final_hardened_dashboard.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md, encoding="utf-8")
    print(f"    OK: Proof-of-work saved to {out_path}")
    
    print("--- Verification Complete ---")

if __name__ == "__main__":
    verify_system()
