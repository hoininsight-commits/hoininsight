import pytest
from pathlib import Path
from src.ops.structural_narrative_mapper import StructuralNarrativeMapper

def test_structural_mapping_policy(tmp_path):
    mapper = StructuralNarrativeMapper(tmp_path)
    fact = {
        "fact_type": "POLICY",
        "fact_text": "New regulation on carbon taxes in Germany",
        "entities": ["Carbon", "Germany"]
    }
    frames = mapper.map_fact(fact)
    
    # POLICY_SHIFT should be triggered
    assert any(f["frame"] == "POLICY_SHIFT" for f in frames)
    # STRATEGIC_DEPENDENCY might not be triggered unless 'energy' or 'defense' are mentioned, 
    # but carbon tax is energy-adjacent. My rules are simple for now.
    
def test_structural_mapping_tech(tmp_path):
    mapper = StructuralNarrativeMapper(tmp_path)
    fact = {
        "fact_type": "TECH",
        "fact_text": "Breakthrough in solid-state battery architecture",
        "entities": ["Battery", "Architecture"]
    }
    frames = mapper.map_fact(fact)
    
    assert any(f["frame"] == "TECH_INFLECTION" for f in frames)

def test_structural_mapping_capital(tmp_path):
    mapper = StructuralNarrativeMapper(tmp_path)
    fact = {
        "fact_type": "BUDGET",
        "fact_text": "US government allocates $100B for semiconductor investment",
        "entities": ["Semiconductor", "US"]
    }
    frames = mapper.map_fact(fact)
    
    assert any(f["frame"] == "CAPITAL_REALLOCATION" for f in frames)

def test_enrich_facts(tmp_path):
    mapper = StructuralNarrativeMapper(tmp_path)
    facts = [
        {
            "fact_type": "TECH",
            "fact_text": "New material for superconductors",
            "entities": ["Superconductor"]
        }
    ]
    enriched = mapper.enrich_facts(facts)
    assert "structural_frames" in enriched[0]
    assert len(enriched[0]["structural_frames"]) > 0
