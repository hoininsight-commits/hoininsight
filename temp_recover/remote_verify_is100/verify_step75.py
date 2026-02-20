import os
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from src.ops.pre_structural_signal_layer import PreStructuralSignal
from src.ops.whynow_escalation_layer import WhyNowEscalationLayer
from src.ops.economic_hunter_narrator import EconomicHunterNarrator

def run_test():
    logging.basicConfig(level=logging.INFO)
    print("=== Step 75: WHY_NOW_ESCALATION_LAYER Verification ===")
    base_dir = Path(".")
    
    # 1. Setup Mock Data
    topics_dir = base_dir / "data/topics/2026/01/27"
    topics_dir.mkdir(parents=True, exist_ok=True)
    
    # Mock Topic with Pre-Structural Data
    mock_topic = {
        "dataset_id": "test_escalation_ds",
        "title": "US Debt Ceiling Deadline Approach",
        "rationale": "Significant budget cutoff approaching in 3 days.",
        "pre_structural_signal": {
            "signal_type": "Deadline",
            "trigger_actor": "US Treasury",
            "temporal_anchor": "2026-01-30",
            "unresolved_question": "Will the default be averted?",
            "expected_market_behavior": "risk_off",
            "escalation_path": {
                "condition_to_upgrade_to_WHY_NOW": "Deadline within 48 hours",
                "condition_to_invalidate": "Vote passed"
            },
            "narrative_pressure_score": 85,
            "related_entities": ["US", "Treasury"],
            "rationale": "High pressure due to approaching deadline.",
            "is_valid": True
        },
        "is_pre_structural": True
    }
    
    # 2. Test Case 1: Automated Escalation (meets B, C, D)
    print("\n[Test 1] Testing Escalation Logic (Conditions B, C, D)...")
    esc_layer = WhyNowEscalationLayer(base_dir)
    # Clear history for clean test
    if esc_layer.history_path.exists():
        esc_layer.history_path.unlink()
    esc_layer.history = []
    
    results = esc_layer.evaluate_signals([mock_topic])
    res = results[0]
    
    if res.get("escalation_status") == "ESC_WHY_NOW":
        print(f"✅ Success: Signal escalated to {res['escalation_info']['trigger_name']}")
        print(f"Reason: {res['escalation_info']['reason']}")
    else:
        print("❌ Fail: Signal not escalated")

    # 3. Test Case 2: Hold Status (only meets B)
    print("\n[Test 2] Testing Hold Status (Only Condition B)...")
    weak_topic = {
        "dataset_id": "test_hold_ds",
        "title": "Normal Sector Growth",
        "pre_structural_signal": {
            "signal_type": "Capital",
            "narrative_pressure_score": 40,
            "related_entities": ["Semiconductors"],
            "escalation_path": {"condition_to_upgrade_to_WHY_NOW": "Unknown"},
            "is_valid": True
        }
    }
    weak_res = esc_layer.evaluate_signals([weak_topic])[0]
    if weak_res.get("escalation_status") == "HOLD_PRE_STRUCTURAL":
        print("✅ Success: Signal held as expected")
    else:
        print("❌ Fail: Weak signal escalated incorrectly")

    # 4. Test Case 3: Narrative Binding
    print("\n[Test 3] Testing Narrative Binding...")
    # Mock top1 today file
    top1_file = base_dir / "data/ops/structural_top1_today.json"
    top1_data = {
        "top1_topics": [
            {
                "title": res["title"],
                "one_line_summary": "Debt ceiling tension",
                "why_now": "Approaching deadline",
                "original_card": res
            }
        ]
    }
    top1_file.parent.mkdir(parents=True, exist_ok=True)
    top1_file.write_text(json.dumps(top1_data), encoding='utf-8')
    
    narrator = EconomicHunterNarrator(base_dir)
    narrator.run()
    
    md_path = base_dir / "data/ops/issue_signal_narrative_today.md"
    if md_path.exists():
        content = md_path.read_text(encoding='utf-8')
        if "[⚡ WHY NOW – Escalated]" in content:
            print("✅ Success: Escalation block found in Markdown")
            # print(content)
        else:
            print("❌ Fail: Escalation block missing in Markdown")
            print("--- Actual Markdown Content ---")
            print(content)
            print("--- End Content ---")
    else:
        print("❌ Fail: Markdown not generated")

if __name__ == "__main__":
    run_test()
