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

        # 프롬프트 데이터 준비
        prompt = WRITER_PROMPT_TEMPLATE.format(
            stocks_json=json.dumps(context.get("stocks_data", {}).get("stocks", []), ensure_ascii=False),
            cot_summary_detailed=json.dumps(context.get("analysis", {}).get("expectation_vs_reality", {}), ensure_ascii=False),
            kospi_foreign_net=context.get("analysis", {}).get("market_state", {}).get("kospi_foreign_net", "0.00"),
            topic=context.get("signal", {}).get("topic"),
            analysis_json=json.dumps(context.get("analysis", {}).get("level2_chain", []), ensure_ascii=False),
            market_state_json=json.dumps(context.get("analysis", {}).get("market_state", {}), ensure_ascii=False),
            today=self.today
        )

        response = self.gemini.call(prompt, max_tokens=3500)
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

        response = self.gemini.call(prompt, max_tokens=3000)
        
        print(f"  [COMPLETION_TRACE] Shorts Response Status: {'COMPLETED' if '(5단계:' in response else 'TRUNCATED'}")
        
        return self._censor_narrative(response)

    def _censor_narrative(self, text: str) -> str:
        """생성된 스크립트에서 SPECULATION 차단 및 태그 제거 (Hardened #051)"""
        if not text:
            return text
            
        # 1. SPECULATION [S] 라인 전면 삭제 (Task 2)
        lines = text.split("\n")
        filtered_lines = []
        for line in lines:
            if "[S]" in line:
                # [S] 태그가 포함된 라인은 자산/심리/의도 등의 추측이므로 제거
                continue
            filtered_lines.append(line)
        text = "\n".join(filtered_lines)

        # 2. 태그 제거 ([F], [I] 제거하여 최종 사용자용으로 변환)
        text = re.sub(r"\[F\]\s*", "", text)
        text = re.sub(r"\[I\]\s*", "", text)

        # 3. 추가적인 하드코딩된 단정적 추측 차단 (Task 2 & 3 보완)
        replacements = [
            (r"(기관|외국인|외인|진짜\s*고수|스마트\s*머니|개미|세력)들이?\s*(매수|매도|몰려|지탱|대응|움직임|의도|조율|조성)", "수급 변화가"),
            (r"상승분을\s*(지키기|관리|보호하기)\s*위한", "가격-수급 디커플링 구간의"),
            (r"보험(성|용)?\s*(헤지|가입|구축)", "숏 포지션 대응"),
            (r"완벽한\s*(골디락스|상황|타이밍|조건)", r"\1"),
            (r"역대급", "이례적인"),
            (r"포모\(FOMO\)[^\s]*", "추세 추종"),
            (r"의문문\?|걸까요\?|까요\?", "."), 
            (r"['\"]?보험['\"]?을\s*들고\s*있다", "[숏 포지션 유지]"),
            (r"유입\s*환경\s*조성", "유입 환경 탐색"),
            
            # 과잉 해석 문장 차단 (해석형으로 하향)
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

    def run(self):
        print(f"\n✍️ AGENT-05 WRITER 시작 [{self.today}]")
        context = self.load_data()
        if not context:
            print("  필요한 분석 데이터가 없습니다.")
            return

        long_script = self.generate_long(context)
        short_script = self.generate_shorts(context)
        self.save_scripts(long_script, short_script)
        print("✅ AGENT-05 완료\n")


if __name__ == "__main__":
    agent = WriterAgent()
    agent.run()
