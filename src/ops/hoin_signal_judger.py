import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

class HoinSignalJudger:
    """
    Step 61-g: HOIN Signal - 구조적 이슈 선점 판단기 v1.0
    Parallel layer to identify structural 'Signal' topics using deterministic rules.
    """
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def run_judgement(self, ymd: str) -> List[Dict[str, Any]]:
        """
        Main execution loop for HOIN Signal judgement.
        """
        # 1. Load Inputs
        anchors = self._load_json(self.base_dir / "data" / "ops" / "fact_anchors_today.json")
        seeds = self._load_json(self.base_dir / "data" / "ops" / "topic_seeds_today.json", default=[])
        
        # Fallback if "today" files are missing but historical exist (for testing)
        if not anchors:
            alt_anchors = list(self.base_dir.glob(f"data/facts/fact_anchors_{ymd.replace('-', '')}.json"))
            if alt_anchors:
                anchors = self._load_json(alt_anchors[0])

        if not anchors and not seeds:
            print("[SignalJudger] No inputs found for judgement.")
            return []

        # 2. Identify Candidates
        signal_candidates = []
        
        # Process from Seeds first
        for seed in seeds:
            if self._is_signal(seed):
                signal_candidates.append(self._to_signal(seed, "SEED"))

        # Process from Anchors
        for anchor in anchors:
            if self._is_signal(anchor):
                signal_candidates.append(self._to_signal(anchor, "FACT"))

        # 3. Sector Compression (Step 61-g-2)
        final_signals = self._compress_sectors(signal_candidates)

        # 4. Save Output (Step 61-g-3)
        self._save_output(final_signals)
        
        return final_signals

    def _load_json(self, path: Path, default: Any = None) -> Any:
        if not path.exists():
            return default if default is not None else []
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except:
            return default if default is not None else []

    def _is_signal(self, item: Dict[str, Any]) -> bool:
        """
        Step 61-g-1: SIGNAL JUDGEMENT RULE
        4 questions, 3+ YES = SIGNAL.
        """
        # Flatten metadata
        flat_item = item.copy()
        if "metadata" in item and isinstance(item["metadata"], dict):
            flat_item.update(item["metadata"])
            
        yes_count = 0
        
        # Q1: 정책 / 자본 / 산업 구조 중 하나인가?
        type_tags = str(flat_item.get("type", "") + flat_item.get("category", "") + \
                        flat_item.get("lane", "") + flat_item.get("fact_type", "")).upper()
        structural_keywords = ["POLICY", "CAPITAL", "STRUCT", "SYSTEM", "GOV"]
        if any(kw in type_tags for kw in structural_keywords):
            yes_count += 1
        elif flat_item.get("lane") in ["POLICY", "STRUCTURAL", "CAPITAL"] or \
             flat_item.get("fact_type") in ["POLICY", "STRUCTURAL", "CAPITAL"]:
            yes_count += 1

        # Q2: 섹터 또는 밸류체인 전체를 건드리는가?
        is_wide = flat_item.get("is_wide", False) or \
                  "chain" in str(flat_item).lower() or \
                  "sector" in str(flat_item).lower()
        if is_wide:
            yes_count += 1

        # Q3: "지금 안 나오면 이상한가?" (Force-Timed)
        if flat_item.get("urgency") == "HIGH" or flat_item.get("why_now") or \
           flat_item.get("is_forced_timing", False) or "immediate" in str(flat_item).lower():
            yes_count += 1

        # Q4: 시장 참여자가 피할 수 없는 선택을 강요받는 구조인가?
        forced_keywords = ["MANDATORY", "REGULATION", "UNAVOIDABLE", "FORCE", "STANDARD", "MUST", "COMPLY"]
        if any(kw in str(flat_item).upper() for kw in forced_keywords):
            yes_count += 1
        
        return yes_count >= 3

    def _to_signal(self, item: Dict[str, Any], source_type: str) -> Dict[str, Any]:
        """
        Map to Signal Output Schema.
        """
        flat_item = item.copy()
        if "metadata" in item and isinstance(item["metadata"], dict):
            flat_item.update(item["metadata"])

        # Determine Signal Type
        stype = "STRUCTURAL"
        type_str = str(flat_item.get("type", "") + flat_item.get("lane", "") + flat_item.get("fact_type", "")).upper()
        if "POLICY" in type_str: stype = "POLICY"
        elif "CAPITAL" in type_str: stype = "CAPITAL"
        
        return {
            "signal_id": f"signal_{flat_item.get('topic_id', flat_item.get('fact_id', 'unknown'))}",
            "signal_title_kr": flat_item.get("title_kr") or flat_item.get("title") or flat_item.get("fact_text", "Untitled Signal"),
            "signal_type": stype,
            "core_fact": flat_item.get("core_fact") or [flat_item.get("fact_text")] if flat_item.get("fact_text") else [],
            "why_now": [flat_item.get("why_now_hint", "Structural Timing Rule Matched")],
            "compressed_sector": flat_item.get("sector") or flat_item.get("impact_area", "GENERIC"),
            "representative_logic": flat_item.get("structural_reason") or "Deterministic Choice imposed by structure.",
            "confidence": "HIGH" if flat_item.get("confidence") == "HIGH" else "MEDIUM",
            "frame": flat_item.get("frame", "UNKNOWN")
        }

    def _compress_sectors(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Step 61-g-2: 섹터 압축 규칙
        """
        groups = {}
        for c in candidates:
            key = (c["frame"], c["signal_type"], c["compressed_sector"])
            if key not in groups:
                groups[key] = c
            else:
                if c["confidence"] == "HIGH" and groups[key]["confidence"] != "HIGH":
                    groups[key] = c
                elif len(c["signal_title_kr"]) > len(groups[key]["signal_title_kr"]):
                    groups[key] = c
        return list(groups.values())

    def _save_output(self, signals: List[Dict[str, Any]]):
        out_path = self.base_dir / "data" / "ops" / "hoin_signal_today.json"
        payload = {
            "run_ts": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "signals": signals
        }
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[SignalJudger] Saved {len(signals)} signals to {out_path}")

if __name__ == "__main__":
    from pathlib import Path
    judger = HoinSignalJudger(Path("."))
    judger.run_judgement(datetime.utcnow().strftime("%Y-%m-%d"))
