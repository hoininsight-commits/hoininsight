import shutil
import os
from pathlib import Path

def publish_assets(project_root: Path):
    """
    Synchronizes data/ui/ and data/decision/ to docs/data/ui/ and docs/data/decision/.
    Ensures docs/data/ targets only.
    """
    src_ui = project_root / "data" / "ui"
    src_decision = project_root / "data" / "decision"
    
    dest_base = project_root / "docs" / "data"
    dest_outputs = project_root / "data_outputs"
    
    # Standard docs/ targets
    dest_ui = dest_base / "ui"
    dest_decision = dest_base / "decision"
    
    # Enhanced data_outputs/ targets
    out_ui = dest_outputs / "ui"
    out_decision = dest_outputs / "decision"
    
    # Ensure manifest exists before publishing
    manifest_file = src_ui / "manifest.json"
    if not manifest_file.exists():
        print("[Publish] Manifest missing. Triggering ManifestBuilder...")
        # Redirect to new standard path
        try:
            from src.ui_logic.contracts.manifest_builder_v3 import build_manifest_v3 as build_m
        except ImportError:
            from src.ui.manifest_builder import build_manifest as build_m
        build_m(project_root)
        
    def sync_dir(src: Path, dest: Path):
        if not src.exists():
            print(f"[Publish] Source {src} does not exist. Skipping.")
            return
        
        dest.mkdir(parents=True, exist_ok=True)
        for item in src.iterdir():
            if item.is_file():
                shutil.copy2(item, dest / item.name)
                print(f"[Publish] Copied {item.name} to {dest}")

    print("\n[Publish] Synchronizing UI assets...")
    sync_dir(src_ui, dest_ui)
    sync_dir(src_ui, out_ui)
    
    print("\n[Publish] Synchronizing Decision assets...")
    sync_dir(src_decision, dest_decision)
    sync_dir(src_decision, out_decision)
    
    print("\n[Publish] Sync completed to docs/data/* and data_outputs/*")

if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent.parent
    publish_assets(project_root)
