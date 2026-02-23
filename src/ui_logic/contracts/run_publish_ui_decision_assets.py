"""
[IS-100] Publish UI Decision Assets — Pipeline Source of Truth
=============================================================
This module is called by full_pipeline.yml AFTER `rm -rf docs/data` and BEFORE git push.
It is the SOLE authority for generating:
  - docs/data/decision/today.json
  - docs/data/decision/editorial/editorial_selection_*.json
  - docs/data/decision/manifest.json

DO NOT include daily_snapshot.json, ops, or market data in manifest.
"""

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(".")
DOCS_DECISION = ROOT / "docs" / "data" / "decision"
DATA_EDITORIAL = ROOT / "data" / "editorial"
DATA_DECISION  = ROOT / "data" / "decision"   # engine writes final_decision_card.json here
DOCS_TODAY     = ROOT / "docs" / "data" / "today.json"

# ---------------------------------------------------------------------------
# Schema validation helpers
# ---------------------------------------------------------------------------
_NON_DECISION_NAMES = {
    "daily_snapshot.json", "health.json", "build_meta.json",
    "collection_status.json", "event_coverage_today.json",
    "latest_run.json", "pipeline_status_v1.json",
}

def _is_decision_file(path: Path) -> bool:
    """Return True only for files that contain decision/editorial data."""
    if path.name in _NON_DECISION_NAMES:
        return False
    if path.suffix != ".json":
        return False
    return True


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Step 1: Publish today.json from final_decision_card (if available)
# ---------------------------------------------------------------------------
def _load_approval_titles() -> set:
    """Loads approved titles from engine gates to merge into UI cards."""
    approved_titles = set()
    try:
        f = ROOT / "data" / "ops" / "topic_speakability_today.json"
        if f.exists():
            data = json.loads(f.read_text(encoding="utf-8"))
            for v in data.get("verdicts", []):
                if v.get("speakability") == "SPEAKABLE_NOW":
                    approved_titles.add(v.get("title", ""))
    except Exception as e:
        print(f"[PUBLISH] warn loading topic_speakability_today: {e}")
        
    try:
        f2 = ROOT / "data" / "ops" / "auto_approved_today.json"
        if f2.exists():
            data2 = json.loads(f2.read_text(encoding="utf-8"))
            for a in data2.get("auto_approved", []):
                approved_titles.add(a.get("title", ""))
    except Exception as e:
        print(f"[PUBLISH] warn loading auto_approved_today: {e}")
        
    return approved_titles


def _publish_today() -> Optional[Dict]:
    """
    Copies the most recent final_decision_card.json → docs/data/decision/today.json.
    Falls back to docs/data/today.json (written by engine) if dated card is missing.
    Returns the manifest entry dict, or None if no source found.
    """
    kst_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")  # approx KST; fine for manifest
    ymd = kst_date.replace("-", "/")
    dated_card = DATA_DECISION / ymd / "final_decision_card.json"

    source = None
    if dated_card.exists():
        source = dated_card
        print(f"[PUBLISH] today.json source: {dated_card}")
    elif DOCS_TODAY.exists():
        source = DOCS_TODAY
        print(f"[PUBLISH] today.json source (fallback): {DOCS_TODAY}")

    if source is None:
        print("[PUBLISH] No today.json source found — skipping")
        return None

    dest = DOCS_DECISION / "today.json"
    shutil.copy2(source, dest)
    print(f"[PUBLISH] today.json → {dest}")

    # Read to get actual date from file and merge approvals
    try:
        data = json.loads(dest.read_text(encoding="utf-8"))
        file_date = data.get("date", kst_date) or kst_date
        
        # Merge approval status
        approved_titles = _load_approval_titles()
        if approved_titles and "top_topics" in data:
            changed = False
            for top in data["top_topics"]:
                if top.get("title") in approved_titles:
                    top["status"] = "APPROVED"
                    top["speakability"] = "OK"
                    changed = True
            if changed:
                dest.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
                
    except Exception:
        file_date = kst_date

    return {
        "path": "today.json",
        "type": "today",
        "date": file_date,
        "updated_at": _utc_now(),
    }


