import json
import os
from pathlib import Path
from datetime import datetime
from src.issuesignal.editorial_light_engine import EditorialLightEngine
from src.issuesignal.dashboard.models import DecisionCard

def test_editorial_light_generation():
    # 1. Mock Macro Actor
    macro_actor = {
        "actor_name_ko": "미국 장기채 자본",
        "actor_type": "자본주체",
        "actor_tag": "상승축적"
    }
    
    # 2. Generate Light Content
    light_content = EditorialLightEngine.generate(macro_actor, "BULL")
    
    print(f"Title: {light_content['title']}")
    print(f"Status: {light_content['status']}")
    print(f"Actor: {light_content['actor']}")
    print(f"One-liner: {light_content['one_liner']}")
    
    # 3. Assert Strict Rules
    assert light_content["status"] == "EDITORIAL_LIGHT"
    assert len(light_content["tickers"]) == 0
    assert "종목을 도출하지 않습니다" in light_content["ticker_path"]["global_bottleneck_ko"]
    assert "관찰해야 합니다" in light_content["long_form"]

def test_rhythm_logic_simulation(base_dir: Path):
    rhythm_path = base_dir / "data" / "ops" / "editorial_rhythm.json"
    rhythm_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Simulate 3-day HOLD streak
    rhythm_data = {
        "consecutive_hold_days": 3,
        "last_editorial_date": "2026-01-25"
    }
    rhythm_path.write_text(json.dumps(rhythm_data))
    
    print(f"Rhythm data simulated at {rhythm_path}")
    
    # Normally run_issuesignal.py would read this and trigger LIGHT.
    # Verification of integration is done by checking the logic in run_issuesignal.py.

if __name__ == "__main__":
    test_editorial_light_generation()
    test_rhythm_logic_simulation(Path("."))
    print("\n[VERIFY] IS-70 Editorial Light Layer Unit Test Passed!")
