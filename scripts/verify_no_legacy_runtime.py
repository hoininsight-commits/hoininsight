#!/usr/bin/env python3
"""
[STRUCTURE-FINAL-FREEZE] Legacy Runtime Checker
Ensures that the modern core (src/hoin, src/ui) does not depend on legacy modules.
"""
import sys
import re
from pathlib import Path

def main():
    print("--- [FREEZE-UI-STRUCTURE] Legacy Runtime Check ---")
    root = Path(".")
    src = root / "src"
    
    scan_dirs = [src / "hoin", src / "ui"]
    
    # Disallowed legacy packages. The modern architecture only allows src.hoin and src.ui conceptually.
    legacy_packages = ["engine", "ui_logic", "ops", "decision", "topics", "anomalies", "legacy"]
    
    legacy_regex = re.compile(r'^(?:import|from)\s+(src\.(' + '|'.join(legacy_packages) + r'))')
    
    # Allowlist existing files so we block NEW usages but don't break the current pipeline.
    allowlist = [
        "src/hoin/engine/orchestrator.py",
        "src/ui/multi_topic_selector.py",
        "src/ui/natural_language_mapper.py",
        "src/ui/capital_perspective_narrator.py",
        "src/ui/schedule_risk_calendar.py",
        "src/ui/sector_rotation_acceleration_detector.py",
        "src/ui/natural_language_summary.py",
        "src/ui/narrative_entry_hook_generator.py",
        "src/ui/manifest_builder.py",
        "src/ui/relationship_stress_generator.py",
        "src/ui/narrative_fusion_engine.py",
        "src/ui/ui_decision_contract.py",
        "src/ui/operator_dashboard_renderer.py",
        "src/ui/publish_ui_assets.py",
        "src/ui/expectation_gap_detector.py",
        "src/ui/operator_main_contract.py",
        "src/ui/risk_timeline_narrator.py",
        "src/ui/sector_rotation_exporter.py",
        "src/ui/operator_narrative_order_builder.py",
        "src/ui/time_to_money_resolver.py",
        "src/ui/valuation_reset_detector.py",
        "src/ui/policy_capital_script_exporter.py",
        "src/ui/policy_capital_transmission.py",
        "src/ui/expectation_gap_exporter.py"
    ]
    
    all_passed = True
    
    for d in scan_dirs:
        if not d.exists():
            continue
        for py_file in d.rglob("*.py"):
            # Skip allowlisted files to avoid breaking current CI. Ensure paths use forward slash.
            if str(py_file).replace("\\", "/") in allowlist:
                continue
            
            try:
                content = py_file.read_text(encoding="utf-8")
                for i, line in enumerate(content.splitlines(), 1):
                    match = legacy_regex.search(line.strip())
                    if match:
                        print(f"❌ [FAIL] Legacy import found in {py_file} (Line {i}): {line.strip()}")
                        all_passed = False
            except Exception as e:
                print(f"⚠️ [WARN] Could not read {py_file}: {e}")

    if not all_passed:
        print("\n❌ LEGACY RUNTIME CHECK FAILED.")
        print("Modern packages (src/hoin, src/ui) must not depend on legacy code.")
        sys.exit(1)
        
    print("\n✅ LEGACY RUNTIME CHECK PASSED.")
    sys.exit(0)

if __name__ == "__main__":
    main()
