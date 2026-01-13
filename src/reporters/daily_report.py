from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pandas as pd

def _utc_date_parts() -> tuple[str, str, str]:
    return (
        datetime.utcnow().strftime("%Y"),
        datetime.utcnow().strftime("%m"),
        datetime.utcnow().strftime("%d"),
    )

def write_daily_brief(base_dir: Path, topics_path: Path) -> Path:
    y, m, d = _utc_date_parts()
    out_dir = base_dir / "data" / "reports" / y / m / d
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "daily_brief.md"

    topics = json.loads(topics_path.read_text(encoding="utf-8"))
    curated = base_dir / "data" / "curated" / "crypto" / "btc_usd.csv"
    df = pd.read_csv(curated)
    last_row = df.iloc[-1].to_dict() if len(df) else {}

    lines = [
        f"# Daily Brief ({y}-{m}-{d})",
        "",
        "## BTC/USD",
        f"- last_ts_utc: {last_row.get('ts_utc', '')}",
        f"- last_price_usd: {last_row.get('value', '')}",
        "",
        "## Topics",
    ]
    if not topics:
        lines.append("- (no topics today)")
    else:
        for t in topics:
            lines.append(f"- {t['title']} | score={t['score']}")
            lines.append(f"  - {t['summary']}")

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_path
