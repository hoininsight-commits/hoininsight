# src/agents/collectors/macro_agent.py

from pathlib import Path

class MacroAgent:
    name = "MACRO"
    sensitivity = "LOW"
    ttl_minutes = 720

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
            return {
                "agent": self.name,
                "process_success": True,
                "data_valid": True,
                "freshness_status": fred["metadata"]["freshness_status"],
                "result": {"fred": fred, "ecos": ecos}
            }
        except Exception as e:
            print(f"[{self.name}] ❌ 실패: {e}")
            return {
                "agent": self.name,
                "process_success": False,
                "error": str(e)
            }


if __name__ == "__main__":
    from pathlib import Path
    from src.utils.target_date import get_standard_path_prefix
    out = Path("data/raw") / get_standard_path_prefix()
    out.mkdir(parents=True, exist_ok=True)
    MacroAgent(out).run()
