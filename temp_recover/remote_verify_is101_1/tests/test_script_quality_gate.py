import pytest
from src.topics.topic_gate.script_quality_gate import ScriptQualityGate

@pytest.fixture
def gate():
    return ScriptQualityGate()

def test_gate_drop_invalid_hook(gate):
    # Hook contains placeholder
    script = """
### 1) 훅 (모순점)
- [데이터 부족/필요] Hook is missing.

### 4) 괴리 (미스매치 원인)
- Some reason.
"""
    result = gate.evaluate("test_topic_1", script)
    assert result["quality_status"] == "DROP"
    assert "FAIL_HOOK" in result["failure_codes"]

def test_gate_drop_no_evidence(gate):
    # Valid hook, but zero evidence
    script = """
### 1) 훅 (모순점)
- This is a valid hook.

### 4) 괴리 (미스매치 원인)
- Valid reason.

### 5) 본질적 증거 비교 (수치)
- [데이터 부족/필요]
"""
    result = gate.evaluate("test_topic_2", script)
    assert result["quality_status"] == "DROP"
    assert "NO_EVIDENCE" in result["failure_codes"]
    assert "INCONSISTENT" in result["failure_codes"] # Valid hook but no evidence implies inconsistency

def test_gate_hold_weak_evidence(gate):
    # Valid hook, 1 evidence point, valid watchlist
    script = """
### 1) 훅 (모순점)
- Valid hook.

### 4) 괴리 (미스매치 원인)
- Valid reason.

### 5) 본질적 증거 비교 (수치)
- **CPI**: 3.2% (Ref: FRED)

### 6) 추후 관찰 지표
- Point 1
- Point 2
"""
    result = gate.evaluate("test_topic_3", script)
    assert result["quality_status"] == "HOLD"
    assert "WEAK_EVIDENCE" in result["failure_codes"]

def test_gate_hold_weak_watch(gate):
    # Valid hook, 2 evidence points, but script generator default watchlist often has placeholders
    # or if we have only 1 valid item
    script = """
### 1) 훅 (모순점)
- Valid hook.

### 4) 괴리 (미스매치 원인)
- Valid reason.

### 5) 본질적 증거 비교 (수치)
- **CPI**: 3.2%
- **PCE**: 2.8%

### 6) 추후 관찰 지표
- Point 1
"""
    result = gate.evaluate("test_topic_4", script)
    assert result["quality_status"] == "HOLD"
    assert "NO_FORWARD_SIGNAL" in result["failure_codes"]

def test_gate_ready(gate):
    # All good
    script = """
### 1) 훅 (모순점)
- Valid hook text.

### 4) 괴리 (미스매치 원인)
- Valid divergence text.

### 5) 본질적 증거 비교 (수치)
- **Signal A**: 100
- **Signal B**: 200

### 6) 추후 관찰 지표
- Watch A
- Watch B
"""
    result = gate.evaluate("test_topic_5", script)
    assert result["quality_status"] == "READY"
    assert not result["failure_codes"]
