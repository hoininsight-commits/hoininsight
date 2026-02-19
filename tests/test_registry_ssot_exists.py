
import os
import pytest
from pathlib import Path

def test_registry_ssot_exists():
    """
    [NEXT-1 PATCH] Task 1: Registry SSOT Exists & Load Check
    """
    root = Path(os.getcwd())
    registry_path = root / "registry"
    
    # 1. Assert registry folder exists
    assert registry_path.exists(), "FAIL: 'registry/' folder missing."
    assert registry_path.is_dir(), "FAIL: 'registry/' is not a directory."
    
    # 2. Assert 'schemas' subfolder exists
    schemas_path = registry_path / "schemas"
    assert schemas_path.exists(), "FAIL: 'registry/schemas' folder missing."
    assert schemas_path.is_dir(), "FAIL: 'registry/schemas' is not a directory."
    
    # 3. Assert at least one .yml/.yaml file exists (Recursive)
    yml_files = list(registry_path.rglob("*.yml")) + list(registry_path.rglob("*.yaml"))
    assert len(yml_files) > 0, "FAIL: No .yml or .yaml files found in registry/."
    
    print(f"\n✅ Registry SSOT Verified: Found {len(yml_files)} YAML files.")
    print(f"✅ Schema folder checked: {schemas_path}")

if __name__ == "__main__":
    test_registry_ssot_exists()
