import logging
from pathlib import Path
from src.ops.narrative_intelligence_layer import NarrativeIntelligenceLayer

def run_verification():
    logging.basicConfig(level=logging.INFO)
    base = Path("/Users/jihopa/Downloads/HoinInsight_Remote")
    ni = NarrativeIntelligenceLayer(base)
    
    print("Step 1: Processing Topics with Phase 15 Enhancements...")
    ni.process_topics()
    
    print("Step 2: Generating Conflict Trace Report for 10 samples...")
    ni.run_conflict_trace(count=10)
    
    print("Step 3: Verifying output files...")
    outputs = [
        "data/ops/narrative_intelligence_v2.json",
        "data_outputs/ops/video_candidate_pool.json",
        "data_outputs/ops/phase15_detection_diagnostics.md",
        "data_outputs/ops/phase15_conflict_trace.md"
    ]
    
    for out in outputs:
        p = base / out
        if p.exists():
            print(f"  [OK] {out} generated.")
        else:
            print(f"  [MISSING] {out}")

if __name__ == "__main__":
    run_verification()
