import shutil
import os
from pathlib import Path

LEDGER_SRC = "data_outputs/ops/deprecation_ledger.json"
LEDGER_DEST = "docs/data/ops/deprecation_ledger.json"

def publish_ledger(project_root: Path = None):
    if project_root is None:
        project_root = Path(os.getcwd())
        
    src = project_root / LEDGER_SRC
    dest = project_root / LEDGER_DEST
    
    if not src.exists():
        print(f"[Publisher] Ledger source {src} not found. Skipping.")
        return
        
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    print(f"[Publisher] Published ledger to {LEDGER_DEST}")

if __name__ == "__main__":
    publish_ledger()
