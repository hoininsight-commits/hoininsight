
import unittest
from pathlib import Path
import sys
import shutil

# Ensure project root is in sys.path
root_path = Path(__file__).resolve().parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from src.dashboard.snapshot_viewer_generator import EconomicHunterSnapshotViewerGenerator

class TestSnapshotViewer(unittest.TestCase):
    def setUp(self):
        self.base_dir = Path("test_snapshot_viewer_env")
        self.base_dir.mkdir(exist_ok=True)
        self.snapshots_dir = self.base_dir / "data" / "snapshots"
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir = self.base_dir / "dashboard" / "snapshot"
        
        # Create dummy snapshots
        (self.snapshots_dir / "2026-01-27_top1_snapshot.md").write_text("# Snapshot 2026-01-27\n\nContent for 27th.", encoding="utf-8")
        (self.snapshots_dir / "2026-01-26_top1_snapshot.md").write_text("# Snapshot 2026-01-26\n\nContent for 26th.", encoding="utf-8")

    def tearDown(self):
        if self.base_dir.exists():
            shutil.rmtree(self.base_dir)

    def test_generator(self):
        print("\n=== Testing Snapshot Viewer Generator ===")
        generator = EconomicHunterSnapshotViewerGenerator(self.base_dir)
        output_file = generator.generate()
        
        # 1. Check file existence
        self.assertTrue(output_file.exists())
        self.assertEqual(output_file.name, "index.html")
        print("✅ HTML File Created")
        
        # 2. Check Content
        content = output_file.read_text(encoding="utf-8")
        
        # Check static strings
        self.assertIn("SYSTEM COGNITIVE SNAPSHOT", content)
        self.assertIn("OPERATOR VIEW ONLY", content)
        print("✅ Static Headers Found")
        
        # Check Data Injection
        self.assertIn('2026-01-27"', content)
        self.assertIn('2026-01-26"', content)
        self.assertIn("Snapshot 2026-01-27", content) # Markdown title should be there (maybe rendered)
        # Actually our parser renders # Header as <h3>Header</h3>
        self.assertIn("Content for 27th", content)
        print("✅ Data Injected Successfully")

if __name__ == "__main__":
    unittest.main()
