from typing import Any, Dict, List, Optional
import json
from pathlib import Path

class TonePersonaLock:
    """
    IS-97-2: Tone & Persona Lock Layer
    Deterministically assigns persona, tone, and authority metadata.
    """

    def build(self, 
              topic_id: str, 
              speakability: Dict[str, Any], 
              content_map: Dict[str, Any], 
              unit: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Build a tone/persona lock for a specific topic.
        """
        flag = speakability.get("speakability_flag", "DROP")
        if flag == "DROP":
            return None

        content_mode = content_map.get("content_mode", "HOLD")
        metrics = unit.get("derived_metrics_snapshot", {})
        tags = unit.get("evidence_tags", [])
        pretext_score = metrics.get("pretext_score", 0.0)
        execution_gap = metrics.get("policy_execution_gap", 0.0)
        
        # 4-3. Persona Determination
        persona = "MARKET_OBSERVER" # Default
        if any(t in tags for t in ["KR_POLICY", "US_POLICY"]):
            persona = "POLICY_ANALYST"
        elif any(t in tags for t in ["FLOW_ROTATION", "GLOBAL_INDEX"]):
            persona = "ECONOMIC_HUNTER"
        elif any(t in tags for t in ["EARNINGS_VERIFY", "PRETEXT_VALIDATION"]):
            persona = "MARKET_OBSERVER"

        # 4-1 & 4-2. Tone Logic
        tone = "OBSERVATIONAL"
        if flag == "HOLD":
            tone = "OBSERVATIONAL"
        elif content_mode == "SHORT":
            tone = "ASSERTIVE"
        elif content_mode == "LONG":
            tone = "EXPLANATORY"
            
        # 4-4. Confidence & Risk Disclaimer
        confidence_level = "MEDIUM"
        risk_mode = "EXPLICIT"
        
        if flag == "HOLD":
            confidence_level = "LOW"
            risk_mode = "EXPLICIT"
        elif pretext_score >= 0.8 and execution_gap <= 0.3: # Using 0.3 as a threshold
            confidence_level = "HIGH"
            risk_mode = "IMPLICIT"
        elif execution_gap > 0.3:
            confidence_level = "MEDIUM"
            risk_mode = "EXPLICIT"

        # Authority Level
        authority = "MEDIUM"
        if content_mode in ["SHORT", "LONG"] and pretext_score >= 0.85:
            authority = "HIGH"

        lock_reasons = []
        if pretext_score >= 0.85: lock_reasons.append(f"PRETEXT_SCORE={pretext_score}")
        if "FLOW_ROTATION" in tags: lock_reasons.append("FLOW_ROTATION_CONFIRMED")
        if "EARNINGS_VERIFY" in tags: lock_reasons.append("EARNINGS_VALIDATED")

        return {
            "topic_id": topic_id,
            "persona": persona,
            "tone": tone,
            "stance": "DATA_VALIDATED" if confidence_level == "HIGH" else "STRUCTURAL",
            "authority_level": authority,
            "confidence_level": confidence_level,
            "emotion_level": "LOW",
            "risk_disclaimer_mode": risk_mode,
            "lock_reason": lock_reasons
        }

def run_tone_persona_lock(output_dir: str = "data/decision"):
    base = Path(output_dir)
    
    # Load inputs
    try:
        content_maps = json.loads((base / "content_speak_map.json").read_text())
        units = json.loads((base / "interpretation_units.json").read_text())
        decisions = json.loads((base / "speakability_decision.json").read_text())
    except Exception as e:
        print(f"[ERR] Failed to load input assets: {e}")
        return

    locker = TonePersonaLock()
    locks = []
    
    # Units is a list, others are dicts keyed by topic_id (mostly)
    # content_speak_map is a list of dicts from IS-97-1 implementation
    
    unit_map = {u["interpretation_id"]: u for u in units}
    
    for cm in content_maps:
        topic_id = cm["topic_id"]
        unit = unit_map.get(topic_id)
        decision = decisions.get(topic_id)
        
        if not unit or not decision:
            continue
            
        lock = locker.build(topic_id, decision, cm, unit)
        if lock:
            locks.append(lock)
            
    # Save output
    out_path = base / "tone_persona_lock.json"
    out_path.write_text(json.dumps(locks, ensure_ascii=False, indent=2))
    print(f"[OK] Saved Tone Persona Lock to {out_path}")
    return locks
