# src/agents/writer.py
# AGENT-05 WRITER
# 역할: 경제사냥꾼 스타일 스크립트 자동 생성

import json
from datetime import datetime
from pathlib import Path
from src.core.claude_client import ClaudeClient


# 경제사냥꾼 스크립트 생성 규칙
SCRIPT_RULES = """
[경제사냥꾼 스타일 규칙]

오프닝 공식:
- "님들, [충격 팩트] 알고 있었어?"
- "다들 [표면 이유]라고 생각하는데 반은 맞고 반은 틀린 이야기야"
- "경제사냥꾼인 내가 싹 다 뜯어왔으니까 딱 집중해 봐"

분석 3렌즈 (반드시 포함):
① 돈의 흐름  ② 구조적 변화  ③ 정책의 방향

레벨2 연결:
- 표면 뉴스 → "근데 진짜 핵심은 지금부터야" → 원인 → 임팩트

비유 규칙:
- 추상 개념은 반드시 일상 비유로 전환
- 숫자는 반드시 체감 단위로 변환 (예: "이게 얼마냐면...")

리스크 병기:
- "물론 맹목적인 낙관은 금물이야"
- 리스크 3개 나열

클로징:
- "정리할게" → 핵심 3줄 → 구독 유도
- 명언 or 투자 원칙으로 마무리

숫자 3의 법칙:
- 원인 3개 / 종목 3개 / 리스크 3개 / 체크포인트 3개

말투:
- 반말 (님들, ~야, ~거든, ~잖아)
- 호칭: "님들", "우리 구독자님들"
- 감탄: "근데 여기서 진짜 핵심이 있어"
"""

# 유형별 길이 기준
CONTENT_TYPES = {
    "롱폼": {"min_words": 2000, "duration": "15~20분"},
    "쇼츠": {"min_words": 400, "duration": "1~2분"},
}


