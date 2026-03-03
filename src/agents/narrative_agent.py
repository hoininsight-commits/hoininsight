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
        # Step 1: Narrative Intelligence Layer
        self.logger.info("Step 1: Running Narrative Intelligence Layer...")
        self._run_module("src.ops.narrative_intelligence_layer")

        # Step 2: [PHASE-23] Structural Regime Layer
        self.logger.info("Step 2: [PHASE-23] Running Structural Regime Layer...")
        self._run_module("src.ops.structural_regime_layer")
        
        # Step 3: [PHASE-22C] Conflict Density Layer
        self.logger.info("Step 3: [PHASE-22C] Running Conflict Density Layer...")
        self._run_module("src.ops.conflict_density_layer")
        
        # Step 4: Freshness Tracking (Phase 36-B)
        self.logger.info("Step 4: Tracking Ops Freshness...")
        self._run_module("src.ops.freshness_tracker")
        
        # Step 5: Ops Scoreboard (Phase 36-B)
        self.logger.info("Step 5: Updating Ops Scoreboard...")
        self._run_module("src.ops.ops_scoreboard")
        
        return {
            "entrypoint": "NarrativeAgent",
            "modules_run": ["narrative_intelligence_layer", "structural_regime_layer", "conflict_density_layer", "freshness_tracker", "ops_scoreboard"],
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
