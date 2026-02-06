from pathlib import Path
from src.ui_logic.contracts.manifest_builder_v3 import build_manifest_v3
from src.ui_logic.contracts.publish_ui_assets import publish_assets

def run_publish(project_root: Path = None):
    """
    Standard publish orchestrator for REF-004.
    1. Builds manifest v3 from registry (with caps).
    2. Publishes assets to docs/data/*.
    """
    if project_root is None:
        project_root = Path(__file__).parent.parent.parent
        
    print("\n[Publish Orchestrator] Starting (v3)...")
    
    # 1. Build Manifest v3
    build_manifest_v3(project_root)
    
    # 2. Publish Assets (Reuse REF-001 logic)
    publish_assets(project_root)
    
    print("[Publish Orchestrator] Completed.")

if __name__ == "__main__":
    run_publish()
