from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class TopicSynthesizer:
    def __init__(self, base_dir: Path, date_str: Optional[str] = None):
        self.base_dir = base_dir
        self.ymd = date_str if date_str else datetime.now().strftime("%Y-%m-%d")
        self.output_dir = self.base_dir / "data" / "topics" / "synthesized" / self.ymd.replace("-", "/")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _load_json(self, path: Path) -> Optional[Dict]:
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except Exception as e:
            logger.error(f"Failed to load {path}: {e}")
            return None

    def run(self) -> Dict[str, Any]:
        """
        Merge Structural Decison Card & Event Topic Gate
        """
        # Paths
        ymd_slash = self.ymd.replace("-", "/")
        gate_path = self.base_dir / "data" / "topics" / "gate" / ymd_slash / "topic_gate_output.json"
        structural_path = self.base_dir / "data" / "decision" / ymd_slash / "final_decision_card.json"

        # Load Inputs
        gate_data = self._load_json(gate_path)
        struct_data = self._load_json(structural_path)

        if not gate_data and not struct_data:
            logger.warning("No input data found for synthesis.")
            return {}

        # 1. Base Synthesis Structure
        synthesized_topic = {
            "meta": {
                "generated_at": datetime.now().isoformat(),
                "base_date": self.ymd,
                "version": "v1"
            },
            "content_topic": {
                "title": "Unknown Topic",
                "status": "WATCH",
                "reason": "Insufficient Data"
            }
        }

        # 2. Extract Event Side (Primary Context)
        event_ctx = {}
        if gate_data:
            event_ctx = {
                "title": gate_data.get("title"),
                "question": gate_data.get("question"),
                "why_confused": gate_data.get("why_people_confused"),
                "eligible": gate_data.get("speak_eligibility", {}).get("eligible", False)
            }
        
        # 3. Extract Structural Side (Evidence)
        struct_ctx = {}
        structural_evidence = []
        if struct_data:
            # Flatten top_topics
            top_topics = struct_data.get("top_topics", [])
            for t in top_topics:
                structural_evidence.append({
                    "dataset_id": t.get("dataset_id"),
                    "title": t.get("title"),
                    "level": t.get("level"),
                    "score": t.get("score"),
                    "rationale": t.get("rationale")
                })
            struct_ctx["evidence_count"] = len(structural_evidence)
            struct_ctx["primary_rationale"] = struct_data.get("structural_rationale")

        # 4. Synthesis Logic
        # Priority: Event Title (Human readable) > Structural Title
        final_title = event_ctx.get("title")
        if not final_title:
            # Fallback to first structural topic title if available
            if structural_evidence:
                final_title = structural_evidence[0].get("title", "Structural Anomaly Detected")
            else:
                final_title = "No Significant Topic"

        # Why Now Construction
        why_now = []
        if event_ctx.get("question"):
            why_now.append(f"Q: {event_ctx['question']}")
        if struct_ctx.get("primary_rationale"):
            why_now.append(f"Data: {struct_ctx['primary_rationale']}")
        
        # Status Determination
        # READY if: Event Eligible OR (Structural Evidence >= 3 AND High Confidence)
        # For this MVP, we strictly follow the Rule: Event Eligible OR Anchor Exists
        # note: structural_evidence usually implies anchor existence in this pipeline
        
        status = "WATCH"
        status_reason = []

        if event_ctx.get("eligible"):
            status = "READY"
            status_reason.append("Event-Gate Passed")
        
        # Check structural weight
        if len(structural_evidence) >= 3:
            status = "READY" # Strong structural signal overrides gate
            status_reason.append(f"Strong Structural Evidence ({len(structural_evidence)} signals)")
        else:
            status_reason.append(f"Weak Structural Evidence ({len(structural_evidence)} signals)")

        if not event_ctx and not struct_ctx:
            status = "NO_DATA"
            status_reason = ["No input tensors"]

        # Final Assembly
        content_topic = {
            "title": final_title,
            "status": status,
            "why_now": " ".join(why_now),
            "status_reason": ", ".join(status_reason),
            "components": {
                "event": event_ctx,
                "structural": structural_evidence
            }
        }
        synthesized_topic["content_topic"] = content_topic

        # Save
        out_file = self.output_dir / "synth_topic_v1.json"
        out_file.write_text(json.dumps(synthesized_topic, indent=2, ensure_ascii=False), encoding='utf-8')
        logger.info(f"Synthesized topic saved to {out_file}")

        return synthesized_topic

if __name__ == "__main__":
    # Test Run
    base_dir = Path(__file__).resolve().parent.parent.parent
    synth = TopicSynthesizer(base_dir)
    res = synth.run()
    print(json.dumps(res, indent=2, ensure_ascii=False))
