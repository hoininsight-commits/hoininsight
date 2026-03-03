"""
[IS-100] Publish UI Decision Assets — Pipeline Source of Truth
=============================================================
This module is called by full_pipeline.yml AFTER `rm -rf docs/data` and BEFORE git push.
It is the SOLE authority for generating:
  - docs/data/decision/today.json
  - docs/data/decision/editorial/editorial_selection_*.json
  - docs/data/decision/manifest.json

DO NOT include daily_snapshot.json, ops, or market data in manifest.
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
        f = ROOT / "data" / "ops" / "topic_speakability_today.json"
        if f.exists():
            data = json.loads(f.read_text(encoding="utf-8"))
            for v in data.get("verdicts", []):
                if v.get("speakability") == "SPEAKABLE_NOW": approved_titles.add(v.get("title", ""))
    except Exception as e: print(f"[PUBLISH] warn loading topic_speakability_today: {e}")
    try:
        f2 = ROOT / "data" / "ops" / "auto_approved_today.json"
        if f2.exists():
            data2 = json.loads(f2.read_text(encoding="utf-8"))
            for a in data2.get("auto_approved", []): approved_titles.add(a.get("title", ""))
    except Exception as e: print(f"[PUBLISH] warn loading auto_approved_today: {e}")
    return approved_titles

def _load_narrative_data() -> Dict[str, Dict]:
    narrative_map = {}
    try:
        f = ROOT / "data" / "ops" / "narrative_intelligence_v2.json"
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
    kst_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    ymd = kst_date.replace("-", "/")
    dated_card = DATA_DECISION / ymd / "final_decision_card.json"
    source = dated_card if dated_card.exists() else (DOCS_TODAY if DOCS_TODAY.exists() else None)
    if source is None: return None
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
            title, topic_id = top.get("title", ""), top.get("topic_id", "")
            if title in approved_titles: top["status"], top["speakability"], changed = "APPROVED", "OK", True
            dataset_id = top.get("dataset_id")
            n_key = dataset_id if dataset_id in narrative_map else next((k for k in narrative_map.keys() if dataset_id == k or (isinstance(k, str) and dataset_id in k)), None)
            if not n_key and title in narrative_map: n_key = title
            if n_key:
                n_data = narrative_map[n_key]
                for k in ["narrative_score", "video_ready", "actor_tier_score", "escalation_flag", "conflict_flag", "cross_axis_multiplier"]: top[k] = n_data.get(k)
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
        if changed:
            if isinstance(data, dict) and "top_topics" in data and len(data["top_topics"]) > 0:
                t0 = data["top_topics"][0]
                if t0.get("conflict_flag"):
                    data["anchor_topic"] = "[CONFLICT] MULTI-AXIS FRICTION"
                    for k in ["topic", "structural_topic"]: data[k] = t0.get("title", data.get(k))
                    data["decision_rationale"] = t0.get("rationale", data.get("decision_rationale"))
            dest.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as e: print(f"[PUBLISH] error in _publish_today: {e}"); file_date = kst_date
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
    
    # 1. Candidate Pool
    src_pool = ROOT / "data_outputs" / "ops" / "video_candidate_pool.json"
    if src_pool.exists():
        shutil.copy2(src_pool, dest_dir / "video_candidate_pool.json")
        print(f"[PUBLISH] video_candidate_pool.json → {dest_dir}")

    # 2. [PHASE-22A] Script Pack (Mandatory check)
    src_json = ROOT / "data_outputs" / "ops" / "video_script_pack.json"
    src_md = ROOT / "data_outputs" / "ops" / "video_script_pack.md"
    
    if src_json.exists():
        shutil.copy2(src_json, dest_dir / "video_script_pack.json")
        print(f"[PUBLISH] video_script_pack.json → {dest_dir}")
    else:
        print(f"❌ [PUBLISH] CRITICAL MISSING: {src_json}")
        # Note: In CI this should fail the build if Phase 22A is strictly enforced.

    # 3. [PHASE-22B] Stock Linkage Pack
    src_linkage = ROOT / "data_outputs" / "ops" / "stock_linkage_pack.json"
    if src_linkage.exists():
        shutil.copy2(src_linkage, dest_dir / "stock_linkage_pack.json")
        print(f"[PUBLISH] stock_linkage_pack.json → {dest_dir}")

    # 4. [PHASE-22C] Conflict Density Pack
    src_density = ROOT / "data_outputs" / "ops" / "conflict_density_pack.json"
    if src_density.exists():
        shutil.copy2(src_density, dest_dir / "conflict_density_pack.json")
        print(f"[PUBLISH] conflict_density_pack.json → {dest_dir}")

    # 5. [PHASE-23] Structural Regime Layer
    src_regime = ROOT / "data_outputs" / "ops" / "regime_state.json"
    if src_regime.exists():
        shutil.copy2(src_regime, dest_dir / "regime_state.json")
        print(f"[PUBLISH] regime_state.json → {dest_dir}")

    # 6. [PHASE-24] Investment OS Layer
    src_os_json = ROOT / "data_outputs" / "ops" / "investment_os_state.json"
    src_os_md = ROOT / "data_outputs" / "ops" / "investment_os_brief.md"
    if src_os_json.exists():
        shutil.copy2(src_os_json, dest_dir / "investment_os_state.json")
        print(f"[PUBLISH] investment_os_state.json → {dest_dir}")
    if src_os_md.exists():
        shutil.copy2(src_os_md, dest_dir / "investment_os_brief.md")
        print(f"[PUBLISH] investment_os_brief.md → {dest_dir}")

if __name__ == "__main__":
    main()
