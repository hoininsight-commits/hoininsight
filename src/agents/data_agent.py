from src.agents.base import BaseAgent
import subprocess
import os

class DataAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="DataAgent",
            description="A1: Data Collection & Normalization Agent"
        )

    def execute(self):
        self.logger.info("Step 1: Running Market Collectors...")
        self._run_module("src.collectors.market_collectors")
        
        self.logger.info("Step 2: Running FRED Collector...")
        self._run_module("src.collectors.fred_collector")
        
        self.logger.info("Step 3: Running ECOS Collector...")
        self._run_module("src.collectors.ecos_collector")
        
        self.logger.info("Step 4: Running CoinGecko Collector...")
        self._run_module("src.collectors.coingecko_btc")
        
        self.logger.info("Step 5: Running Policy Collector...")
        self._run_module("src.collectors.policy_collector")
        
        # [PHASE 21] Placeholder for future normalization step if separated
        # self._run_module("src.pipeline.run_normalize")
        
        return {
            "collectors_run": ["market", "fred", "ecos", "coingecko", "policy"],
            "status": "COMPLETED"
        }

    def _run_module(self, module_name: str):
        if self.dry_run:
            self.logger.info(f"[DRY-RUN] Would run: python -m {module_name}")
            return
            
        cmd = ["python3", "-m", module_name]
        try:
            # We use check_call to ensure the pipeline stops on failure
            subprocess.check_call(cmd, env=os.environ)
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Module {module_name} failed with exit code {e.returncode}")
            raise

if __name__ == "__main__":
    DataAgent().run()
