import shutil
import json
from pathlib import Path
from src.topics.topic_gate.run_script_quality_gate import run as run_gate

def test_runner_creates_sidecar(tmp_path):
    # Setup
    script_file = tmp_path / "test_script.md"
    script_file.write_text("""# Script
### 1) 훅 (모순점)
- Valid Hook

### 4) 괴리 (미스매치 원인)
- Valid Divergence

### 5) 본질적 증거 비교 (수치)
- **A**: 1
- **B**: 2

### 6) 추후 관찰 지표
- Watch 1
- Watch 2
""", encoding="utf-8")
    
    # Execute
    result = run_gate(script_file, "test_topic")
    
    # Verify Return
    assert result["quality_status"] == "READY"
    
    # Verify Sidecar File
    sidecar = tmp_path / "test_script.md.quality.json"
    assert sidecar.exists()
    
    data = json.loads(sidecar.read_text(encoding="utf-8"))
    assert data["topic_id"] == "test_topic"
    assert data["quality_status"] == "READY"
    assert "failure_codes" in data
    assert "summary_reason" in data

def test_runner_handles_missing_file(tmp_path):
    missing_file = tmp_path / "non_existent.md"
    result = run_gate(missing_file, "topic_x")
    assert "error" in result
