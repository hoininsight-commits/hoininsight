from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

def _ymd() -> str:
    return datetime.now().strftime("%Y/%m/%d")

def _read_json(p: Path) -> Any:
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None

def collect_topics_today(base_dir: Path) -> List[Dict[str, Any]]:
    ymd = _ymd()
    root = base_dir / "data" / "topics" / ymd
    out: List[Dict[str, Any]] = []
    if not root.exists():
        return out
    for p in root.glob("*.json"):
        payload = _read_json(p)
        if isinstance(payload, list):
            for t in payload:
                if isinstance(t, dict):
                    t["_dataset_id"] = p.stem
                    out.append(t)
    return out

def fuse_meta_topics(base_dir: Path) -> List[Dict[str, Any]]:
    topics = collect_topics_today(base_dir)

    def has(ds: str, sev_min: str) -> List[Dict[str, Any]]:
        order = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
        return [
            t for t in topics
            if t.get("_dataset_id") == ds and order.get(str(t.get("severity","")),0) >= order.get(sev_min,0)
        ]

    meta: List[Dict[str, Any]] = []

    # Rule 1: Risk-Off Regime
    vix = has("risk_vix_index_stooq", "HIGH")
    btc = has("crypto_btc_usd_spot_coingecko", "MEDIUM")
    spx = has("index_spx_sp500_stooq", "MEDIUM")
    if vix and (btc or spx):
        used = vix + btc + spx
        score = sum(float(t.get("_final_score", t.get("score",0))) for t in used) / max(len(used),1)
        meta.append({
            "meta_topic_id": "risk_off_regime",
            "title": "Risk-Off Regime 강화",
            "severity": "HIGH",
            "score": score,
            "evidence": sorted(list({t.get("_dataset_id") for t in used})),
            "generated_at": datetime.now().isoformat()
        })

    # Rule 2: Rate & FX Shock
    us10y = has("rates_us10y_yield_ustreasury", "MEDIUM")
    usdkrw = has("fx_usdkrw_spot_open_er_api", "MEDIUM")
    if us10y and usdkrw:
        used = us10y + usdkrw
        score = sum(float(t.get("_final_score", t.get("score",0))) for t in used) / max(len(used),1)
        meta.append({
            "meta_topic_id": "rate_fx_shock",
            "title": "금리·환율 동시 충격",
            "severity": "MEDIUM",
            "score": score,
            "evidence": sorted(list({t.get("_dataset_id") for t in used})),
            "generated_at": datetime.now().isoformat()
        })

    return meta

def write_meta_topics(base_dir: Path) -> Path:
    ymd = _ymd()
    out_dir = base_dir / "data" / "meta_topics" / ymd
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "meta_topics.json"
    payload = fuse_meta_topics(base_dir)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out