# ---------------------------------------------------------------------------
# Step 2: Publish editorial_selection_*.json
# ---------------------------------------------------------------------------
def _publish_editorial() -> List[Dict]:
    """
    Copies data/editorial/editorial_selection_*.json
    → docs/data/decision/editorial/editorial_selection_*.json
    Returns sorted list of manifest entry dicts (newest first).
    """
    entries = []
    if not DATA_EDITORIAL.exists():
        print("[PUBLISH] data/editorial/ not found — no editorial history to publish")
        return entries

    dest_dir = DOCS_DECISION / "editorial"
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    approved_titles = _load_approval_titles()

    for src in sorted(DATA_EDITORIAL.glob("editorial_selection_*.json")):
        dest = dest_dir / src.name
        shutil.copy2(src, dest)
        
        # Merge approval status
        try:
            ed_data = json.loads(dest.read_text(encoding="utf-8"))
            changed = False
            for pick in ed_data.get("picks", []):
                pick_title = pick.get("theme") or pick.get("title")
                if pick_title in approved_titles:
                    pick["status"] = "APPROVED"
                    changed = True
            if changed:
                dest.write_text(json.dumps(ed_data, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception as e:
            print(f"[PUBLISH] warn merging approvals for {src.name}: {e}")

        # Extract date from filename: editorial_selection_2026-02-23.json
        date_str = src.stem.replace("editorial_selection_", "")
        entries.append({
            "path": f"editorial/{src.name}",
            "type": "editorial",
            "date": date_str,
            "updated_at": _utc_now(),
        })

    entries.sort(key=lambda e: e["date"], reverse=True)
    print(f"[PUBLISH] editorial: {len(entries)} files → {dest_dir}")
    return entries

# ---------------------------------------------------------------------------
# Step 3: Copy legacy data/ui_decision/*.json (backward compat)
# ---------------------------------------------------------------------------
def _publish_legacy_ui_decision() -> List[Dict]:
    """
    Copies data/ui_decision/*.json → docs/data/decision/*.json
    Only copies files that pass the decision schema check.
    Does NOT add these to manifest (legacy; may be duplicates).
    """
    src_dir = ROOT / "data" / "ui_decision"
    if not src_dir.exists():
        return []
    copied = 0
    for f in src_dir.glob("*.json"):
        if not _is_decision_file(f):
            print(f"[PUBLISH] SKIP non-decision legacy file: {f.name}")
            continue
        shutil.copy2(f, DOCS_DECISION / f.name)
        copied += 1
    print(f"[PUBLISH] legacy ui_decision: {copied} files copied")
    return []


# ---------------------------------------------------------------------------
# Step 4: Write manifest.json
# ---------------------------------------------------------------------------
def _write_manifest(entries: List[Dict]) -> None:
    """
    Writes docs/data/decision/manifest.json.
    entries = list of { path, type, date, updated_at }
    Only decision/editorial types are included — never market snapshots.
    """
    manifest = {
        "generated_at": _utc_now(),
        "schema_version": "v2.5",
        "generated_by": "src.ui_logic.contracts.run_publish_ui_decision_assets",
        "files": entries,
        # UI compat (legacy key): flat list of path strings for operator_today/history.js
        "files_flat": [e["path"] for e in entries],
    }
    out = DOCS_DECISION / "manifest.json"
    out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[PUBLISH] manifest.json → {out}  ({len(entries)} entries)")

    # Sanity: assert no daily_snapshot in manifest
    bad = [e for e in entries if "snapshot" in e["path"] or "daily_snapshot" in e["path"]]
    if bad:
        raise RuntimeError(f"[PUBLISH][BUG] Non-decision files in manifest: {bad}")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
def run_publish():
    DOCS_DECISION.mkdir(parents=True, exist_ok=True)

    manifest_entries: List[Dict] = []

    # 1. Today
    today_entry = _publish_today()
    if today_entry:
        manifest_entries.append(today_entry)

    # 2. Editorial history
    manifest_entries.extend(_publish_editorial())

    # 3. Legacy (no manifest entries added)
    _publish_legacy_ui_decision()

    # 4. Write manifest
    _write_manifest(manifest_entries)

    print(f"[PUBLISH] Done. {len(manifest_entries)} manifest entries.")


if __name__ == "__main__":
    run_publish()

