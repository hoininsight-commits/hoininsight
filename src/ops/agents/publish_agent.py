from src.ops.agents.base import BaseAgent
import subprocess
import os

class PublishAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="PublishAgent",
            description="A6: Asset Publishing & Delivery Agent (SSOT)"
        )

    def execute(self):
        # Step 1: Run SSOT Publisher
        self.logger.info("Step 1: Running SSOT Asset Publisher...")
        self._run_module("src.ui.run_publish_ui_decision_assets")
        
        # Step 2: Dashboard Generation (Reporter role, but part of final publish flow)
        self.logger.info("Step 2: Updating Dashboard Reports...")
        self._run_module("src.ui.dashboard.topic_exporter")
        self._run_module("src.ui.dashboard.dashboard_generator")
        
        return {
            "entrypoint": "PublishAgent",
            "modules_run": ["run_publish_ui_decision_assets", "topic_exporter", "dashboard_generator"],
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
    PublishAgent().run()
