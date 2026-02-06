from pathlib import Path
from src.ui_logic.contracts.publish_ui_assets import publish_assets

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
    
    print("[Canonical Publish] Completed. SSOT: data_outputs/")

if __name__ == "__main__":
    run_publish()
