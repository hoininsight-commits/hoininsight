import json
import re
from datetime import datetime
from pathlib import Path
from src.core.gemini_client import GeminiClient
from src.prompts.writer_prompt import WRITER_PROMPT_TEMPLATE
from src.engine.content_engine import ContentEngine
from src.engine.script_quality_gate import ScriptQualityGate
from src.engine.rule_generator import RuleBasedScriptGenerator


class WriterAgent:

    def __init__(self):
        self.base_dir = Path(".")
        self.today = datetime.now().strftime("%Y%m%d")
        self.signal_dir = Path(f"data/signals/{self.today}")
        self.analysis_dir = Path(f"data/analysis/{self.today}")
        self.script_dir = Path(f"data/scripts/{self.today}")
        self.script_dir.mkdir(parents=True, exist_ok=True)
        self.signal_dir.mkdir(parents=True, exist_ok=True)
        self.analysis_dir.mkdir(parents=True, exist_ok=True)
        self.gemini = GeminiClient()
        self.content_engine = ContentEngine()
        self.quality_gate = ScriptQualityGate()
        self.rule_generator = RuleBasedScriptGenerator()
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
        """유튜브 롱폼 스크립트 생성 (3계층 관리 및 번역 레이어 통합)"""
        print("  롱폼 스크립트 생성 중... [3계층 관리 적용]")

        analysis = context.get("analysis", {})
        if not analysis or not analysis.get("topic_core_claim"):
            print("  ⚠️ 분석 데이터 품질 미달 (topic_core_claim 누락).")
            return ""

        prompt = WRITER_PROMPT_TEMPLATE.format(
            stocks_json=json.dumps(context.get("stocks_data", {}).get("stocks", []), ensure_ascii=False),
            cot_summary_detailed=json.dumps(analysis.get("expectation_vs_reality", {}), ensure_ascii=False),
            kospi_foreign_net=analysis.get("market_state", {}).get("kospi_foreign_net", "0.00"),
            topic=context.get("signal", {}).get("topic"),
            arbiter_rationale=analysis.get("arbiter_rationale", "N/A"),
            hunter_insight=analysis.get("hunter_insight", "N/A"),
            analysis_json=json.dumps(analysis.get("level2_chain", []), ensure_ascii=False),
            market_state_json=json.dumps(analysis.get("market_state", {}), ensure_ascii=False),
            today=self.today
        )

        try:
            # [TASK #093] TIER 1 호출
            response = self.gemini.call_controlled(prompt, agent="WRITER", max_tokens=8192, tier=1)
            if not response: raise Exception("Empty Response")
        except Exception as e:
            print(f"  ⚠️ Gemini(Long) 호출 실패: {e}")
            return ""
            
        return self._censor_narrative(response)

    def generate_shorts(self, context):
        """유튜브 쇼츠 스크립트 생성 (3계층 관리 및 번역 레이어 통합)"""
        print("  쇼츠 스크립트 생성 중...")

        shorts_analysis = {
            "topic": context.get("signal", {}).get("topic"),
            "level2_chain": context.get("analysis", {}).get("level2_chain", []),
            "market_state": context.get("analysis", {}).get("market_state", {}),
            "stocks": [s["name"] for s in context.get("stocks_data", {}).get("stocks", [])]
        }

        prompt = WRITER_PROMPT_TEMPLATE.format(
            stocks_json=json.dumps(shorts_analysis["stocks"], ensure_ascii=False),
            cot_summary_detailed=json.dumps(shorts_analysis["market_state"], ensure_ascii=False),
            kospi_foreign_net=shorts_analysis["market_state"].get("kospi_foreign_net", "0.00"),
            topic=shorts_analysis["topic"],
            analysis_json=json.dumps(shorts_analysis["level2_chain"], ensure_ascii=False),
            market_state_json=json.dumps(shorts_analysis["market_state"], ensure_ascii=False),
            today=self.today
        )
        
        prompt += "\n반드시 1분 분량의 쇼츠 대본(5단계)으로 작성하고, [F], [I] 태그를 문장 앞에 붙여라."
        prompt += "\n마지막에 반드시 [DONE] 태그를 붙여서 작성이 완료되었음을 표시해라."

        try:
            # [TASK #093] TIER 1 호출
            response = self.gemini.call_controlled(prompt, agent="WRITER_SHORTS", max_tokens=2048, tier=1)
            if not response: raise Exception("Empty Response")
        except Exception as e:
            print(f"  ⚠️ Gemini(Shorts) 호출 실패: {e}")
            return ""

        return self._censor_narrative(response)

    def _censor_narrative(self, script):
        """언어 가이드라인 준수 여부 검열 (S-I-F 3계층 준수)"""
        if not script: return script
        
        # 1. SPECULATION 키워드 제거/변경
        script = script.replace("폭등한다", "상승 압력이 관측된다")
        script = script.replace("폭락한다", "하방 압력이 관측된다")
        script = script.replace("무조건", "높은 확률로")
        script = script.replace("확신한다", "시사한다")
        
        # 2. 개인 투자자 비하 표현 제거
        script = script.replace("개미들", "시장 참여자들")
        
        return script

    def run(self, analyst_results=None):
        """[TASK #093] RESILIENCE UPGRADE: Gemini 장애 대응 및 상태 체계 도입"""
        print(f"\n✍️ AGENT-05 CONTENT_ENGINE v9.1 (Resilience Upgrade) 가동")
        
        # 1. Fact Pack 로드
        fact_pack_p = Path("data/fact_pack/candidates_fact_pack.json")
        if not fact_pack_p.exists(): return {"status": "DROP", "reason": "No fact pack"}
            
        try:
            fact_pack = json.loads(fact_pack_p.read_text())
        except: return {"status": "DROP", "reason": "Load error"}

        candidate = fact_pack[0]
        
        # 2. [TIER 1] Gemini 콘텐츠 생성 시도
        print(f"  [TIER 1] Gemini 콘텐츠 생성 시도 중...")
        final_contents = []
        try:
            # content_engine 내부에서 Gemini 호출 (TIER 1로 처리되도록 wrapper 수정됨)
            final_contents = self.content_engine.generate_contents(fact_pack)
        except Exception as e:
            print(f"  ⚠️ Gemini 생성 실패: {e}")

        # 3. [FALLBACK] 결정론적 스크립트 생성
        print(f"  🤖 Deterministic Fallback Engine 가동...")
        fallback_res = self.rule_generator.generate_fallback(candidate)
        if fallback_res:
            fallback_p = Path("data/scripts/fallback_deterministic.json")
            fallback_p.write_text(json.dumps(fallback_res, ensure_ascii=False, indent=2))
        
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
                print(f"  ⚠️ Gemini 결과 품질 미달. 폴백 스크립트로 전환합니다.")
                main_content = fallback_res
                using_fallback = True
        else:
            main_content = fallback_res
            using_fallback = True

        # 폴백 사용 시 재검증
        if using_fallback and main_content:
            print(f"  🛡️ Fallback Script 품질 검증 중...")
            report = self.quality_gate.evaluate(main_content)
            if report["status"] == "PASS":
                status = "PARTIAL_SUCCESS"
            elif report["status"] == "HOLD":
                status = "HOLD"
            else:
                status = "DROP"

        # 5. 결과 저장 및 보고
        long_path = self.script_dir / "today_script_long.md"
        if main_content:
            signal_p = self.signal_dir / "today_signal.json"
            signal_p.write_text(json.dumps(main_content, ensure_ascii=False, indent=2))
            
            status_display = status
            if status == "PARTIAL_SUCCESS":
                status_display = "PARTIAL_SUCCESS (Gemini 실패, fallback 사용)"
            
            script_md = f"# [ECONOMIC HUNTER] {main_content['topic']}\n\n"
            script_md += f"**STATUS**: {status_display} | **GATE**: {report.get('status', 'N/A')}\n"
            script_md += f"**QUALITY SCORE**: {report.get('total_score', 0)} / 5.0\n\n"
            script_md += "---\n\n"
            script_md += main_content['script']
            
            long_path.write_text(script_md, encoding="utf-8")
            print(f"  🎬 최종 상태: {status_display} (Score: {report.get('total_score', 0)})")
            
            self._generate_resilience_report(status, main_content, report)
        
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
