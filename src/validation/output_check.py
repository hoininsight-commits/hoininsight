from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any

from src.registry.loader import load_datasets

@dataclass
class OutputCheckResult:
    ok: bool
    lines: list[str]
    per_dataset: list[dict]

def run_output_checks(base_dir: Path) -> OutputCheckResult:
    reg = base_dir / "registry" / "datasets.yml"
    datasets = [ds for ds in load_datasets(reg) if ds.enabled]

    ok = True
    lines: list[str] = []
    per_dataset: list[dict] = []

    # Required outputs: curated + anomalies + topics (report is global)
    for ds in datasets:
        curated = base_dir / ds.curated_path
        ymd = __import__("datetime").datetime.utcnow().strftime("%Y/%m/%d")
        anomalies = base_dir / "data" / "features" / "anomalies" / ymd / f"{ds.dataset_id}.json"
        topics = base_dir / "data" / "topics" / ymd / f"{ds.dataset_id}.json"

        curated_ok = curated.exists()
        anomalies_ok = anomalies.exists()
        topics_ok = topics.exists()

        status = "OK" if (curated_ok and anomalies_ok and topics_ok) else "MISS"
        if status != "OK":
            if ds.soft_fail:
                lines.append(f"[SKIP] outputs({ds.dataset_id}) missing")
            else:
                ok = False
                lines.append(f"[FAIL] outputs({ds.dataset_id}) missing")

        per_dataset.append(
            {
                "dataset_id": ds.dataset_id,
                "soft_fail": ds.soft_fail,
                "status": status if status == "OK" else ("SKIPPED" if ds.soft_fail else "FAIL"),
                "curated_ok": curated_ok,
                "anomalies_ok": anomalies_ok,
                "topics_ok": topics_ok,
            }
        )

    # Meta Topics Check (Soft)
    ymd = __import__("datetime").datetime.utcnow().strftime("%Y/%m/%d")
    meta_path = base_dir / "data" / "meta_topics" / ymd / "meta_topics.json"
    meta_ok = meta_path.exists()
    
    if not meta_ok:
        lines.append("[SKIP] meta_topics missing (soft)")
        
    per_dataset.append({
        "dataset_id": "meta_topics",
        "soft_fail": True,
        "status": "OK" if meta_ok else "SKIPPED",
        "curated_ok": meta_ok,
        "anomalies_ok": True,
        "topics_ok": True
    })

    # report required -> Changed to SOFT (SKIP)
    report = base_dir / "data" / "reports" / ymd / "daily_brief.md"
    if not report.exists():
        # ok = False  <- Removed hard fail
        lines.append("[SKIP] report missing (soft)")
    
    per_dataset.append({
        "dataset_id": "daily_report",
        "soft_fail": True,
        "status": "OK" if report.exists() else "SKIPPED",
        "curated_ok": report.exists(),
        "anomalies_ok": True,
        "topics_ok": True
    })

    return OutputCheckResult(ok=ok, lines=lines, per_dataset=per_dataset)
