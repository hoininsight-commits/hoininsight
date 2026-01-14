from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from src.registry.loader import load_datasets
from src.reporters.data_snapshot import write_data_snapshot
from src.topics.persistence import count_appearances_7d
from src.topics.fusion import write_meta_topics
from src.topics.momentum import compute_momentum_7d

def _ymd() -> str:
    return datetime.utcnow().strftime("%Y/%m/%d")

def _read_json(p: Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8"))

def _exists_rel(base_dir: Path, rel: str) -> str:
    p = base_dir / rel
    return rel if p.exists() else "-"

def _collect_all_topics(base_dir: Path) -> List[Dict[str, Any]]:
    ymd = _ymd()
    datasets = [ds for ds in load_datasets(base_dir / "registry" / "datasets.yml") if ds.enabled]
    all_topics: List[Dict[str, Any]] = []
    for ds in datasets:
        tp = base_dir / "data" / "topics" / ymd / f"{ds.dataset_id}.json"
        if tp.exists():
            payload = _read_json(tp)
            if isinstance(payload, list):
                for t in payload:
                    if isinstance(t, dict):
                        t["_report_key"] = ds.report_key
                        t["_dataset_id"] = ds.dataset_id
                        all_topics.append(t)
    return all_topics

def write_daily_brief(base_dir: Path) -> Path:
    # Always emit snapshot alongside daily_brief (file-based dashboard)
    write_data_snapshot(base_dir)
    
    # Meta Topics
    meta_path = write_meta_topics(base_dir)
    meta_topics = []
    if meta_path.exists():
        try:
            meta_topics = json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    ymd = _ymd()
    out_dir = base_dir / "data" / "reports" / ymd
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "daily_brief.md"

    topics = _collect_all_topics(base_dir)

    enriched: List[Dict[str, Any]] = []
    for t in topics:
        if not isinstance(t.get("score", None), (int, float)):
            continue
        dataset_id = str(t.get("_dataset_id", ""))
        topic_id = str(t.get("topic_id", ""))
        
        # [Phase 22] Persistence
        appearances_7d = count_appearances_7d(base_dir, dataset_id, topic_id)
        # 1.0 + 0.15 * count => e.g. 1 appearance -> x1.15
        persistence_multiplier = 1.0 + 0.15 * float(appearances_7d)
        _final_score = float(t.get("score")) * persistence_multiplier
        
        # [Phase 23-B] Momentum
        momentum_meta = compute_momentum_7d(base_dir, dataset_id, topic_id)
        _momentum = momentum_meta["momentum"]
        _momentum_slope = momentum_meta["slope"]
        _momentum_n = momentum_meta["n"]
        _momentum_multiplier = momentum_meta["multiplier"]
        
        # Calculate final_score_m
        _final_score_m = _final_score * _momentum_multiplier
        
        t2 = dict(t)
        t2["_appearances_7d"] = int(appearances_7d)
        t2["_persistence_multiplier"] = float(persistence_multiplier)
        t2["_final_score"] = float(_final_score)
        
        t2["_momentum"] = _momentum
        t2["_momentum_slope"] = float(_momentum_slope)
        t2["_momentum_n"] = int(_momentum_n)
        t2["_momentum_multiplier"] = float(_momentum_multiplier)
        t2["_final_score_m"] = float(_final_score_m)

        enriched.append(t2)

    # Sort by final_score_m (Momentum-adjusted)
    enriched.sort(key=lambda x: float(x.get("_final_score_m", 0.0)), reverse=True)
    top5 = enriched[:5]

    lines: List[str] = []
    lines.append("# Phase 23-B 완료")
    lines.append(f"# Daily Brief: {ymd}")
    lines.append("")

    lines.append("## META TOPICS")
    if len(meta_topics) == 0:
        lines.append("- (no meta topics)")
    else:
        meta_topics.sort(key=lambda x: float(x.get("score", 0.0)), reverse=True)
        top_meta = meta_topics[:3]
        lines.append("")
        lines.append("| rank | title | score | severity | evidence |")
        lines.append("|---:|---|---:|---|---|")
        for i, m in enumerate(top_meta, 1):
             ev_str = ", ".join(m.get("evidence", []))
             lines.append(f"| {i} | {m.get('title')} | {m.get('score'):.2f} | {m.get('severity')} | {ev_str} |")
    lines.append("")

    lines.append("## TOP 5 Topics (Momentum Adjusted)")
    if len(top5) == 0:
        lines.append("- (no topics)")
    else:
        lines.append("")
        lines.append("| rank | report_key | title | base | persist(7d) | final | momentum(slope) | final_m | sev | chart | topics | anom |")
        lines.append("|---:|---|---|---:|---:|---:|---|---:|---|---|---|---|")
        for i, t in enumerate(top5, 1):
            dataset_id = str(t.get("_dataset_id", ""))
            chart_rel = _exists_rel(base_dir, f"data/reports/{ymd}/charts/{dataset_id}.png")
            topics_rel = _exists_rel(base_dir, f"data/topics/{ymd}/{dataset_id}.json")
            anomalies_rel = _exists_rel(base_dir, f"data/features/anomalies/{ymd}/{dataset_id}.json")

            chart_cell = f"[png]({chart_rel})" if chart_rel != "-" else "-"
            topics_cell = f"[json]({topics_rel})" if topics_rel != "-" else "-"
            anomalies_cell = f"[json]({anomalies_rel})" if anomalies_rel != "-" else "-"
            
            mom_str = f"{t.get('_momentum')} ({t.get('_momentum_slope'):.2f})"
            final_score_m_val = float(t.get('_final_score_m', 0.0))

            lines.append(
                f"| {i} | {t.get('_report_key','')} | {t.get('title','')} | {t.get('score'):.2f} | "
                f"{t.get('_appearances_7d')} (x{t.get('_persistence_multiplier'):.2f}) | {t.get('_final_score'):.2f} | "
                f"{mom_str} | **{final_score_m_val:.2f}** | {t.get('severity')} | "
                f"{chart_cell} | {topics_cell} | {anomalies_cell} |"
            )

    lines.append("")
    lines.append("## Per-dataset Topics")
    if len(enriched) == 0:
        lines.append("- (no topics)")
    else:
        for t in enriched:
            mom_line = f"Mom: {t.get('_momentum')} (slope={t.get('_momentum_slope'):.2f}) -> x{t.get('_momentum_multiplier')}"
            lines.append(
                f"- [{t.get('severity')}] {t.get('_report_key','')}: {t.get('title','')} "
                f"(base={t.get('score'):.2f}, final_m={t.get('_final_score_m'):.2f}) | {mom_line} | "
                f"App7d={t.get('_appearances_7d')}"
            )

    lines.append("")
    lines.append("## Data Snapshot")
    lines.append(f"- See: `data/reports/{ymd}/data_snapshot.md`")
    lines.append("")

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_path
