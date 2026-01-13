from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

def _utc_date_parts() -> tuple[str, str, str]:
    return (
        datetime.utcnow().strftime("%Y"),
        datetime.utcnow().strftime("%m"),
        datetime.utcnow().strftime("%d"),
    )

def select_topics(base_dir: Path, anomalies_path: Path) -> Path:
    anomalies = json.loads(anomalies_path.read_text(encoding="utf-8"))
    topics = []
    if anomalies:
        a0 = anomalies[0]
        topics.append(
            {
                "topic_id": f"topic_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}",
                "title": "BTC 변동성 이상징후 발생",
                "summary": "BTC/USD 전일 대비 변화율이 임계치를 초과했습니다.",
                "score": int(a0.get("severity", 50)),
                "anomalies": anomalies,
                "supporting_datasets": ["crypto_btc_usd_spot_coingecko"],
                "why_bullets": [
                    "전일 대비 변화율 급등은 리스크/심리 변화를 선행하는 경우가 많음",
                    "단일 자산이 아니라 전체 위험자산 변동성 확대로 확산될 수 있음",
                ],
            }
        )

    y, m, d = _utc_date_parts()
    out_dir = base_dir / "data" / "topics" / y / m / d
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "topics.json"
    out_path.write_text(json.dumps(topics, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path
