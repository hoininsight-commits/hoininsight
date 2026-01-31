from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

def _ymd() -> str:
    return datetime.now().strftime("%Y/%m/%d")

def _read_json(p: Path) -> Any:
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None

def _exists_rel(base_dir: Path, rel: str) -> str:
    p = base_dir / rel
    return rel if p.exists() else "-"

@dataclass
class RegimeCard:
    regime_line: str
    drivers_line: str
    meta_link: str
    structured_data: Dict[str, Any]  # For Phase 26 snapshot


def build_regime_card(
    base_dir: Path,
    enriched_topics: List[Dict[str, Any]],
) -> RegimeCard:
    ymd = _ymd()
    meta_rel = f"data/meta_topics/{ymd}/meta_topics.json"
    meta_path = base_dir / meta_rel
    meta_payload = _read_json(meta_path)

    # Structured Data Init
    s_data = {
        "regime": "None",
        "basis_type": "NONE",
        "basis_id": "",
        "confidence": 0.0,
        "supporting": [],
        "fallback": None
    }

    if isinstance(meta_payload, list) and len(meta_payload) > 0 and isinstance(meta_payload[0], dict):
        meta_sorted = sorted(
            [m for m in meta_payload if isinstance(m, dict) and isinstance(m.get("score", None), (int, float))],
            key=lambda x: float(x.get("score", 0.0)),
            reverse=True,
        )
        if len(meta_sorted) > 0:
            m = meta_sorted[0]
            evidence = m.get("evidence", [])
            s_data["regime"] = m.get('title', 'Unknown')
            s_data["basis_type"] = "META_TOPIC"
            s_data["basis_id"] = m.get("meta_topic_id", "")
            s_data["confidence"] = float(m.get("score", 0.0))
            s_data["supporting"] = evidence if isinstance(evidence, list) else []
            
            if isinstance(evidence, list):
                ev = ",".join([str(x) for x in evidence])
            else:
                ev = str(evidence)
            # Meta Topic becomes the definitive Regime
            regime_line = f"Regime: {m.get('title','')} (severity={m.get('severity')}, score={m.get('score')}) | evidence={ev}"
        else:
            regime_line = "Regime: (no meta regime detected)"
            s_data["regime"] = "(no meta regime detected)"
    else:
        regime_line = "Regime: (no meta regime detected)"
        s_data["regime"] = "(no meta regime detected)"
    
    # Fallback logic for s_data if needed (though per Phase 25 we prefer meta, 
    # if meta is missing we might want to record the top driver as 'regime' 
    # OR just keep it as 'no regime'. The prompt says "Phase 25에서 확정된 결과를 그대로 저장".
    # Since Phase 25 fallback logic was strictly display-based or implied, 
    # we will just record what we have.)

    # Drivers: top 2 by final_score_m
    drivers = sorted(
        [t for t in enriched_topics if isinstance(t.get('_final_score_m', None), (int, float))],
        key=lambda x: float(x.get("_final_score_m", 0.0)),
        reverse=True,
    )[:2]

    parts: List[str] = []
    for t in drivers:
        dataset_id = str(t.get("_dataset_id", ""))
        report_key = str(t.get("_report_key", ""))
        mom = str(t.get("_momentum", "FLAT"))
        slope = t.get("_momentum_slope", 0.0)
        chart_rel = _exists_rel(base_dir, f"data/reports/{ymd}/charts/{dataset_id}.png")
        if chart_rel != "-":
            parts.append(f"{report_key}:{mom}({slope:.2f})[png]({chart_rel})")
        else:
            parts.append(f"{report_key}:{mom}({slope:.2f})")
    if len(parts) == 0:
        drivers_line = "Drivers: (none)"
    else:
        drivers_line = "Drivers: " + " | ".join(parts)

    meta_link = meta_rel if meta_path.exists() else "-"
    return RegimeCard(regime_line=regime_line, drivers_line=drivers_line, meta_link=meta_link, structured_data=s_data)

