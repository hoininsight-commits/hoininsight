import json
from pathlib import Path

def compare():
    base = Path("/Users/jihopa/Downloads/HoinInsight_Remote")
    v2_path = base / "data/ops/narrative_intelligence_v2.json"
    
    if not v2_path.exists():
        print("Error: narrative_intelligence_v2.json not found")
        return

    with open(v2_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = data.get("topics", [])
    total = len(df)
    
    actor_rate = len([t for t in df if t.get("actor_tier_score", 0) > 0]) / total * 100
    axis_rate = len([t for t in df if t.get("cross_axis_count", 0) >= 2]) / total * 100
    conflict_rate = len([t for t in df if t.get("conflict_flag")]) / total * 100
    
    output = f"""# Phase 15 Quality Verification Report (Post-Upgrade)

- **Total Analyzed Topics**: {total}
- **Structural Actor Detection Ratio**: {actor_rate:.2f}% (Baseline: 0.00%)
- **Multi-Axis Multiplier Ratio (Count >= 2)**: {axis_rate:.2f}%
- **Conflict Flag Ratio**: {conflict_rate:.2f}%
"""
    
    report_path = base / "data_outputs/ops/phase15_quality_verification.md"
    report_path.write_text(output, encoding="utf-8")
    print(f"Report saved to {report_path}")

if __name__ == "__main__":
    compare()

