
import unittest
import json
import shutil
from pathlib import Path
from datetime import datetime
import sys

# Ensure project root is in sys.path
root_path = Path(__file__).resolve().parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from src.ops.snapshot_to_dashboard_projector import SnapshotToDashboardProjector

class TestSnapshotProjector(unittest.TestCase):
    def setUp(self):
        self.base_dir = Path("test_step81_env")
        self.base_dir.mkdir(exist_ok=True)
        self.snapshots_dir = self.base_dir / "data" / "snapshots"
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
        self.dashboard_dir = self.base_dir / "data" / "dashboard"
        
        # Create Mock Snapshot
        self.today_str = datetime.now().strftime("%Y-%m-%d")
        self.mock_snapshot_path = self.snapshots_dir / f"{self.today_str}_top1_snapshot.md"
        
        content = f"""[ECONOMIC_HUNTER_TOP1_SNAPSHOT]
DATE: {self.today_str}
PIPELINE_VERSION: v1.5.0-Hunter

[1. WHY NOW — 시간 강제성]
- Trigger Type: Scheduled Catalyst
- Timestamp / Deadline: 2026-03-01
- 지금 행동하지 않으면 사라지는 것: Immediate entry opportunity before regulatory shift.

[2. WHO IS FORCED — 강제된 행위자]
- Actor: Global Banks
- 권한 / 결정권의 성격: High
- 시간 압박의 원인: Basel III Implementation

[3. WHAT IS BREAKING — 섹터가 아닌 ‘행위’]
- 깨지고 있는 것: Legacy Lending Models
- 연쇄적으로 막히는 흐름: SME Credit Lines
- 시장이 아직 숫자로 못 본 이유: Lagging Indicators

[4. MARKET BLIND SPOT]
- 아직 반영되지 않은 이유: Complexity
- 데이터 공백 / 시차: Q1 Reports pending

[5. MENTIONABLE ASSETS]
- Asset 1: XLF (Financial Sector ETF)
- Asset 2: JPM (JPMorgan Chase)
- Asset 3: N/A

[6. SYSTEM DECISION]
- ECONOMIC_HUNTER_LOCK: True
- VIDEO_INTENSITY: STRIKE
- RHYTHM_PROFILE: STRUCTURE_FLOW
"""
        self.mock_snapshot_path.write_text(content, encoding="utf-8")

    def tearDown(self):
        if self.base_dir.exists():
            shutil.rmtree(self.base_dir)

    def test_projector(self):
        print("\n=== Testing Snapshot -> Dashboard Projection ===")
        projector = SnapshotToDashboardProjector(self.base_dir)
        output_file = projector.project()
        
        # 1. Check Output Exists
        self.assertTrue(output_file.exists())
        self.assertEqual(output_file.name, "today.json")
        print("✅ Dashboard JSON Created")
        
        # 2. Check Content
        data = json.loads(output_file.read_text(encoding="utf-8"))
        
        self.assertEqual(data["date"], self.today_str)
        
        signal = data["top_signal"]
        self.assertEqual(signal["title"], "Legacy Lending Models")
        self.assertEqual(signal["trigger"], "Scheduled Catalyst")
        self.assertEqual(signal["intensity"], "STRIKE")
        self.assertEqual(signal["rhythm"], "STRUCTURE_FLOW")
        self.assertEqual(signal["status"], "LOCK")
        self.assertIn("XLF", signal["sectors"])
        self.assertIn("JPM", signal["sectors"])
        print("✅ JSON Content Validation Passed")

if __name__ == "__main__":
    unittest.main()
