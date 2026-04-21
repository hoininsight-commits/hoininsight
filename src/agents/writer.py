import json
import re
from datetime import datetime
from pathlib import Path
from src.core.gemini_client import GeminiClient
from src.prompts.writer_prompt import WRITER_PROMPT_TEMPLATE


class WriterAgent:

    def __init__(self):
        self.today = datetime.now().strftime("%Y%m%d")
        self.signal_dir = Path(f"data/signals/{self.today}")
        self.analysis_dir = Path(f"data/analysis/{self.today}")
        self.script_dir = Path(f"data/scripts/{self.today}")
        self.script_dir.mkdir(parents=True, exist_ok=True)
        self.gemini = GeminiClient()

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

        # Phase 4 Task 5: 품질 검증 - 분석 데이터에 핵심 클레임이 없는 경우 즉시 Fallback
        analysis = context.get("analysis", {})
        if not analysis or not analysis.get("topic_core_claim"):
            print("  ⚠️ 분석 데이터 품질 미달 (topic_core_claim 누락). 즉시 Fallback 적용.")
            from src.writer.fallback_writer import generate_fallback, format_fallback_as_md
            fb_data = generate_fallback(context.get("signal", {}), analysis)
            return format_fallback_as_md(fb_data)

        # 프롬프트 데이터 준비
        prompt = WRITER_PROMPT_TEMPLATE.format(
            stocks_json=json.dumps(context.get("stocks_data", {}).get("stocks", []), ensure_ascii=False),
            cot_summary_detailed=json.dumps(analysis.get("expectation_vs_reality", {}), ensure_ascii=False),
            kospi_foreign_net=analysis.get("market_state", {}).get("kospi_foreign_net", "0.00"),
            topic=context.get("signal", {}).get("topic"),
            analysis_json=json.dumps(analysis.get("level2_chain", []), ensure_ascii=False),
            market_state_json=json.dumps(analysis.get("market_state", {}), ensure_ascii=False),
            today=self.today
        )

        try:
            response = self.gemini.call_controlled(prompt, agent="WRITER", max_tokens=3500)
            if not response: raise Exception("Empty Response")
        except Exception as e:
            print(f"  ⚠️ Gemini(Long) 호출 실패, Fallback 모드 가동: {e}")
            from src.writer.fallback_writer import generate_fallback, format_fallback_as_md
            fb_data = generate_fallback(context.get("signal", {}), context.get("analysis", {}))
            response = format_fallback_as_md(fb_data)
            
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

        # 쇼츠용으로 커스터마이징된 프롬프트 (템플릿 기반)
        prompt = WRITER_PROMPT_TEMPLATE.format(
            stocks_json=json.dumps(shorts_analysis["stocks"], ensure_ascii=False),
            cot_summary_detailed=json.dumps(shorts_analysis["market_state"], ensure_ascii=False),
            kospi_foreign_net=shorts_analysis["market_state"].get("kospi_foreign_net", "0.00"),
            topic=shorts_analysis["topic"],
            analysis_json=json.dumps(shorts_analysis["level2_chain"], ensure_ascii=False),
            market_state_json=json.dumps(shorts_analysis["market_state"], ensure_ascii=False),
            today=self.today
        )
        
        # 쇼츠 전용 제약 추가
        prompt += "\n반드시 1분 분량의 쇼츠 대본(5단계)으로 작성하고, [F], [I] 태그를 문장 앞에 붙여라."
        prompt += "\n마지막에 반드시 [DONE] 태그를 붙여서 작성이 완료되었음을 표시해라."

        try:
            response = self.gemini.call_controlled(prompt, agent="WRITER", max_tokens=4000)
            if not response: raise Exception("Empty Response")
        except Exception as e:
            print(f"  ⚠️ Gemini(Shorts) 호출 실패, Fallback 모드 가동: {e}")
            from src.writer.fallback_writer import generate_fallback, format_fallback_as_md
            fb_data = generate_fallback(context.get("signal", {}), context.get("analysis", {}))
            response = format_fallback_as_md(fb_data)
        
        is_completed = "[DONE]" in response or "(Step 7:" in response or "(Risk:" in response
        print(f"  [COMPLETION_TRACE] Shorts Response Status: {'COMPLETED' if is_completed else 'TRUNCATED'}")
        
        return self._censor_narrative(response)

    def _censor_narrative(self, text: str) -> str:
        """생성된 스크립트에서 SPECULATION 차단 및 태그 제거 (Hardened #053)"""
        if not text:
            return text
            
        # 1. SPECULATION [S] 라인 전면 삭제
        lines = text.split("\n")
        filtered_lines = []
        for line in lines:
            if "[S]" in line:
                continue
            filtered_lines.append(line)
        text = "\n".join(filtered_lines)

        # 2. 태그 제거 ([F], [I] 제거하여 최종 사용자용으로 변환)
        text = re.sub(r"\[F\]\s*", "", text)
        text = re.sub(r"\[I\]\s*", "", text)

        # 3. 추가적인 하드코딩된 단정적 추측 차단 (Task 2 강화 #053)
        replacements = [
            # 보험 — COT 맥락에서 형태 불문 차단
            (r"['\"]?보험['\"]?\s*(을|을\s*들|에\s*가입|을\s*구매|을\s*확보|을\s*든|성|용|처럼)", "숏 포지션 보유"),
            (r"보험(을\s*들고\s*있|을\s*들|에\s*가입하|을\s*구매하|을\s*확보하)[^\s]*", "숏 포지션을 유지"),

            # 극단적 — 과장 수식어
            (r"극단적(인|으로)\s*(과매수|과열|이탈|구간|상황|반응)", "통계적 상단 이탈"),
            (r"역대급", "이례적인"),

            # FOMO/포모 — 행위자 서술
            (r"포모\s*\(FOMO\)[^\s,\.]*", "추세 추종"),
            (r"FOMO\s*(성|형|제대로|심리)", "추세 추종"),
            (r"개미|세력|진짜\s*고수|스마트\s*머니", "시장 참여자"),

            # 외국인 자금 유입 — 단정적 표현 차단
            (r"외국인\s*(자금|수급)\s*(유입|가속|증가|확대)", "시장 수급 변화"),

            # 기관 의도 해석 — SPECULATION (Task 1 & 2 통합)
            (r"기관(들?이?)\s*(하락을\s*예상|보험을|방어적으로|선제적으로|대응하려)", "기관 포지션 변화"),
            (r"헤지\s*오버레이\s*전략을\s*가동", "숏 포지션 증가"),
            (r"포트폴리오\s*헤지로\s*해석", "포지션 변화 관측"),

            # 의문문 형태 — 핵심 금지 단어 및 특정 수급 맥락(의도/심리) 포함 시 우회 차단
            (r"(보험|역대급|걸까요|까요)[^\?\.]*\?", "관련 지표의 변화가 관측됩니다."),
            (r"(포지션|헤지|세력|기관|외국인|수급|베팅)[^\?\.]*(의도|심리)[^\?\.]*\?", "관찰된 포지션의 변화입니다."),
            (r"의문문\?|걸까요\?|까요\?", "."), 
            
            # 기타 과잉 해석 문장 차단
            (r"(유동성\s*유입\s*가속화|가속화|유동성\s*자산\s*유입|자금\s*쏠림)", "수급 지표의 변화 관측"),
            (r"(강제\s*청산\s*압력|청산\s*구간\s*진입|청산\s*유발)", "포지션 변동 가능성 상존"),
            (r"(순환\s*고리\s*형성|악순환|선순환|순환\s*구조)", "지표 간 동조화 현상"),
            (r"(접근\s*유도|접근을\s*강요|지점에\s*도달)", "변동성 확대 구간 진입")
        ]

        for pattern, repl in replacements:
            text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
        return text

    def save_scripts(self, long_script, short_script):
        (self.script_dir / "today_script_long.md").write_text(long_script, encoding="utf-8")
        (self.script_dir / "today_script_short.md").write_text(short_script, encoding="utf-8")
        print(f"  스크립트 저장 완료: {self.script_dir}")

    def run(self, analyst_results=None):
        print(f"\n✍️ AGENT-05 WRITER 시작 [{self.today}]")
        context = self.load_data()
        if not context:
            print("  필요한 분석 데이터가 없습니다.")
            return {"status": "FAIL", "reason": "No context"}

        long_script = self.generate_long(context)
        short_script = self.generate_shorts(context)
        self.save_scripts(long_script, short_script)
        
        # ⚠️ 임시: [FALLBACK] 키워드로 감지 (정밀화 필요 시 플래그 전달 체인 구축)
        is_fallback = "[FALLBACK]" in long_script or "분석 데이터 품질 미달" in long_script
        
        print("✅ AGENT-05 완료\n")
        return {
            "status": "SUCCESS",
            "long_script_path": str(self.script_dir / "today_script_long.md"),
            "short_script_path": str(self.script_dir / "today_script_short.md"),
            "fallback_used": is_fallback,
            "topic_core_claim": context.get("analysis", {}).get("topic_core_claim", ""),
            "why_now": context.get("analysis", {}).get("why_now", ""),
            "one_line_summary": context.get("analysis", {}).get("one_line_summary", "")
        }


if __name__ == "__main__":
    agent = WriterAgent()
    agent.run()
