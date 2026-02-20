import os
import json
from pathlib import Path

def test_ref011_stabilization():
    print("=== VERIFYING REF-011: Single Entry & Legacy Read-Only ===")
    project_root = Path(os.getcwd())
    
    # 1. Manifest exists
    manifest_path = project_root / "docs/data/ui/manifest.json"
    assert manifest_path.exists(), "manifest.json must exist in docs/data/ui"

    # 2. Router exists
    router_path = project_root / "docs/ui/router.js"
    assert router_path.exists(), "router.js must exist"

    # 3. Index.html wiring check
    index_path = project_root / "docs/ui/index.html"
    index_content = index_path.read_text(encoding="utf-8")
    assert 'id="legacy-view"' in index_content, "Legacy view container missing in index.html"
    assert 'src="router.js"' in index_content, "Router script mapping missing in index.html"
    assert 'src="legacy_readonly_wrapper.js"' in index_content, "Wrapper script mapping missing in index.html"

    # 4. Search for sensitive JS leaks in JSON assets
    print("\nScanning JSON assets for 'undefined' leaks...")
    leaks_found = []
    for p in (project_root / "docs/data/ui").rglob("*.json"):
        content = p.read_text(encoding="utf-8")
        if '"undefined"' in content or '"null"' in content.lower():
            # some nulls are allowed in JSON, but "undefined" as a string is never okay in HoinInsight standard
            if '"undefined"' in content:
                leaks_found.append(f"{p.name}: contains 'undefined' string")
    
    assert not leaks_found, f"Found UI data leaks:\n" + "\n".join(leaks_found)

    # 5. Legacy Read-Only Banner check
    wrapper_path = project_root / "docs/ui/legacy_readonly_wrapper.js"
    wrapper_content = wrapper_path.read_text(encoding="utf-8")
    assert "레거시 메인(읽기 전용)" in wrapper_content, "Read-only banner text missing in wrapper"

    # 6. Sidebar Navigation stabilization
    sidebar_path = project_root / "docs/ui/sidebar_registry_loader.js"
    sidebar_content = sidebar_path.read_text(encoding="utf-8")
    assert "오늘의 운영자 메인" in sidebar_content, "Sidebar missing operator link"
    assert "레거시 메인(읽기전용)" in sidebar_content, "Sidebar missing legacy link"

    print("\n=== REF-011 VERIFICATION SUCCESS ===")

if __name__ == "__main__":
    test_ref011_stabilization()
