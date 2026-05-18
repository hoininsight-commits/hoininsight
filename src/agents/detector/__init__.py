import json
import os
from pathlib import Path
from src.utils.target_date import get_target_ymd, get_current_round, get_standard_path_prefix
from src.core.gemini_client import GeminiClient


class DetectorAgent:
    """이상징후 탐지자 — Arbiter를 통해 로우 데이터 전수 조사 후 최강 토픽 선정"""

    def __init__(self):
        self.base_dir = Path(os.getenv("HOIN_BASE_DIR", Path(__file__).resolve().parents[3]))
        self.today = get_target_ymd().replace("-", "")
        self.round = get_current_round()
        self.path_prefix = get_standard_path_prefix()
        self.raw_dir = self.base_dir / "data/raw" / self.path_prefix
        self.signal_dir = self.base_dir / "data/signals" / self.path_prefix
        self.signal_dir.mkdir(parents=True, exist_ok=True)
        self.gemini = GeminiClient()

    def run(self, collector_result=None):
        """로우 데이터 전수 조사 → Arbiter 토픽 선정 → fact_pack 저장"""
        print(f"\n🔍 AGENT-03 DETECTOR [Strategic Hunt Mode] [{self.today}]")

        if not self.raw_dir.exists():
            print(f"  ⚠️ Raw directory not found: {self.raw_dir}")
            return {}

        from src.topic_engine.arbiter import TopicArbiter
        arbiter = TopicArbiter()

        print(f"  🎯 Analyzing all raw data in {self.raw_dir}...")
        hunt_result = arbiter.select_topic_from_raw(self.raw_dir)

        main = hunt_result.get("MAIN")
        if not main:
            print("  ❌ Strategic hunt failed to produce a topic.")
            return {}

        fact_pack = [{
            "topic": main["topic"],
            "core_facts": [],
            "classification": "STRATEGIC",
            "why_now": [main.get("arbiter_rationale", "")],
            "evidence_bundle": {
                "data_chain": main.get("data_chain"),
                "social_intelligence": main.get("hunter_insight"),
            },
            "arbiter_rationale": main.get("arbiter_rationale"),
            "hunter_insight": main.get("hunter_insight"),
            "actionable_event": main.get("actionable_event"),
            "tier": "MAIN/TIER_1",
        }]

        fact_pack_dir = Path("data/fact_pack")
        fact_pack_dir.mkdir(parents=True, exist_ok=True)
        (fact_pack_dir / "candidates_fact_pack.json").write_text(
            json.dumps(fact_pack, ensure_ascii=False, indent=2)
        )
        (self.signal_dir / "today_signal.json").write_text(
            json.dumps(main, ensure_ascii=False, indent=2)
        )

        print(f"  ✅ Strategic Hunt Completed: {main['topic']}")
        return {"selected": hunt_result, "fact_pack": fact_pack}


if __name__ == "__main__":
    DetectorAgent().run()
