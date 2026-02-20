import json
import shutil
import pytest
from pathlib import Path
from src.ops.fact_first_input_loader import load_fact_first_input

@pytest.fixture
def temp_workspace(tmp_path):
    # Setup mock structure
    (tmp_path / "data" / "facts" / "fact_first").mkdir(parents=True)
    (tmp_path / "data" / "ops").mkdir(parents=True)
    return tmp_path

def test_missing_file_returns_errors(temp_workspace):
    """Test 1: Missing file => outputs with errors[] and count=0"""
    result = load_fact_first_input(temp_workspace, "2026-01-27")
    
    assert result["count"] == 0
    assert len(result["errors"]) == 1
    assert "not found" in result["errors"][0]["message"]
    
    # Check outputs written
    assert (temp_workspace / "data/ops/fact_first_input_today.json").exists()
    assert (temp_workspace / "data/ops/fact_first_input_today.md").exists()

def test_valid_file_and_dedup(temp_workspace):
    """Test 2: Valid file load & Dedup"""
    data = [
        {
            "fact_id": "F01", "type": "FLOW", "date": "2026-01-27", 
            "subject": "US Treasure", "object": "Liquidity", 
            "fact": "TGA balance increased.", "source": "Fed", "confidence": "HIGH"
        },
        # Duplicate of F01 logic
        {
            "fact_id": "F02", "type": "FLOW", "date": "2026-01-27", 
            "subject": "US Treasure", "object": "Liquidity", 
            "fact": "TGA balance increased.", "source": "Fed", "confidence": "HIGH"
        },
        # Distinct
        {
            "fact_id": "F03", "type": "POLICY", "date": "2026-01-27", 
            "subject": "BOK", "object": "Rate", 
            "fact": "Cut 25bps.", "source": "BOK", "confidence": "MEDIUM"
        }
    ]
    
    input_file = temp_workspace / "data/facts/fact_first/2026-01-27.json"
    input_file.write_text(json.dumps(data), encoding="utf-8")
    
    result = load_fact_first_input(temp_workspace, "2026-01-27")
    
    assert result["count"] == 2 # F01 and F03 (F02 deduped)
    assert result["counts_by_type"]["FLOW"] == 1
    assert result["counts_by_type"]["POLICY"] == 1
    assert len(result["errors"]) == 0
    assert result["facts"][0]["fact_id"] == "F01"

def test_invalid_enum_handling(temp_workspace):
    """Test 3: Invalid enum => errors populated, valid rows pass"""
    data = [
        # Invalid Type
        {
            "fact_id": "F01", "type": "UNKNOWN_TYPE", "date": "2026-01-27", 
            "subject": "S", "object": "O", "fact": "F", "source": "Src", "confidence": "HIGH"
        },
        # Valid
        {
            "fact_id": "F02", "type": "STRUCTURE", "date": "2026-01-27", 
            "subject": "S", "object": "O", "fact": "F2", "source": "Src", "confidence": "HIGH"
        }
    ]
    
    input_file = temp_workspace / "data/facts/fact_first/2026-01-27.json"
    input_file.write_text(json.dumps(data), encoding="utf-8")
    
    result = load_fact_first_input(temp_workspace, "2026-01-27")
    
    assert result["count"] == 1
    assert len(result["errors"]) == 1
    assert "Invalid type" in result["errors"][0]["message"]
