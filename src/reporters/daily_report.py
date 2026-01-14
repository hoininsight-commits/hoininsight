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
from src.reporters.regime_card import build_regime_card
from src.topics.regime_history import update_regime_history
from src.strategies.regime_strategy_resolver import resolve_strategy_frameworks
from src.reporters.regime_review_reporter import get_historical_context_lines
from src.anomalies.narrative_drift_detector import detect_narrative_drift

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
    lines.append("# Phase 24 완료")
    lines.append(f"# Daily Brief: {ymd}")
    lines.append("")

    # [Phase 24] Regime Summary Card
    card = build_regime_card(base_dir, enriched)
    
    # [Phase 26] History & Persistence
    persistence_info = update_regime_history(base_dir, card.structured_data)
    
    lines.append("## REGIME SUMMARY")
    lines.append(card.regime_line)
    lines.append(card.drivers_line)
    meta_link_md = f"[json]({card.meta_link})" if card.meta_link != "-" else "-"
    lines.append(f"Meta topics: {meta_link_md}")
    
    # Persistence Message
    if persistence_info.get("is_new_regime"):
        lines.append("This is a newly formed regime, detected for the first time today.")
    else:
        days = persistence_info.get("persistence_days", 1)
        start = persistence_info.get("started_at", "unknown")
        lines.append(f"This regime has persisted for {days} consecutive days since {start}.")

    # [Phase 27] Strategy Context
    # Use basis_id if available (meta_topic_id) for better mapping, strictly falling back to regime string
    regime_id_for_strat = card.structured_data.get("basis_id", "")
    if not regime_id_for_strat:
        # Fallback to regime title if ID not present (e.g. driver based)
        regime_id_for_strat = card.structured_data.get("regime", "")
        
    p_days_val = persistence_info.get("persistence_days", 1)
    
    strat_info = resolve_strategy_frameworks(base_dir, regime_id_for_strat, p_days_val)
    frameworks = strat_info.get("strategy_frameworks", [])
    
    if frameworks:
        lines.append("")
        lines.append(f"Under this regime (persisting for {p_days_val} days), the following strategic frameworks are relevant:")
        for fw in frameworks:
            fname = fw.get("name", "Unknown")
            lines.append(f"- {fname}")
        
    lines.append("")

    # [Phase 28] Historical Context
    # current_regime string from persistence_info or card
    curr_r = persistence_info.get("current_regime", "Unknown")
    hist_lines = get_historical_context_lines(base_dir, curr_r)
    if hist_lines:
        lines.extend(hist_lines)
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
    
    # [Phase 29] Narrative Drift Signals
    drift_output = detect_narrative_drift(base_dir)
    drifts = drift_output.get("drifts", [])
    
    if drifts:
        lines.append("Narrative Drift Signals:")
        for d in drifts:
            typ = d.get("drift_type", "NONE")
            eid = d.get("entity_id", "Unknown")
            lines.append(f"- {eid}: {typ}")

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_path
