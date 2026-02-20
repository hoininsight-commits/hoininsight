
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add parent to path to allow imports
sys.path.append(str(Path(__file__).resolve().parent))

from src.ops.pre_structural_signal_layer import PreStructuralSignalLayer
from src.topics.anchor_engine.logic_core import AnchorEngine
from src.ops.script_skeleton_generator import ScriptSkeletonGenerator

def test_step74_full_flow():
    base_dir = Path(".").resolve()
    
    # 1. Mock Topics
    mock_topics = [
        {
            "dataset_id": "rates_us10y_fred",
            "title": "US 10Y Rate Spike",
            "rationale": "Budget deadline approaching in 3 days. Market tension rising.",
            "evidence": {"level": "L2"},
            "score": 75.0
        },
        {
            "dataset_id": "fx_usdkrw_ecos",
            "title": "KRW Weakness",
            "rationale": "General market volatility.",
            "evidence": {"level": "L2"},
            "score": 60.0
        }
    ]
    
    # 2. Test Detection Layer
    print("--- 1. Testing PreStructuralSignalLayer ---")
    ps_layer = PreStructuralSignalLayer(base_dir)
    enriched = ps_layer.analyze_topics(mock_topics)
    
    has_ps = any(t.get("is_pre_structural") for t in enriched)
    print(f"Detection Success: {has_ps}")
    
    ps_topic = next(t for t in enriched if t.get("is_pre_structural"))
    print(f"Detected Signal Type: {ps_topic['pre_structural_signal']['signal_type']}")
    print(f"Rationale: {ps_topic['pre_structural_signal']['rationale']}")
    
    # 3. Test Anchor Engine Integration
    print("\n--- 2. Testing AnchorEngine Integration ---")
    # Mock anomaly data for clustering
    mock_anomalies = [
        {"dataset_id": "rates_us10y_fred", "z_score": 2.5, "status_today": "ANOMALY"},
        {"dataset_id": "fx_usdkrw_ecos", "z_score": 2.1, "status_today": "ANOMALY"}
    ]
    
    ae = AnchorEngine(base_dir)
    ae_results = ae.run_analysis(mock_anomalies, [ps_topic])
    
    if ae_results:
        best = ae_results[0]
        print(f"Anchor Type: {best.why_now_type}")
        print(f"Pre-Structural Context Present: {best.pre_structural_context is not None}")
        md_output = best.to_markdown()
        print("Markdown Output Sample Index 7 (Label):")
        print(md_output)
    else:
        print("FAIL: No anchor result")

    # 4. Test Narrative Binding (Skeleton Generator)
    print("\n--- 3. Testing ScriptSkeletonGenerator Binding ---")
    # Mock data structure for ScriptSkeletonGenerator
    mock_topic_bundle_entry = {
        "topic_id": "rates_us10y_fred",
        "title": "US 10Y Rate Spike",
        "production_format": "BOTH",
        "impact_tag": "NEAR",
        "speak_pack": {
            "one_liner": "Budget deadline causes rate spike.",
            "numbers": ["US10Y: 4.5%"],
            "risk_note": "Risk: High"
        },
        "pre_structural_signal": ps_topic["pre_structural_signal"]
    }
    
    sk_gen = ScriptSkeletonGenerator(base_dir)
    short_sk = sk_gen._generate_short_skeleton(mock_topic_bundle_entry)
    long_sk = sk_gen._generate_long_skeleton(mock_topic_bundle_entry)
    
    label = "[🟠 PRE-STRUCTURAL SIGNAL]"
    found_in_short = label in short_sk
    found_in_long = label in long_sk
    
    print(f"Label found in SHORT skeleton: {found_in_short}")
    print(f"Label found in LONG skeleton: {found_in_long}")
    
    if found_in_short:
        print("Short Preview Snippet:")
        # Show ONE-LINER section
        parts = short_sk.split("## ONE-LINER")
        if len(parts) > 1:
            print(parts[1].split("##")[0].strip())

if __name__ == "__main__":
    test_step74_full_flow()
