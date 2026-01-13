from __future__ import annotations

from datetime import datetime
from pathlib import Path

from src.reporting.run_log import RunResult, write_run_log, append_observation_log
from src.registry.loader import load_datasets, get_callables

def _utc_now_stamp() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def _date_path_utc() -> Path:
    d = datetime.utcnow().strftime("%Y/%m/%d")
    return Path("data") / "reports" / d

def main():
    started = _utc_now_stamp()
    status = "SUCCESS"
    details_lines = []

    try:
        details_lines.append("engine: start")
        reg = Path("registry") / "datasets.yml"
        datasets = [d for d in load_datasets(reg) if d.enabled]
        details_lines.append(f"datasets: {len(datasets)}")

        for ds in datasets:
            details_lines.append(f"dataset: {ds.dataset_id}")
            fns = get_callables(ds)
            raw_path = fns["collector"](Path("."))
            details_lines.append(f" collect: ok | {raw_path}")
            curated_path = fns["normalizer"](Path("."))
            details_lines.append(f" normalize: ok | {curated_path}")

        # anomaly/topic/report는 파이프라인 스텝에서 일괄 수행(기존 구조 유지)
        details_lines.append("engine: done")
    except Exception as e:
        status = "FAIL"
        details_lines.append(f"error: {repr(e)}")

    finished = _utc_now_stamp()
    report_dir = _date_path_utc()
    result = RunResult(
        started_utc=started,
        finished_utc=finished,
        status=status,
        details="\n".join(details_lines),
    )
    log_path = write_run_log(report_dir, result)

    obs_line = f"- {finished} | engine_run | status={status} | run_log={log_path.as_posix()}\n"
    append_observation_log(Path("docs") / "OBSERVATION_LOG.md", obs_line)

    if status != "SUCCESS":
        raise SystemExit(1)

if __name__ == "__main__":
    main()
