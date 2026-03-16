"""
[IS-100] Publish UI Decision Assets — Pipeline Source of Truth
=============================================================
This module is called by full_pipeline.yml AFTER `rm -rf docs/data` and BEFORE git push.
It is the SOLE authority for generating:
  - docs/data/decision/today.json
  - docs/data/decision/editorial/editorial_selection_*.json
  - docs/data/decision/manifest.json

DO NOT include daily_snapshot.json, ops, or market data in manifest.

NOTE: This script primary source of truth is 'data/ops/' and 'data/decision/'.
It maintains 'data_outputs/ops/' as a legacy compatibility mirror.
"""

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(".")
DOCS_DECISION = ROOT / "docs" / "data" / "decision"
DATA_EDITORIAL = ROOT / "data" / "editorial"
DATA_DECISION  = ROOT / "data" / "decision"
DATA_OPS       = ROOT / "data" / "ops"
DATA_OUTPUTS_OPS = ROOT / "data_outputs" / "ops" # Legacy Mirror
DOCS_TODAY     = ROOT / "docs" / "data" / "today.json"

_NON_DECISION_NAMES = {
    "daily_snapshot.json", "health.json", "build_meta.json",
    "collection_status.json", "event_coverage_today.json",
    "latest_run.json", "pipeline_status_v1.json",
}

def _is_decision_file(path: Path) -> bool:
    if path.name in _NON_DECISION_NAMES: return False
    if path.suffix != ".json": return False
    return True

def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def _load_approval_titles() -> set:
    approved_titles = set()
    try:
        f = DATA_OPS / "topic_speakability_today.json"
        if f.exists():
            data = json.loads(f.read_text(encoding="utf-8"))
            for v in data.get("verdicts", []):
                if v.get("speakability") == "SPEAKABLE_NOW": approved_titles.add(v.get("title", ""))
    except Exception as e: print(f"[PUBLISH] warn loading topic_speakability_today: {e}")
    try:
        f2 = DATA_OPS / "auto_approved_today.json"
        if f2.exists():
            data2 = json.loads(f2.read_text(encoding="utf-8"))
            for a in data2.get("auto_approved", []): approved_titles.add(a.get("title", ""))
    except Exception as e: print(f"[PUBLISH] warn loading auto_approved_today: {e}")
    return approved_titles

def _load_narrative_data() -> Dict[str, Dict]:
    narrative_map = {}
    try:
        f = DATA_OPS / "narrative_intelligence_v2.json"
        if f.exists():
            data = json.loads(f.read_text(encoding="utf-8"))
            for t in data.get("topics", []):
                title = t.get("title", "")
                topic_id = t.get("topic_id", "")
                n_data = {
                    "narrative_score": t.get("final_narrative_score", t.get("narrative_score", 0)),
                    "video_ready": t.get("video_ready", False),
                    "actor_tier_score": t.get("actor_tier_score", 0),
                    "escalation_flag": t.get("escalation_flag", False),
                    "conflict_flag": t.get("conflict_flag", False),
                    "cross_axis_multiplier": t.get("cross_axis_multiplier", 1.0),
                    "causal_chain": t.get("causal_chain", {}),
                    "rationale": t.get("rationale_natural", "")
                }
                if title: narrative_map[title] = n_data
                if topic_id: narrative_map[topic_id] = n_data
                refs = t.get("evidence_refs", {})
                for sid in refs.get("source_ids", []):
                    clean_sid = sid.split("_202")[0] if "_202" in sid else sid
                    narrative_map[clean_sid] = n_data
                    narrative_map[sid] = n_data
    except Exception as e: print(f"[PUBLISH] warn loading narrative_intelligence_v2: {e}")
    return narrative_map

