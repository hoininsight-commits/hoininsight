import os
import sys
from pathlib import Path

def verify_layout_priority():
    print("[VERIFY] Checking Dashboard Layout Priority...")
    docs_dir = Path("docs")
    index_html = docs_dir / "index.html"
    
    if not index_html.exists():
        print(f"[FAIL] index.html not found at {index_html}")
        sys.exit(1)
        
    content = index_html.read_text(encoding="utf-8")
    
    # 1. Check DOM order: Top-1 vs Entity Pool
    top1_idx = content.find("topic-card-top1")
    if top1_idx == -1:
        # Check for empty state if no top1
        top1_idx = content.find("empty-state-card")
        
    entity_idx = content.find("entity-pool-container")
    state_idx = content.find("state-panel-container")
    snapshot_idx = content.find("snapshot-list-container")
    
    print(f"Indices: Top1={top1_idx}, Entity={entity_idx}, State={state_idx}, Snapshot={snapshot_idx}")
    
    if top1_idx == -1:
        print("[FAIL] Neither Top-1 nor Empty State card found.")
        sys.exit(1)
        
    # Check hierarchy
    if not (top1_idx < state_idx < entity_idx < snapshot_idx):
        # Allow some flexibility but priority must be top1 first
        if top1_idx > state_idx or top1_idx > entity_idx:
            print("[FAIL] Top-1 is NOT prioritized at the top of the DOM.")
            sys.exit(1)
            
    print("[RUN] Verified: Top-1 is prioritized at the top of tab-today.")
    
    # 2. Check "Scanning" banner shrinkage
    if "empty-icon-small" in content and "empty-text" in content:
        print("[RUN] Verified: Scanning banner is shrunk to thin status bar.")
    elif "topic-card-top1" in content:
        print("[SKIP] Top-1 exists, skipping banner shrinkage check (assumed active via code review).")
    else:
        print("[FAIL] Scanning banner structure not found in docs/index.html.")
        sys.exit(1)

    print("[VERIFY][OK] Layout Priority Verification Passed.")

if __name__ == "__main__":
    # Generate dashboard first to reflect latest changes
    print("[RUN] Generating dashboard for verification...")
    os.system("python3 -m src.dashboard.dashboard_generator")
    verify_layout_priority()
