from src.ops.agents.base import BaseAgent
import subprocess
import os

class SignalAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="SignalAgent",
            description="A2: Anomaly Detection & Topic Generation Agent"
        )

    def execute(self):
        # Step 1: Topic Gate (Filters raw collection)
        self.logger.info("Step 1: Running Topic Gate...")
        self._run_module("src.ops.pipeline.run_topic_gate", ["--as-of-date", self.target_date])
        
        # Step 2: Main Engine (Signal Extraction)
        self.logger.info("Step 2: Running Main Engine (Anomaly Discovery)...")
        self._run_module("src.engine")
        
        # Step 3: Topic Candidate Gate (Enforcement/Scoring)
        self.logger.info("Step 3: Running Topic Candidate Gate (Phase 39)...")
        self._run_module("src.topics.topic_candidate_gate")

        # Step 4: IssueSignal (IS-49 Loop Lock)
        self.logger.info("Step 4: Running IssueSignal Engine (Production mode)...")
        self._run_module("src.ops.issuesignal.run_issuesignal", ["--mode=production"])
        
        return {
            "entrypoint": "SignalAgent",
            "modules_run": ["run_topic_gate", "engine", "topic_candidate_gate", "issuesignal"],
            "status": "COMPLETED"
        }

    def _run_module(self, module_name: str, args: list = None):
        if self.dry_run:
            self.logger.info(f"[DRY-RUN] Would run: python -m {module_name} {args or ''}")
            return
            
        cmd = ["python3", "-m", module_name] + (args or [])
        try:
            subprocess.check_call(cmd, env=os.environ)
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Module {module_name} failed with exit code {e.returncode}")
            raise

if __name__ == "__main__":
    SignalAgent().run()
