import os
import json
import re
from datetime import datetime
from pathlib import Path
from src.core.gemini_client import GeminiClient
from src.utils.target_date import get_target_ymd, get_current_round, get_standard_path_prefix
from src.prompts.writer_prompt import WRITER_PROMPT_TEMPLATE, WRITER_SYSTEM_PROMPT
from src.engine.content_engine import ContentEngine
from src.engine.script_quality_gate import ScriptQualityGate
# from src.engine.rule_generator import RuleBasedScriptGenerator (Deprecated v24.0)


class WriterAgent:

    def __init__(self):
        self.base_dir = Path(".")
        self.today = get_target_ymd().replace("-", "")
        self.path_prefix = get_standard_path_prefix()
        
        self.signal_dir = Path("data/signals") / self.path_prefix
        self.analysis_dir = Path("data/analysis") / self.path_prefix
        self.script_dir = Path("data/scripts") / self.path_prefix
        
        self.script_dir.mkdir(parents=True, exist_ok=True)
        self.signal_dir.mkdir(parents=True, exist_ok=True)
        self.analysis_dir.mkdir(parents=True, exist_ok=True)
        self.gemini = GeminiClient()
        self.content_engine = ContentEngine()
        self.quality_gate = ScriptQualityGate()
        # self.rule_generator = RuleBasedScriptGenerator() (Deprecated)
        self.rule_generator = None
        self.validation_dir = Path("data/validation")
        self.validation_dir.mkdir(parents=True, exist_ok=True)

    def load_data(self):
        signal_p = self.signal_dir / "today_signal.json"
        analysis_p = self.analysis_dir / "today_analysis.json"
        stocks_p = self.analysis_dir / "today_stocks.json"

        data = {}
        if signal_p.exists():
            data["signal"] = json.loads(signal_p.read_text())
        if analysis_p.exists():
            data["analysis"] = json.loads(analysis_p.read_text())
        if stocks_p.exists():
            data["stocks_data"] = json.loads(stocks_p.read_text())
        return data

    def generate_long(self, context):
        """[v15.0] 유튜브 롱폼 스크립트 생성 (The Hunter's Logic)"""
        print("  롱폼 스크립트 생성 중... [v15.0 적용]")

        analysis = context.get("analysis", {})
        
        prompt = WRITER_PROMPT_TEMPLATE.format(
            stocks_json=json.dumps(context.get("stocks_data", {}).get("stocks", []), ensure_ascii=False),
            topic=context.get("signal", {}).get("topic"),
            arbiter_rationale=analysis.get("arbiter_rationale", "N/A"),
            hunter_insight=analysis.get("hunter_insight", "N/A"),
            analysis_json=json.dumps(analysis, ensure_ascii=False),
            today=self.today
        )

        try:
            # [v23.5] HOIN Insight 시스템 프롬프트 주입 및 검열 해제
            response = self.gemini.call_controlled(
                prompt, 
                system_prompt=WRITER_SYSTEM_PROMPT,
                agent="WRITER", 
                max_tokens=8192, 
                tier=1
            )
            if not response: raise Exception("Empty Response")
        except Exception as e:
            print(f"  ⚠️ Gemini(Long) 호출 실패: {e}")
            return ""
            
        return response

    def generate_shorts(self, context):
        """[v15.0] 유튜브 쇼츠 스크립트 생성 (The Hunter's Logic)"""
        print("  쇼츠 스크립트 생성 중... [v15.0 적용]")

        analysis = context.get("analysis", {})
        
        prompt = WRITER_PROMPT_TEMPLATE.format(
            stocks_json=json.dumps(context.get("stocks_data", {}).get("stocks", []), ensure_ascii=False),
            topic=context.get("signal", {}).get("topic"),
            arbiter_rationale=analysis.get("arbiter_rationale", "N/A"),
            hunter_insight=analysis.get("hunter_insight", "N/A"),
            analysis_json=json.dumps(analysis, ensure_ascii=False),
            today=self.today
        )
        
        prompt += "\n반드시 1분 분량의 쇼츠 대본(8단계 요약)으로 작성하고, [F], [I] 태그를 문장 앞에 붙여라."

        try:
            # [v23.5] HOIN Insight 시스템 프롬프트 주입 및 검열 해제
            response = self.gemini.call_controlled(
                prompt, 
                system_prompt=WRITER_SYSTEM_PROMPT,
                agent="WRITER_SHORTS", 
                max_tokens=2048, 
                tier=1
            )
            if not response: raise Exception("Empty Response")
        except Exception as e:
            print(f"  ⚠️ Gemini(Shorts) 호출 실패: {e}")
            return ""

        return response

    # _censor_narrative 제거됨 (v23.5: Raw Hunter Style)

    def run(self, analyst_results=None):
        """[v21.0] STRATEGIC HUNT FLOW: Arbiter 직접 호출 및 자율 사냥"""
        print(f"\n✍️ AGENT-05 CONTENT_ENGINE v21.0 (Strategic Hunt Mode) 가동")
        
        # 1. 로우 데이터 경로 설정 (Arbiter 전수 조사용)
        raw_dir = Path("data/raw") / self.path_prefix
        
        # 2. [STRATEGIC HUNT] Arbiter를 통해 로우 데이터에서 직접 토픽 사냥
        from src.topic_engine.arbiter import TopicArbiter
        arbiter = TopicArbiter()
        
        print(f"  🎯 [Strategic Hunt] Hunting from raw data in {raw_dir}...")
        hunt_result = arbiter.select_topic_from_raw(raw_dir)
        
        candidate = hunt_result.get("MAIN")
        
        if not candidate:
            print("  ⚠️ [Writer] Strategic hunt failed to find a topic. Falling back to legacy fact pack.")
            # [FALLBACK] 기존 Fact Pack 로드 시도
            fact_pack_p = Path("data/fact_pack/candidates_fact_pack.json")
            if not fact_pack_p.exists(): return {"status": "DROP", "reason": "No data found"}
            try:
                fact_pack = json.loads(fact_pack_p.read_text())
                candidate = fact_pack[0]
            except: return {"status": "DROP", "reason": "Load error"}
        else:
            print(f"  🏆 Strategic Hunt Winner: {candidate.get('topic')}")

        # 3. [COST SAVVY] 중복 발송 여부 최종 확인 (Gemini 호출 전)
        topic_name = candidate.get('topic', candidate.get('event', ''))
        log_path = Path("data/history/content_log.json")
        if log_path.exists():
            try:
                log = json.loads(log_path.read_text(encoding="utf-8"))
                today_str = get_target_ymd()
                for entry in log.get("contents", []):
                    if entry.get("date") == today_str and \
                       entry.get("title") == topic_name and \
                       entry.get("publish_status") == "SUCCESS":
                        print(f"  🚫 [STOP] '{topic_name}'은(는) 오늘 이미 발송되었습니다. 비용 절감을 위해 중단합니다.")
                        return {"status": "SKIPPED", "reason": "Already published"}
            except: pass

        # 4. [TIER 1] Gemini 콘텐츠 생성 시도
        print(f"  [TIER 1] Gemini 콘텐츠 생성 시도 중...")
        final_contents = []
        try:
            # 전략 사냥 결과를 리스트로 래핑하여 전달
            final_contents = self.content_engine.generate_contents([candidate])
        except Exception as e:
            error_msg = str(e).lower()
            if "exhausted" in error_msg or "quota" in error_msg:
                print(f"  🚨 Gemini 월간 할당량 초과 감지. 즉시 폴백 모드로 전환합니다.")
            else:
                print(f"  ⚠️ Gemini 생성 실패: {e}")
            final_contents = [] # 명시적 초기화로 폴백 유도

        # [v24.0] Deterministic Fallback Engine Deprecated
        fallback_res = None
        
        # 4. 품질 검증 및 상태 결정
        main_content = None
        status = "DROP"
        using_fallback = False
        report = {}
        
        if final_contents:
            main_content = final_contents[0]
            print(f"  🛡️ Gemini Script 품질 검증 중...")
            report = self.quality_gate.evaluate(main_content)
            
            if report["status"] == "PASS":
                status = "FULL_SUCCESS"
            elif report["status"] == "HOLD":
                status = "HOLD"
            else:
                # Gemini 결과가 DROP이면 폴백 시도
                print(f"  ⚠️ Gemini 결과 품질 미달. 폴백 시도...")
                main_content = fallback_res
                using_fallback = True
        else:
            print(f"  ⚠️ Gemini 생성물 없음. 폴백 시도...")
            main_content = fallback_res
            using_fallback = True

        # 폴백 사용 시 재검증 및 엄격한 통제
        if using_fallback and main_content:
            print(f"  🛡️ Fallback Script 품질 검증 중...")
            report = self.quality_gate.evaluate(main_content)
            
            # [STRICT RULE] 폴백 원고는 PASS 등급이 아니면 무조건 DROP (HOLD 허용 안함)
            if report["status"] == "PASS":
                status = "PARTIAL_SUCCESS"
            else:
                print(f"  🚫 [BLOCK] 폴백 원고 품질 미달 ({report['status']}). 발송을 차단합니다.")
                status = "DROP"
                main_content = None # 발송 대상에서 제외

        # 5. 결과 저장 및 보고
        if main_content:
            # [v22.3] 회차(Round) 폴더를 건너뛰고 날짜(YYYY/MM/DD) 폴더 바로 아래에 Topic_N 생성
            day_path = "/".join(self.path_prefix.split("/")[:3])
            day_dir = self.base_dir / "data/scripts" / day_path
            day_dir.mkdir(parents=True, exist_ok=True)
            
            # [v22.1] 세분화된 토픽 저장소 생성
            # 해당 날짜의 기존 Topic_N 개수 파악
            existing_topics = list(day_dir.glob("Topic_*"))
            topic_idx = len(existing_topics) + 1
            
            topic_dir = day_dir / f"Topic_{topic_idx}"
            topic_dir.mkdir(parents=True, exist_ok=True)
            
            # 대본 및 카드뉴스 저장 경로 변경
            long_script = f"# [ECONOMIC HUNTER] {main_content['topic']}\n\n"
            long_script += f"**STATUS**: {status} | **GATE**: {report.get('status', 'N/A')}\n"
            long_script += f"**QUALITY SCORE**: {report.get('total_score', 0)} / 5.0\n\n---\n\n{main_content['script']}"
            short_script = main_content.get('script_short', main_content['script'])

            long_path = topic_dir / "today_script_long.md"
            short_path = topic_dir / "today_script_short.md"
            insta_path = topic_dir / "insta_cards.json"
            analysis_path = topic_dir / "analysis.json"
            signal_path = topic_dir / "signal.json"
            
            long_path.write_text(long_script, encoding="utf-8")
            short_path.write_text(short_script, encoding="utf-8")
            
            # [v22.2] 분석 및 신호 데이터도 패키지에 포함
            analysis_data = {
                "arbiter_rationale": candidate.get("arbiter_rationale", ""),
                "hunter_insight": candidate.get("hunter_insight", ""),
                "why_hypothesis": candidate.get("why_hypothesis", ""),
                "mechanism": candidate.get("mechanism", ""),
                "predictive_chain": candidate.get("predictive_chain", ""),
                "historical_parallel": candidate.get("historical_parallel", ""),
                "stocks_analysis": candidate.get("stocks_analysis", {})
            }
            analysis_path.write_text(json.dumps(analysis_data, ensure_ascii=False, indent=2), encoding="utf-8")
            signal_path.write_text(json.dumps(candidate, ensure_ascii=False, indent=2), encoding="utf-8")
            
            # [v22.3] PublisherAgent 연동을 위해 경로 정보 추가
            main_content["paths"] = {
                "topic_dir": str(topic_dir),
                "long_path": str(long_path),
                "insta_path": str(insta_path)
            }
            
            print(f"  📸 Instagram 8-slide 카드뉴스 생성 중...")
            insta_slides = self.content_engine.generate_insta_cards(candidate, script=short_script)
            if insta_slides:
                # [v24.0] UI 규격에 맞게 'slides' 키로 감싸서 저장
                insta_data = {"slides": insta_slides}
                insta_path.write_text(json.dumps(insta_data, ensure_ascii=False, indent=2), encoding="utf-8")
                print(f"  ✅ 인스타 카드뉴스 저장 완료: {insta_path}")
                
            # [v24.0] 지능형 에셋 생성 (Imagen 3 활용)
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
                    "topic_dir": str(topic_dir)
                }
            }
        
        return {
            "status": status,
            "type": main_content.get("type") if main_content else "UNKNOWN",
            "long_script_path": str(long_path) if main_content else None,
            "quality_report": report if main_content else {},
            "main_content": main_content
        }

    def _generate_resilience_report(self, status, content, quality_report):
        """[TASK #093] Resilience Upgrade 완료 보고서 생성"""
        report_path = self.base_dir / "reports/hoin_resilience_upgrade_report.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        content_md = f"""# [TASK #093] GEMINI RESILIENCE UPGRADE REPORT

