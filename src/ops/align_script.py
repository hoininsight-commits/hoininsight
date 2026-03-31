import json
from pathlib import Path

def align_script(project_root, core_theme, script_data):
    """
    Ensures the video script is derived from the core theme.
    """
    # Check if core_theme or its key terms are in the script title/hook
    title = script_data.get("title", "")
    hook = script_data.get("hook", "")
    
    # 1. Clean up stale patterns in title and hook FIRST
    stale_patterns = ["Daily Market Convergence", "Market Narrative Missing", "Market Equilibrium"]
    for pattern in stale_patterns:
        if title and pattern in title:
            title = title.replace(pattern, core_theme)
        if hook and pattern in hook:
            hook = hook.replace(pattern, core_theme)

    # 2. Check if already aligned with theme
    if core_theme.lower() in title.lower() or core_theme.lower() in hook.lower():
        print(f"[Aligner] Script title/hook already contains theme '{core_theme}'")
        # Update and return even if 'aligned' to ensure stale patterns were removed
        aligned = script_data.copy()
        aligned["theme"] = core_theme
        aligned["title"] = title
        aligned["hook"] = hook
        return aligned
        
    print(f"[Aligner] ⚠️ Script mismatch. Aligning metadata and adding prefix.")
    
    aligned = script_data.copy()
    aligned["theme"] = core_theme
    aligned["title"] = f"[{core_theme}] {title}"
    aligned["hook"] = hook # Already cleaned up above
        
    return aligned

if __name__ == "__main__":
    sample = {"title": "Market Crash", "hook": "Watch out!"}
    print(json.dumps(align_script(".", "AI Power Constraint", sample), indent=2))
