import json
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
        """유튜브 롱폼 스크립트 생성 (writer_prompt.py 통합)"""
        print("  롱폼 스크립트 생성 중... [writer_prompt.py WRITER_PROMPT_TEMPLATE 적용]")

        prompt = f"""
{WRITER_PROMPT_TEMPLATE}

너는 경제사냥꾼 유튜브 채널의 메인 작가다. 아래 분석 데이터를 바탕으로 7단계 스토리 빌드업을 완벽히 재현한 스크립트를 작성해라.

---

### [분석 데이터]
{json.dumps(context, ensure_ascii=False, indent=2)}

### [출력 형식 (Markdown)]
# HOIN Insight 스크립트
날짜: {self.today}
토픽: {context.get('signal', {}).get('topic')}
강도: {context.get('signal', {}).get('strength')}
유형: 롱폼

[시장 상태 판단]
...

[사용된 데이터 근거]
...

---

## [유튜브 제목]
(3가지 제안)

## [썸네일 구성]
...

---

## [스크립트]
(Step 1: Hook)
...
(Step 7: Risk)
...
"""
        # [TRACE] writer_prompt.py 로드 확인 (Task 3)
        print(f"  [PROMPT_TRACE] WRITER_PROMPT_TEMPLATE 로드 성공 (chars: {len(WRITER_PROMPT_TEMPLATE)})")
        
        # [TRACE] Gemini 호출 직전 프롬프트 샘플 (Task 3-REWORK)
        prompt_sample = prompt.replace("\n", " ")[:300]
        print(f"  [PROMPT_TRACE] Full Prompt Sample (first 300 chars): {prompt_sample}...")

        response = self.gemini.call(prompt, max_tokens=3500)
        return self._censor_narrative(response)

    def generate_shorts(self, context):
        """유튜브 쇼츠 스크립트 생성 (writer_prompt.py 통합 + Truncation 방지)"""
        print("  쇼츠 스크립트 생성 중...")

        shorts_analysis = {
            "topic": context.get("signal", {}).get("topic"),
            "level2_chain": context.get("analysis", {}).get("level2_chain", []),
            "market_state": context.get("analysis", {}).get("market_state", {}),
            "stocks": [s["name"] for s in context.get("stocks_data", {}).get("stocks", [])]
        }

        # [TRACE] writer_prompt.py 규칙을 쇼츠에도 통합 (Task 3)
        prompt = f"""
{WRITER_PROMPT_TEMPLATE}

너는 경제사냥꾼 채널의 쇼츠 작가다. 위 [절대 규칙]을 반드시 준수하여 아래 분석 데이터를 바탕으로 5단계 스크립트를 작성해라.

[분석 데이터]
{json.dumps(shorts_analysis, ensure_ascii=False)}

[출력 형식]
(1단계: 후킹)
...
(5단계: 결론)

[제목]
(강렬한 제목 1개)
"""
        # [TRACE] 쇼츠 전용 5단계 구조 + WRITER_PROMPT_TEMPLATE 통합 (Task 3)
        print(f"  [PROMPT_TRACE] 쇼츠용 WRITER_PROMPT 통합 완료 (chars: {len(prompt)})")

        response = self.gemini.call(prompt, max_tokens=3000)
        
        # [TRACE] 쇼츠 응답 완료 상태 및 길이 확인 (Task 5 & #050-REWORK 보완)
        print(f"  [COMPLETION_TRACE] Shorts Response Length: {len(response)} chars")
        print(f"  [COMPLETION_TRACE] Last Stage Check: {'(5단계:' in response}")
        print(f"  [COMPLETION_TRACE] Response Status: {'COMPLETED' if '(5단계:' in response else 'TRUNCATED'}")
        
        return self._censor_narrative(response)

    def _censor_narrative(self, text: str) -> str:
        """생성된 스크립트에서 금지 표현 및 과잉 해석 팩트 중심 치환 (Hardened v6.0)"""
        if not text:
            return text
            
        import re
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
            
            # [Task 3-REWORK] 과잉 해석 문장 차단
            (r"(유동성\s*유입\s*가속화|가속화|유동성\s*자산\s*유입|자금\s*쏠림)", "수급 지표의 변화 관측"),
            (r"(강제\s*청산\s*압력|청산\s*구간\s*진입|청산\s*유발)", "포지션 변동 가능성 상존"),
            (r"(순환\s*고리\s*형성|악순환|선순환|순환\s*구조)", "지표 간 동조화 현상"),
            (r"(접근\s*유도|접근을\s*강요|지점에\s*도달)", "변동성 확대 구간 진입"),
            (r"(작용하며|기여|작용하여|이바지)", "동시에 관측됨"),
            (r"(유도|확장|견인|압력을\s*가하며)", "동반 변화가 관측됨"),
            (r"(조성|마련|환경\s*조성|구축)", "현상 관측")
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
