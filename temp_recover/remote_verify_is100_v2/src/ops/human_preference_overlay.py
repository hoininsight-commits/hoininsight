from __future__ import annotations
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import Counter

class HumanPreferenceOverlay:
    """
    Step 57: Human Preference Signal Overlay.
    Surfaces historical patterns of what humans rated as 'STRONG' 
    and compares them to today's topics.
    """

    OVERLAY_ENUM = ["HUMAN_LIKELY_STRONG", "HUMAN_UNCERTAIN", "HUMAN_LIKELY_WEAK", "INSUFFICIENT_HISTORY"]

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.log_file = base_dir / "data" / "ops" / "topic_quality_log.jsonl"
        self.signature_file = base_dir / "data" / "ops" / "human_pref_signature_30d.json"
        self.overlay_file = base_dir / "data" / "ops" / "human_pref_overlay_today.json"

    def build_signature(self, lookback_days: int = 30) -> Dict[str, Any]:
        """
        Builds a 'STRONG' signature from the last N days of logs.
        """
        if not self.log_file.exists():
            signature = {"status": "INSUFFICIENT_HISTORY", "traits": {}}
            self._save_json(self.signature_file, signature)
            return signature

        # 1. Filter logs for 'STRONG' and within lookback
        cutoff = (datetime.now() - timedelta(days=lookback_days)).isoformat()
        strong_records = []
        total_count = 0
        
        with open(self.log_file, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip(): continue
                try:
                    record = json.loads(line)
                    total_count += 1
                    if record.get("verdict") == "STRONG" and record.get("timestamp", "") >= cutoff:
                        strong_records.append(record)
                except: continue

        # 2. Insufficient History Check
        if total_count < 20 or not strong_records:
            signature = {"status": "INSUFFICIENT_HISTORY", "traits": {}}
            self._save_json(self.signature_file, signature)
            return signature

        # 3. Aggregate traits
        traits = {
            "lane": Counter([r.get("lane") for r in strong_records]),
            "narration_level": Counter([r.get("narration_level") for r in strong_records]),
            "impact_tag": Counter([r.get("impact_tag") for r in strong_records if r.get("impact_tag")]),
            "evidence_count_bucket": Counter([self._bucket_evidence(r.get("evidence_count", 0)) for r in strong_records])
        }

        # Convert counters to top traits (proportions)
        sig_traits = {}
        for key, counter in traits.items():
            total = sum(counter.values())
            sig_traits[key] = {str(k): v / total for k, v in counter.items() if (v / total) >= 0.2}

        signature = {
            "status": "SUCCESS",
            "lookback_days": lookback_days,
            "sample_size": len(strong_records),
            "traits": sig_traits,
            "timestamp": datetime.now().isoformat()
        }
        
        self._save_json(self.signature_file, signature)
        return signature

    def evaluate_today(self, topic_view: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates today's topics against the STRONG signature.
        """
        signature = self._load_json(self.signature_file)
        if not signature or signature.get("status") == "INSUFFICIENT_HISTORY":
            results = {"run_date": topic_view.get("run_date"), "status": "INSUFFICIENT_HISTORY", "overlays": {}}
            self._save_json(self.overlay_file, results)
            return results

        overlays = {}
        sig_traits = signature.get("traits", {})

        # Process each topic in all sections
        for section in topic_view.get("sections", {}).values():
            for topic in section:
                tid = topic.get("topic_id")
                if not tid: continue
                
                # Compare attributes
                matched = []
                missing = []
                
                compare_map = {
                    "lane": topic.get("lane"),
                    "narration_level": topic.get("level"),
                    "impact_tag": topic.get("impact"),
                    "evidence_count_bucket": self._bucket_evidence(topic.get("evidence_count", 0))
                }

                for attr, val in compare_map.items():
                    attr_sig = sig_traits.get(attr, {})
                    if str(val) in attr_sig:
                        matched.append(f"{attr.upper()}:{val}")
                    else:
                        # Find most frequent trait for this attr in signature
                        if attr_sig:
                            top_trait = max(attr_sig.items(), key=lambda x: x[1])[0]
                            missing.append(f"{attr.upper()}:{top_trait}")

                # Heuristic Rule
                match_count = len(matched)
                if match_count >= 3:
                    bucket = "HUMAN_LIKELY_STRONG"
                elif match_count == 2:
                    bucket = "HUMAN_UNCERTAIN"
                else:
                    bucket = "HUMAN_LIKELY_WEAK"

                overlays[tid] = {
                    "topic_id": tid,
                    "overlay_bucket": bucket,
                    "matched_traits": matched,
                    "missing_traits": missing,
                    "match_count": match_count
                }

        results = {
            "run_date": topic_view.get("run_date"),
            "status": "SUCCESS",
            "overlays": overlays,
            "summary": {
                "HUMAN_LIKELY_STRONG": len([o for o in overlays.values() if o["overlay_bucket"] == "HUMAN_LIKELY_STRONG"]),
                "HUMAN_UNCERTAIN": len([o for o in overlays.values() if o["overlay_bucket"] == "HUMAN_UNCERTAIN"]),
                "HUMAN_LIKELY_WEAK": len([o for o in overlays.values() if o["overlay_bucket"] == "HUMAN_LIKELY_WEAK"]),
            },
            "top_strong_traits": self._get_top_traits(sig_traits)
        }
        
        self._save_json(self.overlay_file, results)
        return results

    def _bucket_evidence(self, count: int) -> str:
        if count == 0: return "0"
        if count <= 2: return "1-2"
        if count <= 5: return "3-5"
        return "6+"

    def _get_top_traits(self, sig_traits: Dict[str, Any]) -> List[str]:
        flat = []
        for attr, values in sig_traits.items():
            for val, prop in values.items():
                flat.append((f"{attr.upper()}:{val}", prop))
        flat.sort(key=lambda x: x[1], reverse=True)
        return [x[0] for x in flat[:5]]

    def _save_json(self, path: Path, data: Any):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def _load_json(self, path: Path) -> Optional[Dict]:
        if not path.exists(): return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except: return None
