from __future__ import annotations

from datetime import datetime
from pathlib import Path

from src.pipeline.run_collect import main as collect_main
from src.pipeline.run_normalize import main as normalize_main
from src.pipeline.run_anomaly import main as anomaly_main
from src.pipeline.run_topic import main as topic_main
from src.pipeline.run_report import main as report_main
from src.reporting.run_log import RunResult, write_run_log, append_observation_log

def _utc_now_stamp() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def _date_path_utc() -> Path:
    # UTC 기준으로 날짜 폴더 생성 (파일 기반 운영 단순화)
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
        report_main()
        details_lines.append("report: ok")
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

    # observation log (구조 변경 불필요라도 실행 관찰은 누적)
    obs_line = f"- {finished} | engine_run | status={status} | run_log={log_path.as_posix()}\n"
    append_observation_log(Path("docs") / "OBSERVATION_LOG.md", obs_line)

    # 실패 시에는 exit code로 GitHub Actions에 신호
    if status != "SUCCESS":
        raise SystemExit(1)

if __name__ == "__main__":
    main()
