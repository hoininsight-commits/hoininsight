import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

class BaseAgent:
    """
    Base Agent class for Phase 21 Modularization.
    Standardizes execution, parameter handling, and logging across all agents.
    """
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.root = Path(".").resolve()
        self.args = self._parse_args()
        self._setup_logging()
        
        self.target_date = self.args.date
        self.ymd_path = self.target_date.replace("-", "/")
        self.dry_run = self.args.dry_run
        
    def _parse_args(self) -> argparse.Namespace:
        parser = argparse.ArgumentParser(description=self.description)
        parser.add_argument(
            "--date", 
            type=str, 
            default=datetime.now().strftime("%Y-%m-%d"),
            help="Target date in YYYY-MM-DD format (default: today)"
        )
        parser.add_argument(
            "--dry-run", 
            action="store_true", 
            help="Simulate execution without writing critical files"
        )
        parser.add_argument(
            "--emit-runlog", 
            action="store_true", 
            help="Generate execution log in data_outputs/ops/runlogs/"
        )
        return parser.parse_known_args()[0]

    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format=f"%(asctime)s [{self.name}] %(levelname)s: %(message)s",
            handlers=[logging.StreamHandler(sys.stdout)]
        )
        self.logger = logging.getLogger(self.name)

    def emit_runlog(self, status: str, metadata: Dict[str, Any] = None):
        """Generates a runlog artifact for CI/Audit visibility."""
        if not self.args.emit_runlog:
            return
            
        log_dir = self.root / "data" / "ops" / "runlogs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_entry = {
            "agent": self.name,
            "timestamp": datetime.now().isoformat(),
            "target_date": self.target_date,
            "status": status,
            "dry_run": self.dry_run,
            "metadata": metadata or {}
        }
        
        log_file = log_dir / f"{self.name}_{datetime.now().strftime('%H%M%S')}.json"
        log_file.write_text(json.dumps(log_entry, indent=2, ensure_ascii=False), encoding="utf-8")
        self.logger.info(f"Runlog emitted: {log_file}")

    def run(self):
        """Main execution entrypoint to be overridden by subclasses."""
        self.logger.info(f"Starting {self.name} for date: {self.target_date} (Dry Run: {self.dry_run})")
        try:
            results = self.execute()
            self.logger.info(f"{self.name} completed successfully.")
            self.emit_runlog("SUCCESS", results)
        except Exception as e:
            self.logger.error(f"{self.name} failed: {e}")
            self.emit_runlog("FAILED", {"error": str(e)})
            sys.exit(1)

    def execute(self) -> Dict[str, Any]:
        """Subclasses must implement the actual logic here."""
        raise NotImplementedError("Subclasses must implement execute()")
