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

        # Step 4: [PHASE-24] Investment OS Layer
        self.logger.info("Step 4: [PHASE-24] Running Investment OS Layer...")
        self._run_module("src.ops.investment_os_layer")

        # Step 5: [PHASE-25] Strategic Capital Allocation Layer
        self.logger.info("Step 5: [PHASE-25] Running Strategic Capital Allocation Layer...")
        self._run_module("src.ops.capital_allocation_layer")
        
        # Step 6: Freshness Tracking (Phase 36-B)
        self.logger.info("Step 6: Tracking Ops Freshness...")
        self._run_module("src.ops.freshness_tracker")
        
        # Step 7: Ops Scoreboard (Phase 36-B)
        self.logger.info("Step 7: Updating Ops Scoreboard...")
        self._run_module("src.ops.ops_scoreboard")

        # Step 8: [PHASE-26] Structural Timing Layer
        self.logger.info("Step 8: [PHASE-26] Running Structural Timing Layer...")
        self._run_module("src.ops.structural_timing_layer")
        
        return {
            "entrypoint": "NarrativeAgent",
            "modules_run": ["narrative_intelligence_layer", "structural_regime_layer", "conflict_density_layer", "investment_os_layer", "capital_allocation_layer", "freshness_tracker", "ops_scoreboard", "structural_timing_layer"],
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
