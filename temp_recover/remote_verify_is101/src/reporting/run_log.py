from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

KST_OFFSET = "+0900"

@dataclass
class RunResult:
    started_utc: str
    finished_utc: str
    status: str
    details: str

def _utc_now_stamp() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

def write_run_log(report_dir: Path, result: RunResult) -> Path:
    report_dir.mkdir(parents=True, exist_ok=True)
    out = report_dir / "run_log.md"
    out.write_text(
        "\n".join(
            [
                "# Run Log",
                "",
                f"- started_utc: {result.started_utc}",
                f"- finished_utc: {result.finished_utc}",
                f"- status: {result.status}",
                "",
                "## details",
                "",
                "```",
                result.details.rstrip(),
                "```",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return out

def append_observation_log(obs_file: Path, line: str) -> None:
    obs_file.parent.mkdir(parents=True, exist_ok=True)
    if not obs_file.exists():
        obs_file.write_text("# OBSERVATION_LOG\n\n", encoding="utf-8")
    obs_file.write_text(obs_file.read_text(encoding="utf-8") + line, encoding="utf-8")
