from __future__ import annotations

from datetime import datetime
from pathlib import Path

from src.reporting.run_log import RunResult, write_run_log, append_observation_log
from src.pipeline.run_collect import main as collect_main
from src.pipeline.run_normalize import main as normalize_main
from src.pipeline.run_anomaly import main as anomaly_main
from src.pipeline.run_topic import main as topic_main
from src.validation.output_check import run_output_checks

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
        collect_main()
        details_lines.append("collect: ok")
        normalize_main()
        details_lines.append("normalize: ok")
        anomaly_main()
        details_lines.append("anomaly: ok")
        topic_main()
        details_lines.append("topic: ok")

        # report (합본)
        from src.reporters.daily_report import write_daily_brief
        report_path = write_daily_brief(Path("."))
        details_lines.append(f"report: ok | {report_path.as_posix()}")

        # output checks
        chk = run_output_checks(Path("."))
        details_lines.extend(["checks:"] + chk.lines)
        if not chk.ok:
            raise RuntimeError("output checks failed")

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
