import json
from pathlib import Path

def load_ui_context(project_root: Path):
    """
    Loads necessary data for UI contract building.
    """
    data_dir = project_root / "data"
    
    context = {
        "ui": {},
        "decision": {},
        "citations": {}
    }
    
    # Load citations
    cit_path = data_dir / "decision" / "evidence_citations.json"
    if cit_path.exists():
        with open(cit_path, "r", encoding="utf-8") as f:
            context["citations"] = json.load(f)
            
    # Load interpretation units as base context
    unit_path = data_dir / "decision" / "interpretation_units.json"
    if unit_path.exists():
        with open(unit_path, "r", encoding="utf-8") as f:
            context["decision"]["units"] = json.load(f)
            
    return context
