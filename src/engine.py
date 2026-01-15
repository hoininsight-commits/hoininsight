from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

from src.reporting.run_log import RunResult, write_run_log, append_observation_log
from src.pipeline.run_collect import main as collect_main
from src.pipeline.run_normalize import main as normalize_main
from src.pipeline.run_anomaly import main as anomaly_main
from src.pipeline.run_topic import main as topic_main
from src.validation.output_check import run_output_checks
from src.reporters.daily_report import write_daily_brief
from src.reporting.health import write_health
from src.validation.schema_check import run_schema_checks

def _utc_now_stamp() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def _date_path_utc() -> Path:
    d = datetime.utcnow().strftime("%Y/%m/%d")
    return Path("data") / "reports" / d

def main(target_categories: list[str] = None):
    started = _utc_now_stamp()
    status = "SUCCESS"
    details_lines = []
    check_lines = []
    checks_ok = False
    per_dataset = []

    try:
        details_lines.append("engine: start")
        print("engine: start", file=sys.stderr)
        
        collect_main(target_categories)
        details_lines.append("collect: ok")
        print("collect: ok", file=sys.stderr)
        
        normalize_main(target_categories)
        details_lines.append("normalize: ok")
        print("normalize: ok", file=sys.stderr)
        
        anomaly_main()
        details_lines.append("anomaly: ok")
        print("anomaly: ok", file=sys.stderr)
        
        topic_main()
        details_lines.append("topic: ok")
        print("topic: ok", file=sys.stderr)

        report_path = write_daily_brief(Path("."))
        details_lines.append(f"report: ok | {report_path.as_posix()}")
        print(f"report: ok | {report_path.as_posix()}", file=sys.stderr)

        chk = run_output_checks(Path("."), target_categories)
        check_lines = chk.lines
        per_dataset = chk.per_dataset
        checks_ok = chk.ok
        details_lines.extend(["checks:"] + chk.lines)
        if not chk.ok:
            # We print detailed validation errors to stderr
            for line in chk.lines:
                print(f"validation: {line}", file=sys.stderr)
            raise RuntimeError("output checks failed")

        sch = run_schema_checks(Path("."), target_categories)
        details_lines.extend(["schema_checks:"] + sch.lines)
        if not sch.ok:
            for line in sch.lines:
                print(f"schema: {line}", file=sys.stderr)
            raise RuntimeError("schema checks failed")

        details_lines.append("engine: done")
        print("engine: done", file=sys.stderr)
        
    except Exception as e:
        status = "FAIL"
        err_msg = f"error: {repr(e)}"
        details_lines.append(err_msg)
        # CRITICAL: Print error to stderr so it appears in CI logs
        print(err_msg, file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)

    health_path = write_health(Path("."), status=status, checks_ok=checks_ok, check_lines=check_lines, per_dataset=per_dataset)
    details_lines.append(f"health: {health_path.as_posix()}")

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
        sys.exit(1)

if __name__ == "__main__":
    main()