def _publish_today() -> Optional[Dict]:
    # Correct KST logic: UTC+9
    from datetime import timedelta
    now_utc = datetime.now(timezone.utc)
    kst_now = now_utc + timedelta(hours=9)
    kst_date = kst_now.strftime("%Y-%m-%d")
    
    ymd = kst_date.replace("-", "/")
    dated_card = DATA_DECISION / ymd / "final_decision_card.json"
    
    # Priority: 1. Today's dated card, 2. Previous version on docs/data/decision/today.json (self-fallback)
    source = dated_card if dated_card.exists() else None
    if source is None:
        print(f"[PUBLISH] warn: No dated card found for {kst_date} at {dated_card}")
        return None
    dest = DOCS_DECISION / "today.json"
    shutil.copy2(source, dest)
    try:
        data = json.loads(dest.read_text(encoding="utf-8"))
        file_date = data.get("date", kst_date) or kst_date
        approved_titles = _load_approval_titles()
        narrative_map = _load_narrative_data()
        topics_to_check = data if isinstance(data, list) else (data.get("top_topics", [data]) if isinstance(data, dict) else [])
        changed = False
        for top in topics_to_check:
            if not isinstance(top, dict): continue
            title, topic_id = top.get("title", ""), top.get("topic_id", "")
            if title in approved_titles: top["status"], top["speakability"], changed = "APPROVED", "OK", True
            
            dataset_id = top.get("dataset_id")
            n_key = None
            if dataset_id:
                if dataset_id in narrative_map:
                    n_key = dataset_id
                else:
                    n_key = next((k for k in narrative_map.keys() if dataset_id == k or (isinstance(k, str) and dataset_id in k)), None)
            
            if not n_key and title in narrative_map: n_key = title
            
            if n_key:
                n_data = narrative_map[n_key]
                for k in ["narrative_score", "video_ready", "actor_tier_score", "escalation_flag", "conflict_flag", "cross_axis_multiplier"]: 
                    top[k] = n_data.get(k)
                if n_data.get("causal_chain"): top["causal_chain"] = n_data["causal_chain"]
                if n_data.get("rationale"): top["rationale"] = n_data["rationale"]
                if top.get("conflict_flag") and top.get("dataset_id") != "human_selection":
                    cam = top.get("cross_axis_multiplier", 1.0)
                    top["logic_block"] = f"CONFLICT DETECTED (x{cam})"
                changed = True
            if top.get("intensity") is None and top.get("score") is not None:
                try: top["intensity"], changed = float(top["score"]), True
                except: pass
            if "narrative_score" not in top: top["narrative_score"], changed = None, True
            
            # Merge refined titles if available from Topic Formatter
            try:
                topic_f = DATA_OPS / "economic_hunter_topic.json"
                if topic_f.exists():
                    tf_data = json.loads(topic_f.read_text(encoding="utf-8"))
                    if tf_data.get("title_refined"):
                        top["title_refined"] = tf_data["title_refined"]
                        top["title_raw"] = tf_data.get("title_raw", top.get("title"))
                        changed = True
            except: pass
        if changed:
            if isinstance(data, dict) and "top_topics" in data and len(data["top_topics"]) > 0:
                t0 = data["top_topics"][0]
                if t0.get("conflict_flag"):
                    pass # Placeholder logic removed. Deliver original engine result.
            dest.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as e: print(f"[PUBLISH] error in _publish_today: {e}"); file_date = kst_date

    # [STEP-20] Enrich today.json with Portfolio Relevance summary
    try:
        pr_path = DATA_OPS / "portfolio_relevance.json"
        if pr_path.exists() and dest.exists():
            pr_data = json.loads(pr_path.read_text(encoding="utf-8"))
            today_data = json.loads(dest.read_text(encoding="utf-8"))
            if isinstance(today_data, dict):
                theme = pr_data.get("top_portfolio_theme", {})
                today_data["portfolio_focus"] = theme.get("portfolio_focus", "")
                today_data["portfolio_theme"] = theme.get("theme", "")
                today_data["core_picks"] = [
                    {"name": p["name"], "ticker": p["ticker"], "score": p["portfolio_relevance_score"],
                     "impact_direction": p["impact_direction"], "action_note": p["action_note"]}
                    for p in pr_data.get("core_picks", [])[:5]
                ]
                today_data["tactical_picks"] = [
                    {"name": p["name"], "ticker": p["ticker"], "score": p["portfolio_relevance_score"],
                     "impact_direction": p["impact_direction"], "action_note": p["action_note"]}
                    for p in pr_data.get("tactical_picks", [])[:5]
                ]
                today_data["watchlist_picks"] = [
                    {"name": p["name"], "ticker": p["ticker"], "score": p["portfolio_relevance_score"],
                     "impact_direction": p["impact_direction"], "action_note": p["action_note"]}
                    for p in pr_data.get("watchlist_picks", [])[:5]
                ]
                dest.write_text(json.dumps(today_data, indent=2, ensure_ascii=False), encoding="utf-8")
                print(f"[PUBLISH] ✅ Portfolio Relevance merged into today.json")
    except Exception as e:
        print(f"[PUBLISH] ⚠️ Portfolio Relevance merge failed: {e}")

    # [STEP-30] Enrich today.json with Operator Action summary
    try:
        oa_path = DATA_OPS / "operator_actions.json"
        if oa_path.exists() and dest.exists():
            oa_data = json.loads(oa_path.read_text(encoding="utf-8"))
            today_data = json.loads(dest.read_text(encoding="utf-8"))
            if isinstance(today_data, dict) and len(oa_data) > 0:
                top_action = oa_data[0]
                today_data["operator_action"] = top_action.get("action", "")
                today_data["operator_theme"] = top_action.get("theme", "")
                today_data["operator_focus"] = top_action.get("recommended_focus", [])
                dest.write_text(json.dumps(today_data, indent=2, ensure_ascii=False), encoding="utf-8")
                print(f"[PUBLISH] ✅ Operator Action merged into today.json")
    except Exception as e:
        print(f"[PUBLISH] ⚠️ Operator Action merge failed: {e}")

    # [STEP-31] Enrich today.json with Auto Script status
    try:
        as_path = DATA_OPS.parent / "content" / "auto_scripts.json"
        if as_path.exists() and dest.exists():
            as_data = json.loads(as_path.read_text(encoding="utf-8"))
            today_data = json.loads(dest.read_text(encoding="utf-8"))
            if isinstance(today_data, dict):
                today_data["auto_script_available"] = len(as_data) > 0
                if len(as_data) > 0:
                    today_data["auto_script_theme"] = as_data[0].get("theme", "")
                dest.write_text(json.dumps(today_data, indent=2, ensure_ascii=False), encoding="utf-8")
                print(f"[PUBLISH] ✅ Auto Script status merged into today.json")
    except Exception as e:
        print(f"[PUBLISH] ⚠️ Auto Script merge failed: {e}")

    # [STEP-33] Enrich today.json for Market Prediction Benchmark
    try:
        # [STEP-33] Market Prediction Benchmark
        today_data = json.loads(dest.read_text(encoding="utf-8")) # Reload to ensure latest state
        benchmark_path = DATA_OPS / "market_prediction_benchmark.json"
        if benchmark_path.exists() and isinstance(today_data, dict):
            with open(benchmark_path, 'r', encoding='utf-8') as f:
                benchmark = json.load(f)
                today_data["market_state"] = benchmark.get("benchmark_summary", {}).get("market_state", today_data.get("market_state", "N/A"))
                today_data["liquidity_state"] = benchmark.get("liquidity", {}).get("state", "N/A")
                today_data["macro_regime"] = benchmark.get("macro_regime", {}).get("regime", "N/A")
                today_data["risk_state"] = benchmark.get("risk", {}).get("state", "N/A")
                today_data["structural_focus"] = benchmark.get("structural_shift", {}).get("active_shifts", [{}])[0].get("theme", "N/A")
                print("[PUBLISH] ✅ Market Prediction Benchmark merged into today.json")

        # [STEP-34] Market Contradiction Engine
        contradiction_path = ROOT / "data" / "contradictions" / "contradiction_state.json"
        if contradiction_path.exists() and isinstance(today_data, dict):
            with open(contradiction_path, 'r', encoding='utf-8') as f:
                contra_data = json.load(f)
                today_data["contradictions"] = contra_data.get("contradictions", [])
                print(f"[PUBLISH] ✅ Contradiction Engine merged into today.json")

        # [STEP-39] Theme Early Detection Engine
        early_path = ROOT / "data" / "theme" / "top_early_theme.json"
        if early_path.exists() and isinstance(today_data, dict):
            with open(early_path, 'r', encoding='utf-8') as f:
                early_data = json.load(f)
                today_data["early_theme"] = {
                    "theme": early_data.get("theme", "N/A"),
                    "score": early_data.get("score", 0),
                    "stage": early_data.get("stage", "N/A")
                }
                print(f"[PUBLISH] ✅ Early Detection Engine merged into today.json")
        
        # [STEP-35] Market Story Engine
        story_path = ROOT / "data" / "story" / "today_story.json"
        if story_path.exists() and isinstance(today_data, dict):
            with open(story_path, 'r', encoding='utf-8') as f:
                story_data = json.load(f)
                today_data["market_story"] = {
                    "title": story_data.get("title", ""),
                    "summary": story_data.get("summary", ""),
                    "featured_theme": story_data.get("featured_theme", "")
                }
                print(f"[PUBLISH] ✅ Market Story Engine merged into today.json")

        # [STEP-36] Impact & Mentionables Engine
        mentionables_path = ROOT / "data" / "story" / "impact_mentionables.json"
        if mentionables_path.exists() and isinstance(today_data, dict):
            with open(mentionables_path, 'r', encoding='utf-8') as f:
                men_data = json.load(f)
                today_data["mentionable_stocks"] = men_data.get("mentionable_stocks", [])
                print(f"[PUBLISH] ✅ Mentionables Engine merged into today.json")

        # [STEP-38] Topic Pressure & Selection Engine
        topic_path = ROOT / "data" / "topic" / "top_topic.json"
        if topic_path.exists() and isinstance(today_data, dict):
            with open(topic_path, 'r', encoding='utf-8') as f:
                topic_data = json.load(f)
                today_data["top_topic"] = {
                    "selected": topic_data.get("selected_topic", "N/A"),
                    "pressure": topic_data.get("topic_pressure", 0)
                }
                print(f"[PUBLISH] ✅ Topic Pressure Engine merged into today.json")

        # [STEP-37] Video Script Engine
        script_path = ROOT / "data" / "content" / "today_video_script.json"
        if script_path.exists() and isinstance(today_data, dict):
            with open(script_path, 'r', encoding='utf-8') as f:
                script_data = json.load(f)
                today_data["video_script_preview"] = {
                    "hook": script_data.get("hook", ""),
                    "action": script_data.get("operator_action", "WATCH")
                }
                print(f"[PUBLISH] ✅ Video Script Engine merged into today.json")
        
        # Write back the updated today_data if any changes were made in this block
        dest.write_text(json.dumps(today_data, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        print(f"[PUBLISH] ⚠️ Market Prediction Benchmark/Contradiction merge failed: {e}")

    return {"path": "today.json", "type": "today", "date": file_date, "updated_at": _utc_now()}

def _publish_editorial() -> List[Dict]:
    entries = []
    if not DATA_EDITORIAL.exists(): return entries
    dest_dir = DOCS_DECISION / "editorial"
    dest_dir.mkdir(parents=True, exist_ok=True)
    approved_titles = _load_approval_titles()
    narrative_map = _load_narrative_data()
    for src in sorted(DATA_EDITORIAL.glob("editorial_selection_*.json")):
        dest = dest_dir / src.name
        shutil.copy2(src, dest)
        try:
            ed_data = json.loads(dest.read_text(encoding="utf-8"))
            changed = False
            for pick in ed_data.get("picks", []):
                pick_title = pick.get("theme") or pick.get("title")
                if pick_title in approved_titles: pick["status"], changed = "APPROVED", True
                if pick_title in narrative_map:
                    n_data = narrative_map[pick_title]
                    for k in ["narrative_score", "actor_tier_score", "video_ready"]: pick[k] = n_data.get(k)
                    pick["escalation_flag"] = n_data.get("escalation_flag", False)
                    pick["conflict_flag"] = n_data.get("conflict_flag", False)
                    if n_data.get("causal_chain"): pick["causal_chain"] = n_data["causal_chain"]
                    changed = True
                if pick.get("intensity") is None and pick.get("score") is not None: pick["intensity"], changed = pick["score"], True
                if "narrative_score" not in pick:
                    pick["narrative_score"] = pick["actor_tier_score"] = None
                    pick["video_ready"] = pick.get("promotion_hint") == "DAILY_LONG"
                    changed = True
                if "intensity" not in pick: pick["intensity"] = pick.get("score") or pick.get("narrative_score") or 0; changed = True
            if changed: dest.write_text(json.dumps(ed_data, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception as e: print(f"[PUBLISH] warn merging approvals for {src.name}: {e}")
        entries.append({"path": f"editorial/{src.name}", "type": "editorial", "date": src.stem.replace("editorial_selection_", ""), "updated_at": _utc_now()})
    entries.sort(key=lambda e: e["date"], reverse=True)
    return entries

def _publish_legacy_ui_decision() -> List[Dict]:
    src_dir = ROOT / "data" / "ui_decision"
    if not src_dir.exists(): return []
    for f in src_dir.glob("*.json"):
        if _is_decision_file(f): shutil.copy2(f, DOCS_DECISION / f.name)
    return []

def _write_manifest(entries: List[Dict]) -> None:
    manifest = {"generated_at": _utc_now(), "schema_version": "v2.5", "generated_by": "src.ui_logic.contracts.run_publish_ui_decision_assets", "files": entries, "files_flat": [e["path"] for e in entries]}
    out = DOCS_DECISION / "manifest.json"
    out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

def main():
    DOCS_DECISION.mkdir(parents=True, exist_ok=True)
    manifest_entries = []
    today_entry = _publish_today()
    if today_entry: manifest_entries.append(today_entry)
    manifest_entries.extend(_publish_editorial())
    _publish_legacy_ui_decision()
    _publish_ops_assets()
    _write_manifest(manifest_entries)

def _publish_ops_assets():
    dest_dir = ROOT / "docs" / "data" / "ops"
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    # Authority: data/ops/
    # Legacy Mirror: data_outputs/ops/
    
    files_to_publish = [
        "structural_top1_today.json",
        "video_candidate_pool.json",
        "video_script_pack.json",
        "video_script_pack.md",
        "stock_linkage_pack.json",
        "conflict_density_pack.json",
        "regime_state.json",
        "investment_os_state.json",
        "investment_os_brief.md",
        "capital_allocation_state.json",
        "capital_allocation_brief.md",
        "timing_state.json",
        "timing_brief.md",
        "probability_compression_state.json",
        "probability_compression_brief.md",
        "meta_volatility_state.json",
        "meta_volatility_brief.md",
        "phase15_detection_diagnostics.md",
        "phase15_conflict_trace.md",
        "topic_probability_ranking.json",
        "economic_hunter_radar.json",
        "topic_predictions.json",
        "narrative_propagation.json",
        "capital_flow_impact.json",
        "portfolio_relevance.json",
        "system_health.json",
        "usage_audit.json",
        "../memory/narrative_patterns.json",
        "../memory/narrative_cycles.json",
        "../memory/theme_evolution.json",
        "early_topic_candidates.json",
        "narrative_escalation.json",
        "operator_actions.json",
        "../content/auto_scripts.json",
        "../decision/predicted_narratives.json",
        "../decision/mentionables.json",
        "../ontology/topic_resolved.json",
        "../ontology/topic_ontology.json",
        "liquidity_state.json",
        "macro_regime.json",
        "risk_state.json",
        "structural_shift.json",
        "market_prediction_benchmark.json",
        "../contradictions/contradiction_state.json",
        "../theme/top_early_theme.json",
        "../story/today_story.json",
        "../story/impact_mentionables.json",
        "../content/today_video_script.json",
        "../topic/top_topic.json"
    ]

    print(f"\n[PUBLISH] Publishing Ops Assets from {DATA_OPS} to {dest_dir}...")
    for filename in files_to_publish:
        # Handle relative paths for memory/decision/ontology
        if filename.startswith("../"):
            source_dir = DATA_OPS.parent
            src = (source_dir / filename.replace("../", "")).resolve()
            target_name = src.name
            
            if "memory" in filename:
                target_dir = ROOT / "docs" / "data" / "memory"
            elif "ontology" in filename:
                target_dir = ROOT / "docs" / "data" / "ontology"
            else:
                target_dir = dest_dir # default to ops if not specified
            
            target_dir.mkdir(parents=True, exist_ok=True)
            dest = target_dir / target_name
        else:
            src = DATA_OPS / filename
            dest = dest_dir / filename

        if src.exists():
            shutil.copy2(src, dest)
            # Sync to legacy mirror only if not memory/ontology
            if "memory" not in filename and "ontology" not in filename:
                DATA_OUTPUTS_OPS.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, DATA_OUTPUTS_OPS / (src.name))
            print(f"✅ [OK] {filename}")
        else:
            if filename.endswith(".json"):
                print(f"⚠️ [SKIP] {filename} (not found in {DATA_OPS})")

    print(f"[PUBLISH] Ops sync completed to docs/data/ops and data_outputs/ops (legacy mirror)")

if __name__ == "__main__":
    main()
