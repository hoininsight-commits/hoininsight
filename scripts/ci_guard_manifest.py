"""
CI Guard: Verify docs/data/decision/manifest.json
==================================================
Called by full_pipeline.yml "Verify Decision Manifest (CI Guard)" step.
Exits with code 1 if any assertion fails — this blocks deployment.

Assertions:
  1. manifest.files >= 1 entry
  2. All manifest paths exist on disk
  3. No daily_snapshot.json or market data in manifest
"""

import json
import sys
from pathlib import Path

BASE = Path("docs/data/decision")
MANIFEST = BASE / "manifest.json"


def main() -> None:
    if not MANIFEST.exists():
        print("❌ DEPLOY GUARD: manifest.json not found")
        sys.exit(1)

    m = json.loads(MANIFEST.read_text(encoding="utf-8"))

    # Support both v2.5 (files_flat) and legacy (files[] as strings or dicts)
    raw = m.get("files_flat") or m.get("files", [])
    files = []
    for entry in raw:
        if isinstance(entry, str):
            files.append(entry)
        elif isinstance(entry, dict):
            p = entry.get("path", "")
            if p:
                files.append(p)

    # Assertion 1: at least one entry
    if len(files) < 1:
        print("❌ DEPLOY GUARD: manifest has 0 entries — aborting deployment")
        sys.exit(1)

    # Assertion 2: all manifest paths exist on disk
    missing = [f for f in files if not (BASE / f).exists()]
    if missing:
        print(f"❌ DEPLOY GUARD: {len(missing)} manifest path(s) missing on disk:")
        for f in missing:
            print(f"   - {f}")
        sys.exit(1)

    # Assertion 3: no non-decision files
    bad = [f for f in files if "daily_snapshot" in f or ("snapshot" in f and "decision" not in f)]
    if bad:
        print(f"❌ DEPLOY GUARD: non-decision files in manifest: {bad}")
        sys.exit(1)

    schema = m.get("schema_version", "?")
    types = sorted(set(
        e.get("type", "?") for e in m.get("files", []) if isinstance(e, dict)
    ))
    print(f"✅ DEPLOY GUARD: manifest OK (schema={schema}, {len(files)} entries, types={types or ['string-list']})")


if __name__ == "__main__":
    main()
