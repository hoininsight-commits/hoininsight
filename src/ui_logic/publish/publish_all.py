from pathlib import Path
import os
from src.ui_logic.contracts.publish_ui_assets import publish_assets
from src.ui_logic.guards.legacy_report import write_report
from src.ui_logic.guards.legacy_hard_report import generate_readiness_report
from src.refactor.legacy_deprecation_scanner import scan_codebase
from src.refactor.publish_deprecation_ledger import publish_ledger

def run_publish(project_root: Path = None):
    """
    REF-006 Consolidated Publish Orchestrator.
    REF-010 Integration: Legacy Deprecation Guidance.
    """
    if project_root is None:
        project_root = Path(__file__).parent.parent.parent.parent
        
    print("\n[Canonical Publish] Starting...")
    
    # 1. Sync Assets
    publish_assets(project_root)
    
    # 2. Legacy Usage Monitoring (REF-007, REF-008)
    write_report(project_root)
    generate_readiness_report(project_root)
    
    # 3. Deprecation Scanning & Guidance (REF-010)
    ledger = scan_codebase()
    publish_ledger(project_root)
    
    # 4. Enforcement Check (REF-010)
    if os.getenv("HOIN_LEGACY_ENFORCE") == "1" and ledger["summary"]["high"] > 0:
        raise RuntimeError(f"[REF-010][BLOCK] critical legacy hits found: {ledger['summary']['high']}")

    print("\n[Canonical Publish] Complete. SSOT: data_outputs/ops/")

if __name__ == "__main__":
    run_publish()
