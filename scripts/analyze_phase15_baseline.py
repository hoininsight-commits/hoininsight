import json
from datetime import datetime, timedelta
from pathlib import Path

def analyze():
    base_dir = Path("/Users/jihopa/Downloads/HoinInsight_Remote")
    autopsy_path = base_dir / "data_outputs/ops/narrative_component_autopsy_last14days.json"
    
    if not autopsy_path.exists():
        print(f"Error: {autopsy_path} not found")
        return

    with open(autopsy_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Filter for last 7 days (Feb 19 to Feb 25)
    today = datetime(2026, 2, 25)
    start_date = today - timedelta(days=6)
    
    df = [item for item in data if datetime.strptime(item["date"], "%Y-%m-%d") >= start_date]
    
    total_topics = len(df)
    if total_topics == 0:
        print("No topics found in the last 7 days.")
        return

    n_scores = [item.get("final_narrative_score", 0) for item in df if item.get("_has_narrative_score", False)]
    avg_n_score = sum(n_scores) / len(n_scores) if n_scores else 0
    
    # Calculate medians
    sorted_n = sorted(n_scores)
    median_n = sorted_n[len(sorted_n)//2] if sorted_n else 0

    video_ready_rate = len([item for item in df if item.get("video_ready")]) / total_topics * 100
    conflict_rate = len([item for item in df if item.get("conflict_flag")]) / total_topics * 100
    escalation_rate = len([item for item in df if item.get("escalation_detected")]) / total_topics * 100
    
    actor_rate = len([item for item in df if item.get("structural_actor_score", 0) > 0]) / total_topics * 100
    flow_rate = len([item for item in df if item.get("capital_flow_score", 0) > 0]) / total_topics * 100
    policy_rate = len([item for item in df if item.get("policy_score", 0) > 0]) / total_topics * 100

    output = f"""# Phase 15 Quality Baseline (Last 7 Days: {start_date.strftime('%Y-%m-%d')} ~ {today.strftime('%Y-%m-%d')})

- **Total Generated Topics**: {total_topics}
- **Narrative Score Average**: {avg_n_score:.2f}
- **Narrative Score Median**: {median_n:.2f}
- **Video Ready Ratio**: {video_ready_rate:.2f}%
- **Conflict Flag Ratio**: {conflict_rate:.2f}%
- **Escalation Detected Ratio**: {escalation_rate:.2f}%
- **Structural Actor Score > 0 Ratio**: {actor_rate:.2f}%
- **Capital Flow Score > 0 Ratio**: {flow_rate:.2f}%
- **Policy Score > 0 Ratio**: {policy_rate:.2f}%
"""
    
    output_path = base_dir / "data_outputs/ops/phase15_quality_baseline.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output, encoding="utf-8")
    print(f"Baseline saved to {output_path}")

if __name__ == "__main__":
    analyze()
