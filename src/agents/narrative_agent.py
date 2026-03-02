from src.agents.base import BaseAgent
import subprocess
import os

class NarrativeAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="NarrativeAgent",
            description="A3: Narrative Intelligence & Scoring Agent"
        )

    def execute(self):
        # Step 1: Narrative Intelligence Layer (WhyNow + Stress)
        self.logger.info("Step 1: Running Narrative Intelligence Layer...")
        self._run_module("src.ops.narrative_intelligence_layer")
        
        # Step 2: Freshness Tracking (Phase 36-B)
        self.logger.info("Step 2: Tracking Ops Freshness...")
        self._run_module("src.ops.freshness_tracker")
        
        # Step 3: Ops Scoreboard (Phase 36-B)
        self.logger.info("Step 3: Updating Ops Scoreboard...")
        self._run_module("src.ops.ops_scoreboard")
        
        return {
            "entrypoint": "NarrativeAgent",
            "modules_run": ["narrative_intelligence_layer", "freshness_tracker", "ops_scoreboard"],
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
    NarrativeAgent().run()
