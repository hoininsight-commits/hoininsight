# src/agents/collectors/macro_agent.py

from pathlib import Path

class MacroAgent:
    name = "MACRO"

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir

    def run(self) -> dict:
        print(f"[{self.name}] 수집 시작...")
        try:
            from src.agents.collector import CollectorAgent
            collector = CollectorAgent()
            collector.output_dir = self.output_dir
            fred = collector.collect_fred()
            ecos = collector.collect_ecos()
            print(f"[{self.name}] ✅ 완료")
            return {"agent": self.name, "status": "success",
                    "result": {"fred": fred, "ecos": ecos}}
        except Exception as e:
            print(f"[{self.name}] ❌ 실패: {e}")
            return {"agent": self.name, "status": "failed", "error": str(e)}
