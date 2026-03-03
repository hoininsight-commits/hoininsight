from src.agents.base import BaseAgent
import subprocess
import os

class VideoAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="VideoAgent",
            description="A5: Video Intelligence & Candidate Pool Agent"
        )

    def execute(self):
        # Step 1: Video Intelligence Layer
        self.logger.info("Step 1: Running Video Intelligence Layer...")
        self._run_module("src.ops.video_intelligence_layer")
        
        # Step 2: Script Intelligence Layer
        self.logger.info("Step 2: Running Script Intelligence Layer...")
        self._run_module("src.ops.video_script_intelligence_layer")
        
        return {
            "entrypoint": "VideoAgent",
            "modules_run": ["video_intelligence_layer", "video_script_intelligence_layer"],
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
    VideoAgent().run()
