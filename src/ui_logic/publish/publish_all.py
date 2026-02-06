from pathlib import Path
from src.ui_logic.contracts.publish_ui_assets import publish_assets
from src.ui_logic.guards.legacy_report import write_report
from src.ui_logic.guards.legacy_hard_report import generate_readiness_report

def run_publish(project_root: Path = None):
    """
    REF-006 Consolidated Publish Orchestrator.
    Treats data_outputs/ as the primary operational source.
    """
    if project_root is None:
        project_root = Path(__file__).parent.parent.parent.parent
        
    print("\n[Canonical Publish] Starting...")
    
    # Delegate to the unified logic (which mirrors to data_outputs and docs/data)
    publish_assets(project_root)
    
    # Generate Legacy Usage & Hard Readiness Reports
    write_report(project_root)
    generate_readiness_report(project_root)
    
    print("[Canonical Publish] Completed. SSOT: data_outputs/")

if __name__ == "__main__":
    run_publish()