class WriterAgent:

    def __init__(self):
        self.today = datetime.now().strftime("%Y%m%d")
        self.signal_dir = Path(f"data/signals/{self.today}")
        self.analysis_dir = Path(f"data/analysis/{self.today}")
        self.output_dir = Path(f"data/scripts/{self.today}")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.claude = ClaudeClient()

    def load_signal(self) -> dict:
        p = self.signal_dir / "today_signal.json"
        if not p.exists():
            # 이전 날짜에서 찾기
            for d in sorted(Path("data/signals").iterdir(), reverse=True):
                p = d / "today_signal.json"
                if p.exists():
                    print(f"  신호 파일 사용: {p}")
                    break
        if p.exists():
            return json.loads(p.read_text())
        return {}

    def load_analysis(self) -> tuple:
        analysis, stocks = {}, {}
        ap = self.analysis_dir / "today_analysis.json"
        sp = self.analysis_dir / "today_stocks.json"

        # 이전 날짜에서 찾기
        if not ap.exists():
            for d in sorted(Path("data/analysis").iterdir(), reverse=True):
                ap = d / "today_analysis.json"
                sp = d / "today_stocks.json"
                if ap.exists():
                    print(f"  분석 파일 사용: {ap}")
                    break

        if ap.exists():
            analysis = json.loads(ap.read_text())
        if sp.exists():
            stocks = json.loads(sp.read_text())

        return analysis, stocks

    def generate_longform(self, signal: dict, analysis: dict, stocks: dict) -> str:
        """롱폼 스크립트 생성 (15~20분 분량)"""
        print("  롱폼 스크립트 생성 중...")

        stocks_text = json.dumps(
            stocks.get("stocks", [])[:3], ensure_ascii=False
        )
        level2 = "\n".join(signal.get("level2_chain", []))
        risk_factors = "\n".join(
            analysis.get("risk_factors", ["리스크 데이터 없음"])
        )
        check_points = "\n".join(
            analysis.get("check_points", ["체크포인트 없음"])
        )
        historical = analysis.get("historical_reference", {})
        lens = analysis.get("three_lens_analysis", {})

        prompt = f"""
너는 경제사냥꾼 유튜브 채널의 스크립트 작가다.
아래 분석 데이터를 기반으로 경제사냥꾼 스타일의 완성 스크립트를 작성해라.

[스타일 규칙]
{SCRIPT_RULES}

[오늘의 토픽]
{signal.get("topic", "")}

[신호 강도]
{signal.get("strength", 0)} / 10

[레벨2 인과관계 체인]
{level2}

[3렌즈 분석]
돈의 흐름: {lens.get("money_flow", "")}
구조적 변화: {lens.get("structural_change", "")}
정책 방향: {lens.get("policy_direction", "")}

[역사적 유사 사례]
사례: {historical.get("case", "")}
유사성: {historical.get("similarity", "")}
결과: {historical.get("outcome", "")}

[관련 종목]
{stocks_text}

[리스크 요인]
{risk_factors}

[투자 체크포인트]
{check_points}

[출력 조건]
- 분량: 15~20분 분량 (2000자 이상)
- 구조: 오프닝 훅 → 배경 설명 → 레벨2 분석 (3렌즈) → 종목 해설 → 리스크 → 클로징
- 반드시 경제사냥꾼 말투 그대로 재현
- 숫자는 체감 단위로 변환
- 추상 개념은 일상 비유로 전환
- 제목 3개 옵션과 썸네일 문구도 마지막에 추가

출력 형식:
[스크립트]
(스크립트 본문)

[제목 옵션]
1.
2.
3.

[썸네일 문구]
(10자 이내 핵심 문구)
"""
        return self.claude.call(prompt, max_tokens=4000)

    def generate_shorts(self, signal: dict, analysis: dict) -> str:
        """쇼츠 스크립트 생성 (1~2분 분량)"""
        print("  쇼츠 스크립트 생성 중...")

        level2 = " → ".join(signal.get("level2_chain", [])[:3])

        prompt = f"""
너는 경제사냥꾼 유튜브 채널의 쇼츠 스크립트 작가다.
아래 내용으로 1분짜리 쇼츠 스크립트를 작성해라.

[스타일 규칙]
{SCRIPT_RULES}

[토픽]
{signal.get("topic", "")}

[핵심 인과관계]
{level2}

[출력 조건]
- 분량: 1~2분 (400자 내외)
- 구조: 충격 팩트 오프닝 → 핵심 이유 2가지 → 한 줄 결론
- 경제사냥꾼 말투 그대로

출력 형식:
[쇼츠 스크립트]
(스크립트 본문)

[제목]
(제목 1개)
"""
        return self.claude.call(prompt, max_tokens=800)

    def save_scripts(self, longform: str, shorts: str, signal: dict):
        """스크립트 파일 저장"""
        long_path = self.output_dir / "today_script_long.md"
        short_path = self.output_dir / "today_script_short.md"

        header = f"""# HOIN Insight 스크립트
날짜: {self.today}
토픽: {signal.get("topic", "")}
강도: {signal.get("strength", 0)}
유형: {signal.get("content_type", "")}
생성: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

"""
        long_path.write_text(header + longform, encoding="utf-8")
        short_path.write_text(header + shorts, encoding="utf-8")

        print(f"  롱폼 저장: {long_path}")
        print(f"  쇼츠 저장: {short_path}")

    def run(self, analyst_result: dict = None):
        print(f"\n✍️ AGENT-05 WRITER 시작 [{self.today}]")

        signal = self.load_signal()
        if not signal:
            print("  신호 데이터 없음 — 종료")
            return {}

        print(f"  토픽: {signal.get('topic', '')}")
        print(f"  유형: {signal.get('content_type', '')}")

        analysis, stocks = self.load_analysis()

        # 롱폼 생성
        longform = self.generate_longform(signal, analysis, stocks)

        # 쇼츠 생성
        shorts = self.generate_shorts(signal, analysis)

        # 저장
        self.save_scripts(longform, shorts, signal)

        print("✅ AGENT-05 완료\n")
        return {
            "longform_path": str(self.output_dir / "today_script_long.md"),
            "shorts_path": str(self.output_dir / "today_script_short.md"),
        }


if __name__ == "__main__":
    agent = WriterAgent()
    agent.run()