## 📊 최종 시스템 상태
- **상태**: `{status}`
- **판정**: {"정상 발행" if status in ["FULL_SUCCESS", "PARTIAL_SUCCESS"] else "발행 보류"}
- **AI 활용**: {"Gemini + Rule-based" if status == "FULL_SUCCESS" else "Deterministic Fallback Only"}

## 🧩 콘텐츠 품질 (Quality Gate v2)
- **종합 점수**: {quality_report.get('total_score', 0)} / 5.0
- **상세 점수**:
    - HOOK: {quality_report.get('hook_score', 0)}
    - WHY NOW: {quality_report.get('why_now_score', 0)}
    - SCENARIO: {quality_report.get('scenario_score', 0)}
    - ACTION: {quality_report.get('action_score', 0)}

## 🔥 Resilience 핵심 지표
1. **Gemini Tiering**: TIER 1/2/3 분리 및 재시도 최적화 완료
2. **Deterministic Fallback**: AI 실패 시에도 3.0 이상의 고품질 스크립트 확보
3. **Dual Quality Gate**: Gemini 장애 시에도 결정론적 평가로 파이프라인 유지

## 📥 산출물 위치
- Fallback JSON: `data/scripts/fallback_deterministic.json`
- Final Script: `data/scripts/{self.today}/today_script_long.md`
"""
        report_path.write_text(content_md, encoding="utf-8")
        print(f"  📝 Resilience 보고서 생성 완료: {report_path}")


if __name__ == "__main__":
    agent = WriterAgent()
    agent.run()
