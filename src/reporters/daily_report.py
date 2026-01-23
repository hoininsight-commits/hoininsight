from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from src.registry.loader import load_datasets
try:
    from src.reporters.data_snapshot import write_data_snapshot
except ImportError:
    def write_data_snapshot(base_dir): return None
from src.topics.persistence import count_appearances_7d
from src.topics.fusion import write_meta_topics
from src.topics.momentum import compute_momentum_7d
from src.reporters.regime_card import build_regime_card
from src.topics.regime_history import update_regime_history
from src.strategies.regime_strategy_resolver import resolve_strategy_frameworks
from src.reporters.regime_review_reporter import get_historical_context_lines
from src.anomalies.narrative_drift_detector import detect_narrative_drift
from src.reporters.content_generator import generate_insight_content

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
    
    # [Ops Upgrade v1] Regime Confidence
    from src.ops.regime_confidence import calculate_regime_confidence
    conf_res = calculate_regime_confidence(base_dir / "data" / "dashboard" / "collection_status.json")
    conf_level = conf_res.get("regime_confidence", "LOW")
    bd = conf_res.get("core_breakdown", {})
    bd_str = ", ".join([f"{k}={v}" for k, v in bd.items()])
    lines.append(f"Confidence: {conf_level} (Core: {bd_str})")
    
    # [Ops Upgrade v1.1] Content Status
    from src.ops.content_gate import evaluate_content_gate
    gate_status = evaluate_content_gate(base_dir)
    c_mode = gate_status.get("content_mode", "UNKNOWN")
    lines.append(f"Content Status: {c_mode}")

    # [Ops Upgrade v1.2] Content Preset
    if c_mode != "SKIP":
        from src.ops.content_preset_selector import select_content_preset
        # Resolve Regime (fallback to card data)
        regime_title = card.structured_data.get("regime", "Unknown")
        has_meta = len(meta_topics) > 0
        preset_info = select_content_preset(regime_title, conf_level, has_meta)
        lines.append(f"Content Preset: {preset_info.get('preset', 'UNKNOWN')}")
    
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

    # [Phase 32] Proposal Priority Snapshot
    prio_path = base_dir / "data" / "narratives" / "prioritized" / ymd / "proposal_scores.json"
    if prio_path.exists():
        try:
            p_items = json.loads(prio_path.read_text(encoding="utf-8"))
            # Expecting already sorted by prioritization engine
            top_p = p_items[:3]
            
            lines.append("")
            lines.append("## PROPOSAL PRIORITY SNAPSHOT")
            if not top_p:
                lines.append("- No proposals scored today.")
            else:
                lines.append("| Rank | Video ID | Score | Why (Def/Evid/Reg/Imp) |")
                lines.append("|---:|---|---:|---|")
                for p in top_p:
                    lines.append(f"| {p.get('priority_rank')} | {p.get('video_id')} | **{p.get('alignment_score')}** | {p.get('score_breakdown')} |")
                
                lines.append("")
                lines.append(f"*See full prioritization list in `data/narratives/prioritized/{ymd}/proposal_scores.json`*")
        except:
            lines.append("## PROPOSAL PRIORITY SNAPSHOT")
            lines.append("- Error loading priority data.")
    
    # [Phase 33] Proposal Aging Snapshot
    aging_path = base_dir / "data" / "narratives" / "prioritized" / ymd / "proposal_scores_with_aging.json"
    if aging_path.exists():
        try:
            aging_data = json.loads(aging_path.read_text(encoding="utf-8"))
            if isinstance(aging_data, dict) and "items" in aging_data:
                aging_items = aging_data["items"]
            else:
                aging_items = aging_data if isinstance(aging_data, list) else []
            
            top_aged = aging_items[:3]
            
            lines.append("")
            lines.append("## PROPOSAL AGING SNAPSHOT")
            if not top_aged:
                lines.append("- No aged proposals today.")
            else:
                lines.append("| Rank | Video ID | Final Priority | Age (days) | Decay Factor | Status |")
                lines.append("|---:|---|---:|---:|---:|---|")
                for p in top_aged:
                    lines.append(f"| {p.get('final_priority_rank')} | {p.get('video_id')} | **{p.get('final_priority_score')}** | {p.get('age_days')} | {p.get('decay_factor')} | {p.get('status')} |")
                
                lines.append("")
                lines.append("Older proposals are deprioritized by decay (half-life: 7 days).")
        except:
            lines.append("## PROPOSAL AGING SNAPSHOT")
            lines.append("- Error loading aging data.")
    lines.append("")
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
            
    lines.append("")
    
    # [Phase 31-E] Applied Changes (Narrative-Driven)
    applied_sum_path = base_dir / "data" / "narratives" / "applied" / ymd / "applied_summary.json"
    if applied_sum_path.exists():
        try:
            as_data = json.loads(applied_sum_path.read_text(encoding="utf-8"))
            as_items = as_data.get("items", [])
            
            if as_items:
                lines.append("## APPLIED CHANGES (Narrative-Driven)")
                lines.append(f"Narrative feedback loop active. {len(as_items)} approved proposal(s) applied.")
                lines.append("")
                
                for it in as_items:
                    vid = it.get('video_id', 'unknown')
                    scopes = it.get('applied_scopes', [])
                    scope_str = ", ".join(scopes)
                    lines.append(f"- Approved narrative (video_id={vid}) resulted in additive update to {scope_str}.")
        except:
            pass

    # [Phase 34] Change Effectiveness Snapshot
    effectiveness_path = base_dir / "data" / "narratives" / "effectiveness" / ymd / "effectiveness.json"
    if effectiveness_path.exists():
        try:
            eff_data = json.loads(effectiveness_path.read_text(encoding="utf-8"))
            events = eff_data.get("events", [])
            
            if events:
                # Get most recent event
                latest = sorted(events, key=lambda x: x["applied_at"], reverse=True)[0]
                metrics = latest.get("metrics", {})
                
                lines.append("")
                lines.append("## CHANGE EFFECTIVENESS SNAPSHOT")
                lines.append(f"Latest applied change: {latest['event_id']} (applied {latest['applied_at']})")
                
                # Extract key deltas
                success_delta = metrics.get("pipeline_reliability", {}).get("delta")
                topics_delta = metrics.get("topics_count_avg", {}).get("delta")
                conf_delta = metrics.get("confidence_high_share", {}).get("delta")
                flip_delta = metrics.get("regime_flip_count", {}).get("delta")
                
                lines.append(f"- Success Rate Δ: {success_delta:+.2f}" if success_delta is not None else "- Success Rate Δ: N/A")
                lines.append(f"- Topics Count Δ: {topics_delta:+.1f}" if topics_delta is not None else "- Topics Count Δ: N/A")
                lines.append(f"- Confidence HIGH Share Δ: {conf_delta:+.2%}" if conf_delta is not None else "- Confidence HIGH Share Δ: N/A")
                lines.append(f"- Regime Flips Δ: {flip_delta:+d}" if flip_delta is not None else "- Regime Flips Δ: N/A")
        except:
            lines.append("")
            lines.append("## CHANGE EFFECTIVENESS SNAPSHOT")
            lines.append("- N/A")

    # [Phase 35] Rejection Ledger Snapshot
    ledger_path = base_dir / "data" / "narratives" / "ledger_summary" / ymd / "ledger_summary.json"
    if ledger_path.exists():
        try:
            ledger_data = json.loads(ledger_path.read_text(encoding="utf-8"))
            counts = ledger_data.get("counts_by_decision", {})
            recent_entries = ledger_data.get("recent_entries", [])
            
            lines.append("")
            lines.append("## REJECTION LEDGER SNAPSHOT")
            lines.append(f"Last 90 days: REJECTED={counts.get('REJECTED', 0)}, DEFERRED={counts.get('DEFERRED', 0)}, DUPLICATE={counts.get('DUPLICATE', 0)}")
            
            if recent_entries:
                newest = recent_entries[0]
                decision = newest.get("decision", "UNKNOWN")
                decided_at = newest.get("decided_at", "")[:10]
                reason = newest.get("reason", "No reason")[:80]  # Truncate
                lines.append(f"Newest: {decision} on {decided_at} - {reason}")
            else:
                lines.append("- No recent entries")
        except:
            lines.append("")
            lines.append("## REJECTION LEDGER SNAPSHOT")
            lines.append("- N/A")

    # [Phase 36] Auto Archive Snapshot
    archive_path = base_dir / "data" / "narratives" / "archive" / ymd / "archive_summary.json"
    if archive_path.exists():
        try:
            archive_data = json.loads(archive_path.read_text(encoding="utf-8"))
            total = archive_data.get("total_archived", 0)
            
            if total > 0:
                lines.append("")
                lines.append("## AUTO ARCHIVE SNAPSHOT")
                lines.append(f"Total archived today: {total} items (non-destructive)")
                
                # Show first archived item
                archived_items = archive_data.get("archived_items", [])
                if archived_items:
                    first = archived_items[0]
                    video_id = first.get("video_id", "")
                    decision = first.get("original_decision", "")
                    archive_reason = first.get("archive_reason", "")
                    lines.append(f"Example: {video_id} ({decision}) - {archive_reason}")
        except:
            pass

    # [Phase 36-B] Ops Health Snapshot
    fresh_path = base_dir / "data" / "ops" / "freshness" / ymd / "freshness_summary.json"
    if fresh_path.exists():
        try:
            fd = json.loads(fresh_path.read_text(encoding="utf-8"))
            overall = fd.get("overall_system_freshness_pct", 0)
            breaches = fd.get("sla_breach_count", 0)
            
            lines.append("")
            lines.append("## OPS HEALTH SNAPSHOT")
            if breaches > 0:
                lines.append(f"⚠️ SLA BREACH DETECTED: {breaches} axes stale (>6h)")
                lines.append(f"Affected: {', '.join(fd.get('sla_breach_axes', [])) or 'Unknown'}")
            else:
                lines.append("✅ All systems nominal - Data freshness within SLA")
                
            lines.append(f"- System Freshness: {overall}%")
        except:
            pass

    # [Phase 37] Revival Proposal Snapshot
    revival_path = base_dir / "data" / "narratives" / "revival" / ymd / "revival_proposals.json"
    if revival_path.exists():
        try:
            rv = json.loads(revival_path.read_text(encoding="utf-8"))
            items = rv.get("items", [])
            
            if items:
                lines.append("")
                lines.append("## REVIVAL PROPOSAL SNAPSHOT")
                lines.append(f"Engine proposed {len(items)} reconsideration(s) based on today's context.")
                
                # Show first revival item
                first = items[0]
                lines.append(f"- Candidate: {first.get('video_id')} (Was {first.get('original_decision')})")
                lines.append(f"- Reason: {first.get('revival_reason')}")
        except:
            pass

    # [Phase 37-B] Revival Ops Context
    evidence_path = base_dir / "data" / "narratives" / "revival" / ymd / "revival_evidence.json"
    loop_path = base_dir / "data" / "narratives" / "revival" / ymd / "revival_loop_flags.json"
    if evidence_path.exists():
        try:
            ev = json.loads(evidence_path.read_text(encoding="utf-8"))
            loops = {}
            if loop_path.exists():
                loops = json.loads(loop_path.read_text(encoding="utf-8"))
            
            ctx = ev.get("ops_context", {})
            loop_vids = loops.get("loop_detected_vids", [])
            
            lines.append("")
            lines.append("## REVIVAL OPS CONTEXT")
            lines.append(f"- Avg Freshness: {ctx.get('overall_system_freshness_pct', 0)}%")
            lines.append(f"- SLA Breach Count: {ctx.get('sla_breach_count', 0)}")
            if loop_vids:
                lines.append(f"- ⚠️ Cognitive Loop Warning: {len(loop_vids)} items repeating decisions")
            else:
                lines.append("- Cognitive Loop Guard: Nominal")
        except:
            pass

    # [Phase 38] Final Decision Card Snapshot
    card_path = base_dir / "data" / "decision" / ymd / "final_decision_card.json"
    print(f"[DEBUG] Card Path: {card_path} (Exists: {card_path.exists()})")
    if card_path.exists():
        try:
            print(f"[DEBUG] Loading card from {card_path}")
            card = json.loads(card_path.read_text(encoding="utf-8"))
            blocks = card.get("blocks", {})
            reg = blocks.get("regime", {})
            rev = blocks.get("revival", {})
            ops = blocks.get("ops", {})
            
            lines.append("")
            lines.append("## FINAL DECISION CARD SNAPSHOT")
            lines.append(f"- Regime: {reg.get('current_regime')} (Conf: {reg.get('confidence', 0):.1%})")
            lines.append(f"- Revival: {rev.get('proposal_count', 0)} candidate(s)")
            lines.append(f"- Ops Health: {ops.get('system_freshness', 0)}% Freshness")
            
            # [Phase 40] Show generated topics
            m_topic = card.get("topic")
            n_topics = card.get("narrative_topics", [])
            
            if m_topic:
                 lines.append(f"- Structural Topic: **{m_topic}**")
            elif n_topics:
                 lines.append(f"- Structural Topic: None (Found {len(n_topics)} Narrative Topics)")
                 for i, nt in enumerate(n_topics[:3], 1):
                     lines.append(f"  {i}. **{nt.get('topic_anchor')}**")
                     lines.append(f"     - Driver: {nt.get('narrative_driver')}")
                     lines.append(f"     - Risk: {nt.get('risk_note', 'N/A')}")
            else:
                 lines.append(f"- Topic: Pending")

            lines.append(f"- Prompt: {card.get('human_prompt')}")
        except:
            pass


    # [Phase 39] Topic Candidate Snapshot
    cand_path = base_dir / "data" / "topics" / "candidates" / ymd / "topic_candidates.json"
    if cand_path.exists():
        try:
            c_data = json.loads(cand_path.read_text(encoding="utf-8"))
            count_alive = c_data.get("alive_count", 0)
            
            lines.append("")
            lines.append("## TOPIC CANDIDATE SNAPSHOT")
            lines.append(f"Gate Filter Result: {count_alive} candidate(s) survived survival rules.")
            lines.append("No automatic selection performed. See Dashboard for details.")
        except:
            pass

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    
    # [Phase 30] Automated Insight Content
    generate_insight_content(base_dir)
    
    return out_path

if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent.parent
    write_daily_brief(base_dir)

