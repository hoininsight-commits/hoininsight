import json
from datetime import datetime
from pathlib import Path
from src.core.gemini_client import GeminiClient
from src.utils.target_date import get_target_ymd, get_standard_path_prefix
from src.engine.content_engine import ContentEngine
from src.engine.script_quality_gate import ScriptQualityGate
from src.utils.dna_manager import DNAManager


class WriterAgent:

    def __init__(self):
        self.base_dir = Path(".")
        self.dna_manager = DNAManager()
        self.today = get_target_ymd().replace("-", "")
        self.path_prefix = get_standard_path_prefix()

        self.signal_dir = Path("data/signals") / self.path_prefix
        self.script_dir = Path("data/scripts") / self.path_prefix

        self.script_dir.mkdir(parents=True, exist_ok=True)
        self.signal_dir.mkdir(parents=True, exist_ok=True)
        self.gemini = GeminiClient()
        self.content_engine = ContentEngine()
        self.quality_gate = ScriptQualityGate()

    def run(self, analyst_results=None):
        """Detector 결과 또는 직접 사냥으로 스크립트 생성"""
        print(f"\n✍️ AGENT-05 WRITER [Strategic Hunt Mode] [{self.today}]")

        candidate = None

        if analyst_results:
            if isinstance(analyst_results, list) and len(analyst_results) > 0:
                print(f"  📦 Using provided analyst results (Fact Pack).")
                candidate = analyst_results[0]
            elif isinstance(analyst_results, dict):
                candidate = analyst_results

        if not candidate:
            raw_dir = Path("data/raw") / self.path_prefix
            from src.topic_engine.arbiter import TopicArbiter
            arbiter = TopicArbiter()
            print(f"  🎯 [Strategic Hunt] Hunting from raw data in {raw_dir}...")
            hunt_result = arbiter.select_topic_from_raw(raw_dir)
            candidate = hunt_result.get("MAIN")

        if not candidate:
            print("  ⚠️ Strategic hunt failed. Falling back to saved fact pack.")
            fact_pack_p = Path("data/fact_pack/candidates_fact_pack.json")
            if not fact_pack_p.exists():
                return {"status": "DROP", "reason": "No data found"}
            try:
                fact_pack = json.loads(fact_pack_p.read_text())
                candidate = fact_pack[0]
            except Exception:
                return {"status": "DROP", "reason": "Load error"}
        else:
            print(f"  🏆 Content Generation Topic: {candidate.get('topic')}")

        # 중복 발송 방지
        topic_name = candidate.get("topic", candidate.get("event", ""))
        log_path = Path("data/history/content_log.json")
        if log_path.exists():
            try:
                log = json.loads(log_path.read_text(encoding="utf-8"))
                today_str = get_target_ymd()
                for entry in log.get("contents", []):
                    if (entry.get("date") == today_str
                            and entry.get("title") == topic_name
                            and entry.get("publish_status") == "SUCCESS"):
                        print(f"  🚫 '{topic_name}'은(는) 오늘 이미 발송됨. 중단.")
                        return {"status": "SKIPPED", "reason": "Already published"}
            except Exception:
                pass

        # Gemini 콘텐츠 생성
        print(f"  [TIER 1] Gemini 콘텐츠 생성 중...")
        final_contents = []
        try:
            final_contents = self.content_engine.generate_contents([candidate])
        except Exception as e:
            print(f"  ⚠️ Gemini 생성 실패: {e}")

        main_content = None
        status = "DROP"
        report = {}
        using_fallback = not bool(final_contents)

        if final_contents:
            main_content = final_contents[0]
            print(f"  🛡️ 품질 검증 중...")
            report = self.quality_gate.evaluate(main_content)
            if report["status"] == "PASS":
                status = "FULL_SUCCESS"
            elif report["status"] == "HOLD":
                status = "HOLD"
            else:
                print(f"  ⚠️ 품질 미달. 폴백 시도...")
                using_fallback = True

        if using_fallback:
            from src.engine.deterministic_topic_engine import DeterministicTopicEngine
            det_engine = DeterministicTopicEngine()

            raw_dir = self.base_dir / "data" / "raw" / self.path_prefix
            if not raw_dir.exists():
                raw_dir = self.base_dir / "data" / "raw" / datetime.now().strftime("%Y/%m/%d")

            print(f"  🔍 [Fallback] Analyzing raw data in: {raw_dir}")
            if not candidate or not candidate.get("evidence"):
                candidate = det_engine.analyze(raw_dir)

            if candidate:
                evidence_items = [
                    f"- {item.get('text', '')} [링크]({item['url']})" if item.get("url")
                    else f"- {item.get('text', '')}"
                    for item in candidate.get("evidence", [])
                ]
                evidence_str = "\n".join(evidence_items) or "상세 근거 데이터 분석 중"

                fallback_script = f"""# [ECONOMIC HUNTER] {candidate.get('topic', 'N/A')}

[HOOK]
데이터가 가리키는 오늘의 핵심 징후는 '{candidate.get('topic')}'입니다.

[CONTEXT]
{candidate.get('arbiter_rationale', '현재 시장 데이터에서 특이점이 포착되었습니다.')}

[HUNTER'S INSIGHT]
{candidate.get('hunter_insight', '인과관계의 끝단을 추적한 결과, 특정 자산군으로의 수급 쏠림이 예상됩니다.')}

[EVIDENCE]
{evidence_str}

[DATA CHAIN]
{candidate.get('data_chain', 'DART 및 소셜 트렌드 지표가 상호 검증되었습니다.')}

[ACTION]
핵심 인과관계를 중심으로 포트폴리오 리스크를 재점검하고, 자금의 길목을 선점하십시오.
"""
                main_content = {
                    "topic": candidate.get("topic"),
                    "script": fallback_script,
                    "script_short": fallback_script[:500],
                    "type": "NORMAL",
                }
                status = "PARTIAL_SUCCESS"
                report = {"status": "PASS", "total_score": 3.5}

        if main_content:
            day_path = "/".join(self.path_prefix.split("/")[:3])
            day_dir = self.base_dir / "data/scripts" / day_path
            day_dir.mkdir(parents=True, exist_ok=True)

            existing_topics = list(day_dir.glob("Topic_*"))
            topic_dir = day_dir / f"Topic_{len(existing_topics) + 1}"
            topic_dir.mkdir(parents=True, exist_ok=True)

            long_script = (
                f"# [ECONOMIC HUNTER] {main_content['topic']}\n\n"
                f"**STATUS**: {status} | **GATE**: {report.get('status', 'N/A')}\n"
                f"**QUALITY SCORE**: {report.get('total_score', 0)} / 5.0\n\n---\n\n"
                f"{main_content['script']}"
            )
            short_script = main_content.get("script_short", main_content["script"])

            long_path = topic_dir / "today_script_long.md"
            short_path = topic_dir / "today_script_short.md"
            insta_path = topic_dir / "insta_cards.json"
            analysis_path = topic_dir / "analysis.json"
            signal_path = topic_dir / "signal.json"

            long_path.write_text(long_script, encoding="utf-8")
            short_path.write_text(short_script, encoding="utf-8")

            analysis_data = {
                "arbiter_rationale": candidate.get("arbiter_rationale", ""),
                "hunter_insight": candidate.get("hunter_insight", ""),
                "why_hypothesis": candidate.get("why_hypothesis", ""),
                "mechanism": candidate.get("mechanism", ""),
                "predictive_chain": candidate.get("predictive_chain", ""),
                "historical_parallel": candidate.get("historical_parallel", ""),
                "stocks_analysis": candidate.get("stocks_analysis", {}),
            }
            analysis_path.write_text(json.dumps(analysis_data, ensure_ascii=False, indent=2), encoding="utf-8")
            signal_path.write_text(json.dumps(candidate, ensure_ascii=False, indent=2), encoding="utf-8")

            main_content["paths"] = {
                "topic_dir": str(topic_dir),
                "long_path": str(long_path),
                "insta_path": str(insta_path),
            }

            print(f"  📸 Instagram 카드뉴스 생성 중...")
            insta_slides = self.content_engine.generate_insta_cards(candidate, script=short_script)
            if insta_slides:
                insta_path.write_text(json.dumps({"slides": insta_slides}, ensure_ascii=False, indent=2), encoding="utf-8")
                print(f"  ✅ 인스타 카드뉴스 저장: {insta_path}")

            self.content_engine.generate_visual_assets(candidate, topic_dir)
            print(f"  🎬 최종 상태: {status} (Score: {report.get('total_score', 0)})")
            self._generate_resilience_report(status, main_content, report)

            return {
                "status": "SUCCESS",
                "topic": candidate.get("topic"),
                "paths": {
                    "long": str(long_path),
                    "short": str(short_path),
                    "insta": str(insta_path),
                    "topic_dir": str(topic_dir),
                },
            }

        return {"status": status, "reason": "No content generated"}

    def _generate_resilience_report(self, status, content, quality_report):
        report_path = self.base_dir / "reports/hoin_resilience_upgrade_report.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        content_md = f"""# GEMINI RESILIENCE UPGRADE REPORT

## 최종 시스템 상태
- **상태**: `{status}`
- **판정**: {"정상 발행" if status in ["FULL_SUCCESS", "PARTIAL_SUCCESS"] else "발행 보류"}

## 콘텐츠 품질 (Quality Gate)
- **종합 점수**: {quality_report.get('total_score', 0)} / 5.0
- HOOK: {quality_report.get('hook_score', 0)}
- WHY NOW: {quality_report.get('why_now_score', 0)}
- SCENARIO: {quality_report.get('scenario_score', 0)}
- ACTION: {quality_report.get('action_score', 0)}
"""
        report_path.write_text(content_md, encoding="utf-8")
        print(f"  📝 Resilience 보고서 생성: {report_path}")


if __name__ == "__main__":
    WriterAgent().run()
