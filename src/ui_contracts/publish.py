from pathlib import Path
from src.ui_contracts.manifest_builder_v2 import build_manifest_v2
from src.ui.publish_ui_assets import publish_assets

def run_publish(project_root: Path = None):
    """
    Standard publish orchestrator for REF-002.
    1. Builds manifest v2 from registry.
    2. Publishes assets to docs/data/*.
    """
    if project_root is None:
        project_root = Path(__file__).parent.parent.parent
        
    print("\n[Publish Orchestrator] Starting...")
    
    # 1. Build Manifest v2
    build_manifest_v2(project_root)
    
    # 2. Publish Assets (Reuse REF-001 logic)
    publish_assets(project_root)
    
    print("[Publish Orchestrator] Completed.")

if __name__ == "__main__":
    run_publish()
