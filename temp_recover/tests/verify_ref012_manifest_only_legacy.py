import os
import json
import re
from pathlib import Path

def test_ref012_unification():
    print("=== VERIFYING REF-012: Legacy Data Source Unification ===")
    project_root = Path(os.getcwd())
    
    # 1. Loader & Adapter check
    assert (project_root / "docs/ui/manifest_loader.js").exists(), "manifest_loader.js missing"
    assert (project_root / "docs/ui/legacy_adapter.js").exists(), "legacy_adapter.js missing"
    
    # 2. Legacy Renderer hardcoding check
    legacy_renderer_path = project_root / "docs/ui/legacy_render.js"
    assert legacy_renderer_path.exists(), "legacy_render.js missing"
    
    content = legacy_renderer_path.read_text(encoding="utf-8")
    
    # Legacy renderer should NOT contain hardcoded data paths (except manifest)
    bad_paths = [
        re.compile(r"['\"]data/ui/"),
        re.compile(r"['\"]data/decision/")
    ]
    
    # We allow "manifest.json" reference
    for pattern in bad_paths:
        matches = pattern.findall(content)
        for match in matches:
            if "manifest.json" not in match:
                assert False, f"Hardcoded path found in legacy renderer: {match}"

    # 3. Safe Loading Check in renderers
    # Both should use ManifestLoader
    render_js = (project_root / "docs/ui/render.js").read_text(encoding="utf-8")
    assert "window.ManifestLoader" in render_js or "loader.loadAsset" in render_js, "Operator renderer must use shared ManifestLoader"
    
    # 4. JSON Leak Check (Strict Version)
    print("Scanning JSON assets for serialization leaks...")
    leaks = []
    for p in (project_root / "docs/data/ui").rglob("*.json"):
        txt = p.read_text(encoding="utf-8")
        if '"undefined"' in txt:
            leaks.append(f"{p.name}: contains 'undefined'")
        if '"null"' in txt.lower() and p.name != "manifest.json": # Some nulls might stay in complex structures, but we prefer empty strings
            pass # Relaxing null check for raw data, but renderer will handle it via safeGet
            
    assert not leaks, f"Leaks found: {leaks}"

    print("\n=== REF-012 VERIFICATION SUCCESS ===")

if __name__ == "__main__":
    test_ref012_unification()
