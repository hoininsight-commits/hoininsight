import json
import logging
from pathlib import Path
from src.ops.narrative_intelligence_layer import NarrativeIntelligenceLayer

def verify():
    base = Path("/Users/jihopa/Downloads/HoinInsight_Remote")
    ni = NarrativeIntelligenceLayer(base)
    
    # 1. Capture Baseline from v2 (already contains previous run results if it exists)
    v2_path = base / "data/ops/narrative_intelligence_v2.json"
    baseline_conflicts = 0
    if v2_path.exists():
        with open(v2_path, "r", encoding="utf-8") as f:
            v2_data = json.load(f)
            baseline_conflicts = len([t for t in v2_data.get("topics", []) if t.get("conflict_flag")])

    print(f"Step 1: Baseline Conflict Count = {baseline_conflicts}")

    # 2. Run Process with Context Pack Injection
    print("Step 2: Processing topics with Context Pack Injection...")
    ni.process_topics()
    
    # 3. Verify Results
    with open(v2_path, "r", encoding="utf-8") as f:
        v3_data = json.load(f)
    
    current_conflicts = len([t for t in v3_data.get("topics", []) if t.get("conflict_flag")])
    total = len(v3_data.get("topics", []))
    
    print(f"Step 3: Post-Injection Conflict Count = {current_conflicts}")
    print(f"Step 4: Activation Ratio = {current_conflicts}/{total}")

    # 4. Generate Samples for Phase 16A report
    samples = v3_data.get("topics", [])[:10]
    sample_md = "# Phase 16A Context Pack Samples\n\n"
    for s in samples:
        sample_md += f"## Topic: {s.get('title')}\n"
        sample_md += f"- **Rationale (Enriched)**:\n```\n{s.get('rationale_natural')}\n```\n"
        sample_md += f"- **Conflict Detected**: {s.get('conflict_flag')}\n"
        sample_md += f"- **Matched Patterns**: {s.get('_diag_conflict_patterns')}\n\n"
    
    sample_report_path = base / "data_outputs/ops/phase16a_context_pack_samples.md"
    sample_report_path.write_text(sample_md, encoding="utf-8")
    
    delta_md = f"""# Phase 16A Conflict Delta Report

- **Total Topics**: {total}
- **Baseline Conflicts**: {baseline_conflicts} (0% target)
- **Post-Injection Conflicts**: {current_conflicts}
- **Delta**: +{current_conflicts - baseline_conflicts}
- **Status**: {"SUCCESS" if current_conflicts > 0 else "FAILED"} (Target >= 1)
"""
    delta_report_path = base / "data_outputs/ops/phase16a_conflict_delta.md"
    delta_report_path.write_text(delta_md, encoding="utf-8")
    
    print(f"Reports saved to data_outputs/ops/")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    verify()
