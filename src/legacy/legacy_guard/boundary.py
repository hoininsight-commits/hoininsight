import os
from pathlib import Path

# Paths that are officially recognized as "Legacy Context"
# Any file inside or matching these is allowed to contain legacy references (for now)
LEGACY_ROOTS = [
    "src/ui/",
    "src/legacy/",
    "docs/ui/",  # Existing view logic
    "src/collectors/", # Old path (legacy shims usually live here)
    "src/normalizers/",
    "src/engine/__init__.py", # Existing bridge to run_publish
    "src/ui_contracts/", # Existing bridge area
    "src/ui_logic/contracts/", # Existing bridge area
    "src/ui_logic/publish/",   # Existing bridge area
    "src/ui_logic/guards/",    # Monitoring area
    "src/ops/run_daily_pipeline.py", # Main orchestrator
    "scripts/", # Maintenance tool area
]

def is_legacy_context(file_path: str) -> bool:
    """
    Determines if the given file_path belongs to the legacy technical debt area.
    """
    # Normalize path to relative from project root
    p = Path(file_path)
    try:
        # If it's an absolute path, try to make it relative to cwd
        if p.is_absolute():
            rel_path = str(p.relative_to(os.getcwd()))
        else:
            rel_path = str(p)
    except ValueError:
        rel_path = str(p)

    rel_path = rel_path.replace("\\", "/")
    
    for root in LEGACY_ROOTS:
        if rel_path.startswith(root):
            return True
            
    return False
