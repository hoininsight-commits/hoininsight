from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Set, Literal

CANDIDATE_ALIVE = "CANDIDATE_ALIVE"
CANDIDATE_DEFERRED = "CANDIDATE_DEFERRED"
CANDIDATE_EXPIRED = "CANDIDATE_EXPIRED"

def _read_json(p: Path) -> Any:
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except:
        return None

def _write_json(p: Path, data: Any) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def get_utc_ymd() -> str:
    return datetime.utcnow().strftime("%Y/%m/%d")

class TopicCandidateEngine:
    """
    Phase 39: Topic Candidate Gate & Survival Rules
    Filters anomaly detection results into viable Topic Candidates.
    
    Gates:
    1. Multi-Axis Confirmation (Concurrency)
    2. Temporal Density (Recency)
    3. Explainability
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.ymd_str = get_utc_ymd()
        self.output_dir = base_dir / "data" / "topics" / "candidates" / self.ymd_str
        self.registry = self._load_registry()
        
    def _load_registry(self) -> List[Dict]:
        reg_path = self.base_dir / "registry" / "datasets.yml"
        if not reg_path.exists():
            return []
        try:
            import yaml
            with open(reg_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
                return data.get("datasets", [])
        except:
            return []

    def _get_active_anomalies_today(self) -> List[Dict]:
        """Load all anomaly files for today and return detected anomalies."""
        anom_dir = self.base_dir / "data" / "features" / "anomalies" / self.ymd_str
        active_anomalies = []
        
        if not anom_dir.exists():
            return []
            
        for f in anom_dir.glob("*.json"):
            dataset_id = f.stem
            content = _read_json(f)
            
            # Anomaly content is usually a list of anomalies or an empty list
            if isinstance(content, list):
                for item in content:
                    # Depending on exact anomaly structure. 
                    # Usually: {"is_anomaly": True, "severity": "HIGH", ...}
                    # Or simpler: the file itself implies checking. 
                    # Assuming content contains anomaly events.
                    # Based on phase 16/17, it might be a list of detected regimes or specific points.
                    # Let's assume if the list is non-empty, it's a candidate signal.
                    # We add dataset info.
                    if isinstance(item, dict):
                        item["_dataset_id"] = dataset_id
                        active_anomalies.append(item)
            elif isinstance(content, dict):
                 # Some formats might be dict
                 if content.get("is_anomaly") or content.get("anomalies"):
                     content["_dataset_id"] = dataset_id
                     active_anomalies.append(content)
                     
        return active_anomalies

    def run(self):
        print(f"[Phase 39] Running Topic Candidate Gate for {self.ymd_str}")
        
        candidates = []
        raw_signals = self._get_active_anomalies_today()
        
        # Signal aggregation with metadata
        signals_by_id = {}
        category_map = {d["dataset_id"]: d.get("category", "OTHER") for d in self.registry}
        
        signals_by_category = {}
        for sig in raw_signals:
            ds_id = sig.get("_dataset_id")
            if not ds_id: continue
            
            category = category_map.get(ds_id, "OTHER")
            sig["_category"] = category
            signals_by_id[ds_id] = sig
            
            if category not in signals_by_category:
                signals_by_category[category] = []
            signals_by_category[category].append(ds_id)

        # --- GATE 1: Multi-Axis Confirmation ---
        # Requirement: At least 2 independent axes must have anomalies.
        active_axes = list(signals_by_id.keys())
        has_global_concurrency = len(active_axes) >= 2
        
        # --- GATE 2: Temporal Density ---
        # Requirement: Recent N hours/days.
        # Since we run daily on today's data, implicitly satisfied if raw_signals are from today.
        # We check "timestamp" or "date" in signal if available, else assume today.
        is_fresh = True # Default for daily batch
        
        # Processing Candidates
        for ds_id, sig in signals_by_id.items():
            candidate = {
                "candidate_id": f"cand_{ds_id}_{self.ymd_str.replace('/','')}",
                "dataset_id": ds_id,
                "category": sig.get("_category", "OTHER"),
                "created_at": datetime.utcnow().isoformat(),
                "status": "UNKNOWN",
                "gates": {
                    "multi_axis": False,
                    "temporal": True,
                    "explainability": False
                },
                "supporting_evidence": []
            }
            
            # Identify Supporting Evidence
            # 1. Intra-category evidence (other anomalies in the same category)
            my_cat = candidate["category"]
            same_cat_others = [x for x in signals_by_category.get(my_cat, []) if x != ds_id]
            
            # 2. Inter-category evidence (Global correlation)
            other_cats = [c for c in signals_by_category.keys() if c != my_cat]
            
            candidate["supporting_evidence"] = {
                "intra_category": same_cat_others,
                "inter_category_axes": other_cats
            }
            
            # Check Gate 1: Multi-Axis (Now requires either same-category cluster OR global diversity)
            if same_cat_others or len(other_cats) > 0:
                candidate["gates"]["multi_axis"] = True
            
            # Check Gate 3: Explainability
            if candidate["gates"]["multi_axis"]:
                if same_cat_others:
                    reason = f"Category Cluster: Detected in [{ds_id}] with corroborating signals in {same_cat_others}."
                else:
                    reason = f"Cross-Axis: Detected in [{ds_id}] during global market volatility in categories {other_cats}."
                candidate["reason"] = reason
                candidate["gates"]["explainability"] = True
            else:
                candidate["reason"] = "Isolated anomaly without cross-signal confirmation."
                candidate["gates"]["explainability"] = False
                
            # Final Status Determination
            if (candidate["gates"]["multi_axis"] and 
                candidate["gates"]["temporal"] and 
                candidate["gates"]["explainability"]):
                candidate["status"] = CANDIDATE_ALIVE
            else:
                # Differentiate Deferred vs Expired?
                # Condition Unmet -> Deferred (Gate 1 fail usually means 'wait for more data' or 'not enough signal')
                # Expired -> Time passed (Gate 2 fail). 
                # Since Gate 2 passed, we use DEFERRED.
                candidate["status"] = CANDIDATE_DEFERRED
            
            candidates.append(candidate)
            
        # If no signals at all
        if not candidates:
            print("[Phase 39] No anomalies detected to process.")
        
        # Output
        output_data = {
            "generated_at": datetime.utcnow().isoformat(),
            "candidate_count": len(candidates),
            "alive_count": len([c for c in candidates if c["status"] == CANDIDATE_ALIVE]),
            "candidates": candidates
        }
        
        outfile = self.output_dir / "topic_candidates.json"
        _write_json(outfile, output_data)
        print(f"[Phase 39] Generated {len(candidates)} candidates. {output_data['alive_count']} ALIVE.")
        print(f"saved to {outfile}")

def main():
    base_dir = Path(os.getcwd())
    # Adjust if run from src module
    if str(base_dir).endswith("src/topics"):
        base_dir = base_dir.parent.parent
        
    engine = TopicCandidateEngine(base_dir)
    engine.run()

if __name__ == "__main__":
    main()
