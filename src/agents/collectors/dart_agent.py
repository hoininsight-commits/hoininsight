# src/agents/collectors/dart_agent.py

from pathlib import Path

class DartAgent:
    name = "DART"
    sensitivity = "MID"
    ttl_minutes = 120

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir

    def run(self) -> dict:
        print(f"[{self.name}] 수집 시작...")
        try:
            from src.agents.collector import CollectorAgent
            collector = CollectorAgent()
            collector.output_dir = self.output_dir
            result = collector.collect_dart()
            print(f"[{self.name}] ✅ 완료")
            return {
                "agent": self.name,
                "process_success": True,
                "data_valid": result["metadata"]["freshness_status"] != "UNKNOWN",
                "freshness_status": result["metadata"]["freshness_status"],
                "result": result
            }
        except Exception as e:
            print(f"[{self.name}] ❌ 실패: {e}")
            return {
                "agent": self.name, 
                "process_success": False, 
                "error": str(e)
            }
