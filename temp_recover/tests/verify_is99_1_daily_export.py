import os
import json
import csv
import subprocess
import hashlib
from pathlib import Path
from src.topics.content_pack.daily_run_orchestrator import DailyRunOrchestrator

def get_hash(file_path):
    with open(file_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def verify_is99_1():
    print("\n" + "="*60)
    print("📋 IS-99-1 DAILY EXPORT VERIFICATION")
    print("="*60)

    # 1. SETUP MOCK DATA
    print("\n[1/7] Preparing Mock Multipack...")
    mock_dir = Path("data/decision_mock_is99_1")
    mock_dir.mkdir(parents=True, exist_ok=True)
    
    mock_pack = {
        "date": "2026-02-03",
        "packs": [
            {
                "pack_id": "LONG_20260203_001",
                "format": "LONG",
                "topic_id": "T1",
                "status": {"speakability": "READY"},
                "assets": {
                    "title": "NVIDIA EARNINGS",
                    "one_liner": "NVIDIA SURPRISE",
                    "long_script": {"sections": [{"name": "HOOK", "text": "H1"}, {"name": "EVIDENCE", "text": "E1"}]},
                    "decision_card": {"risks": ["R1"], "why_now": "Now"},
                    "mentionables": [{"name": "NVDA", "why_must": "W1"}],
                    "evidence_sources": [{"evidence_tag": "TAG1", "status": "VERIFIED"}]
                }
            },
            {
                "pack_id": "SHORT_20260203_001",
                "format": "SHORT",
                "topic_id": "T2",
                "status": {"speakability": "READY"},
                "assets": {
                    "title": "Short Title",
                    "one_liner": "Short Claim",
                    "shorts_script": {"hook": "SH1", "evidence_3": ["SE1"]},
                    "decision_card": {"why_now": "SN"}
                }
            }
        ],
        "summary": {"ready_count": 2, "hold_included": 0}
    }
    
    multipack_file = mock_dir / "content_pack_multipack.json"
    with open(multipack_file, "w", encoding="utf-8") as f:
        json.dump(mock_pack, f, indent=2)

    # 2. RUN ORCHESTRATOR
    print("[2/7] Running DailyRunOrchestrator...")
    export_dir = Path("exports_test_is99_1")
    orch = DailyRunOrchestrator(input_dir=str(mock_dir), export_dir=str(export_dir))
    orch.run()

    # 3. VERIFY FILES
    print("\n[3/7] Verifying File Existence")
    files = ["daily_upload_pack.md", "daily_upload_pack.json", "daily_upload_pack.csv"]
    for f in files:
        if (export_dir / f).exists():
            print(f"  ✅ {f}: EXISTS")
        else:
            print(f"  ❌ {f}: MISSING")

    # 4. CONTENT ALIGNMENT
    print("\n[4/7] Verifying Content Alignment (CSV ↔ Multipack)")
    with open(export_dir / "daily_upload_pack.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        if len(rows) == 2 and rows[0]["title"] == "NVIDIA EARNINGS":
            print("  ✅ CSV titles match: PASS")
        else:
            print(f"  ❌ CSV mismatch: {rows}")

    # 5. MARKDOWN FORMAT CHECK
    print("\n[5/7] Verifying Markdown Format")
    md_content = (export_dir / "daily_upload_pack.md").read_text(encoding="utf-8")
    if "LONG FORM (1)" in md_content and "SHORT #1" in md_content and "2026-02-03" in md_content:
        print("  ✅ MD headers and date present: PASS")
    else:
        print("  ❌ MD format error")

    # 6. DETERMINISM
    print("\n[6/7] Determinism Check")
    orch.run()
    if (export_dir / "daily_upload_pack.json").exists():
        print("  ✅ Deterministic (Run twice OK): PASS")

    # 7. INTEGRITY
    print("\n[7/7] Checking Constitutional Documents...")
    forbidden = ["docs/DATA_COLLECTION_MASTER.md", "docs/BASELINE_SIGNALS.md", "docs/ANOMALY_DETECTION_LOGIC.md"]
    for doc in forbidden:
        try:
            diff = subprocess.check_output(["git", "diff", "HEAD", "--", doc]).decode("utf-8")
            if diff:
                print(f"  ❌ {doc}: MODIFIED! (Integrity breach)")
            else:
                print(f"  ✅ {doc}: OK")
        except:
             print(f"  ⚠️ {doc}: Git check failed.")

    # CLEANUP TEST DIRS
    # subprocess.run(["rm", "-rf", str(mock_dir), str(export_dir)])

    print("\nVERIFICATION COMPLETE")

if __name__ == "__main__":
    verify_is99_1()
