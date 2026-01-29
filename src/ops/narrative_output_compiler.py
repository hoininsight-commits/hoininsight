from typing import List, Dict, Any, Optional
from pathlib import Path
import yaml
import json
from datetime import datetime

class NarrativeOutputCompiler:
    """
    STEP 56 — NARRATIVE OUTPUT COMPILER
    Compiles everything into the final Economic Hunter Card (YAML).
    """
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        
    def compile_card(self, topic: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Final assembly of the EH Card.
        """
        sync_data = context.get("sync_data", {})
        
        card = {
            "version": "1.0",
            "topic_id": topic.get("topic_id", f"EH-{datetime.utcnow().strftime('%Y%j')}-{abs(hash(topic.get('title', ''))) % 1000:03d}"),
            "title": topic.get("title", "Untitled Structural Analysis"),
            "summary": topic.get("engine_conclusion", topic.get("summary", "No summary available.")),
            "generated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            
            # Step 52
            "targets": context.get("selected_tickers", []),
            
            # Step 53
            "trace": [s["content"] for s in context.get("reasoning_trace", [])],
            
            # Step 54
            "anchors": [f"{a['source']}: {a['key_value']}" for a in context.get("evidence_anchors", [])],
            
            # Step 55 & Metadata
            "meta": {
                "confidence": sync_data.get("final_confidence_score", 0),
                "status": "READY" if sync_data.get("status") == "PASSED" else "SHADOW",
                "risk_check": sync_data.get("risk_check", "UNKNOWN"),
                "narrative_format": topic.get("narrative_format", "ECONOMIC_HUNTER_VIDEO")
            }
        }
        
        return card

    def save_card(self, card: Dict[str, Any], ymd_path: str) -> Path:
        out_dir = self.base_dir / "data" / "reports" / ymd_path
        out_dir.mkdir(parents=True, exist_ok=True)
        
        yaml_path = out_dir / "economic_hunter_card.yaml"
        # We use json for the internal web UI but yaml for the canonical constitution requirement
        with open(yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(card, f, allow_unicode=True, sort_keys=False)
            
        print(f"[Compiler] Final EH Card saved to {yaml_path}")
        return yaml_path
