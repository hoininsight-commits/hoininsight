import json
from pathlib import Path
from typing import Dict
from src.topics.topic_gate.script_quality_gate import ScriptQualityGate

def run(script_path: Path, topic_id: str) -> Dict:
    """
    Runner for Script Quality Gate.
    Reads the script, runs evaluation, and saves the sidecar JSON.
    """
    if not script_path.exists():
        return {"error": f"Script file not found: {script_path}"}
        
    script_text = script_path.read_text(encoding="utf-8")
    
    gate = ScriptQualityGate()
    result = gate.evaluate(topic_id, script_text)
    
    # Save Sidecar
    sidecar_path = script_path.parent / (script_path.name + ".quality.json")
    sidecar_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    
    return result
