import unittest
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))
from ops.event_input_truth import diagnose

class TestEventInputTruth(unittest.TestCase):
    def test_output_path_missing(self):
        with TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            # Create an EMPTY datasets registry
            reg_dir = tmp_path / "registry"
            reg_dir.mkdir()
            (reg_dir / "datasets.yml").write_text("datasets: []")
            
            res = diagnose("2026-01-26", base_dir=tmp_path)
            self.assertEqual(res["root_cause_code"], "OUTPUT_PATH_MISSING")

    def test_fetch_failed(self):
        with TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            # Create a registry with enabled sources
            reg_dir = tmp_path / "registry"
            reg_dir.mkdir()
            (reg_dir / "datasets.yml").write_text("dataset_id: test\nenabled: true")
            
            res = diagnose("2026-01-26", base_dir=tmp_path)
            self.assertEqual(res["root_cause_code"], "FETCH_FAILED")

    def test_source_registry_missing(self):
        with TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            # No registry directory at all
            res = diagnose("2026-01-26", base_dir=tmp_path)
            # If events.json is missing AND datasets.yml is missing
            self.assertEqual(res["root_cause_code"], "SOURCE_REGISTRY_MISSING")

    def test_output_empty_valid(self):
        with TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            events_dir = tmp_path / "data" / "events" / "2026" / "01" / "26"
            events_dir.mkdir(parents=True)
            events_file = events_dir / "events.json"
            events_file.write_text(json.dumps({"events": []}))
            
            res = diagnose("2026-01-26", base_dir=tmp_path)
            self.assertEqual(res["root_cause_code"], "OUTPUT_EMPTY_VALID")
            self.assertEqual(res["events_count"], 0)

    def test_output_success(self):
        with TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            events_dir = tmp_path / "data" / "events" / "2026" / "01" / "26"
            events_dir.mkdir(parents=True)
            events_file = events_dir / "events.json"
            events_file.write_text(json.dumps({"events": [{"id": 1}]}))
            
            res = diagnose("2026-01-26", base_dir=tmp_path)
            self.assertIsNone(res["root_cause_code"])
            self.assertEqual(res["events_count"], 1)

    def test_parse_failed(self):
        with TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            events_dir = tmp_path / "data" / "events" / "2026" / "01" / "26"
            events_dir.mkdir(parents=True)
            events_file = events_dir / "events.json"
            events_file.write_text("invalid json")
            
            res = diagnose("2026-01-26", base_dir=tmp_path)
            self.assertEqual(res["root_cause_code"], "PARSE_FAILED")

if __name__ == "__main__":
    unittest.main()
