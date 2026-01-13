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

def select_topics(base_dir: Path, dataset_id: str, anomalies_path: Path) -> Path:
    anomalies = json.loads(anomalies_path.read_text(encoding="utf-8")) if anomalies_path.exists() else []
    topics = []
    if anomalies:
        a0 = anomalies[0]
        topics.append(
            {
                "topic_id": f"topic_{dataset_id}_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}",
                "dataset_id": dataset_id,
                "title": f"{dataset_id} 변동성 이상징후 발생",
                "summary": "전일 대비 변화율이 임계치를 초과했습니다.",
                "score": int(a0.get("severity", 50)),
                "anomalies": anomalies,
                "supporting_datasets": [dataset_id],
                "why_bullets": [
                    "전일 대비 변화율 급등은 리스크/심리 변화를 선행하는 경우가 많음",
                    "단일 지표 이상징후가 다른 시장/자산으로 전이될 수 있음",
                ],
            }
        )

    y, m, d = _utc_date_parts()
    out_dir = base_dir / "data" / "topics" / y / m / d
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{dataset_id}.json"
    out_path.write_text(json.dumps(topics, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path
