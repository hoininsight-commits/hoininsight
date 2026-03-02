from src.agents.base import BaseAgent
import subprocess
import os

class DecisionAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="DecisionAgent",
            description="A4: Approval & Final Decision Card Agent"
        )

    def execute(self):
        # Step 1: Auto Approval Gate (Phase 39)
        self.logger.info("Step 1: Running Auto Approval Gate...")
        self._run_module("src.ops.auto_approval_gate")
        
        # Step 2: Final Decision Card Generation (Phase 38)
        self.logger.info("Step 2: Generating Final Decision Card...")
        self._run_module("src.decision.final_decision_card")
        
        # Step 3: Health Check & Metadata
        self.logger.info("Step 3: Generating Operational Metadata (Health/Coverage)...")
        self._run_module("src.ops.health_check")
        self._run_module("src.ops.event_coverage")
        self._run_module("src.ops.dashboard_manifest")
        
        return {
            "entrypoint": "DecisionAgent",
            "modules_run": ["auto_approval_gate", "final_decision_card", "health_check", "event_coverage", "dashboard_manifest"],
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
    DecisionAgent().run()
