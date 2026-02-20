"""
Verify IS-95-x Labor Shift Collectors
"""
import sys
import pytest
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.collectors.labor_market_us_collector import LaborMarketUSCollector
from src.collectors.education_training_us_collector import EducationTrainingUSCollector
from src.collectors.datacenter_capex_pipeline_us_collector import DatacenterCapexPipelineUSCollector
from src.collectors.layoffs_white_collar_us_collector import LayoffsWhiteCollarUSCollector

def test_collectors_exist():
    assert LaborMarketUSCollector
    assert EducationTrainingUSCollector
    assert DatacenterCapexPipelineUSCollector
    assert LayoffsWhiteCollarUSCollector

def test_labor_market_structure():
    c = LaborMarketUSCollector(api_key="mock")
    assert hasattr(c, 'collect_all')
    assert 'LNS14027660' in c.SERIES_MAP  # Bachelors Unemp

def test_education_stub():
    c = EducationTrainingUSCollector()
    c.collect_all() # Should run without error (stub)
    output = Path(__file__).parent.parent / "data" / "collect" / "education_training_us" / "latest_snapshot.json"
    assert output.exists()

if __name__ == "__main__":
    # Minimal manual run
    try:
        test_collectors_exist()
        test_labor_market_structure()
        test_education_stub()
        print("IS-95-x Collectors Verification: PASSED")
    except Exception as e:
        print(f"IS-95-x Collectors Verification: FAILED - {e}")
        sys.exit(1)
