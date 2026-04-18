# src/agents/writer.py
# AGENT-05 WRITER
# 역할: 경제사냥꾼 스타일 스크립트 자동 생성

import json
from datetime import datetime
from pathlib import Path
from src.core.gemini_client import GeminiClient


# 경제사냥꾼 스크립트 생성 규칙
SCRIPT_RULES = """
[진성 경제사냥꾼 v8.0 집필 규칙 — Soul Alignment]

1. **사냥꾼의 화법 (Hunter's Vernacular)**:
   - "안녕하세요" 대신 **"님들, 지금 이 날짜 꼭 기억해 둬야 해"** 또는 **"진짜 충격적인 사실 하나 알려줄까?"**로 시작할 것.
   - 문장 사이사이에 **"이면을 봐야 해", "이게 뭘 의미하냐면...", "진짜 싸움은 여기서부터거든"**을 적절히 배치.
   - AI 특유의 "~할 것으로 예상됩니다"를 금지하고, **"결국 이건 ~라는 뜻이야", "~될 수밖에 없어"**와 같은 확신에 찬 어조 사용.

2. **7단계 실전 빌드업 (YouTube Style)**:
   - **Hook**: 시장의 상식을 깨는 질문 (예: "금리가 오르는데 주가는 왜 갈까?")
   - **물리적 병목 (New)**: 지표 뒤의 '물, 전기, 해협' 등 실질적 제약 사항 언급.
   - **돈의 흐름**: 권력과 자본이 어디로 향하는지 선명하게 기술.
   - **사냥꾼의 결론**: 남들이 보지 못하는 이면의 수혜자/리스크 지목.

3. **화법 상세**:
   - 반말 (님들, ~야, ~거든, ~잖아) 사용 필수.
   - 비유: 추상적 개념은 '내 주머니 사정'이나 '아파트 가격' 등으로 비유.
   - "사냥꾼인 내가 밤새 데이터 뜯어서 가져왔으니까 딱 집중해" 톤 유지.
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
        self.gemini = GeminiClient()
        self.raw_dir = Path(f"data/raw/{self.today}")

    def load_raw_data(self) -> dict:
        """오늘의 원천 데이터 로드 및 요약 (프롬프트 비대화 방지)"""
        raw_data = {"market_summary": "", "cot_summary": "", "consensus_summary": ""}
        
        m_path = self.raw_dir / "market.json"
        c_path = self.raw_dir / "cot.json"
        cs_path = self.raw_dir / "consensus.json"

        if m_path.exists():
            m = json.loads(m_path.read_text())
            stats = m.get("data", {}).get("multi_period_stats", {})
            summary = []
            for k, v in stats.items():
                summary.append(f"{k.upper()}: Z={v.get('z_score_20d')}, 5d_chg={v.get('chg_5d')}%")
            raw_data["market_summary"] = "\n".join(summary)

        if c_path.exists():
            c = json.loads(c_path.read_text())
            summary = []
            for asset, pos in c.get("positions", {}).items():
                summary.append(f"COT {asset}: {pos.get('direction')} ({pos.get('net_change', 0):+,} contracts)")
            raw_data["cot_summary"] = "\n".join(summary)

        if cs_path.exists():
            cs = json.loads(cs_path.read_text())
            summary = []
            for ev in cs.get("major_surprises", []) or []:
                summary.append(f"Event: {ev.get('event')}, Surprise: {ev.get('surprise_pct')}%")
            raw_data["consensus_summary"] = "\n".join(summary)
            
        return raw_data

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

        # 분석 실패 마커 확인
        for d in sorted(Path("data/analysis").iterdir(), reverse=True):
            failure_marker = d / "analysis_failed.txt"
            ap = d / "today_analysis.json"
            if failure_marker.exists() and not ap.exists():
                print(f"  ⚠️ 분석 실패 마커 감지: {failure_marker}")
                return None, None  # None 반환으로 실패 신호
            if ap.exists():
                break

        ap = self.analysis_dir / "today_analysis.json"
        sp = self.analysis_dir / "today_stocks.json"

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

        # 빈 분석 데이터 체크
        if not analysis or analysis == {}:
            print("  ⚠️ 분석 데이터 비어있음")
            return None, None

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
너는 경제사냥꾼 유튜브 채널의 메인 작가다.
아래 분석 데이터를 기반으로 경제사냥꾼의 '7단계 스토리 빌드업'을 완벽히 재현한 스크립트를 작성해라.

[절대 금지]
- 제공된 [오늘의 분석 데이터] 및 [원본 통계 데이터]에 없는 수치, 사실, 현상을 창작하거나 추론하여 삽입하는 것을 엄격히 금지한다.
- 데이터로 설명되지 않는 내용은 반드시 "~로 해석될 수 있다", "~가능성이 있다" 등 추론임을 명시하는 표현을 사용하며, 이를 사실인 것처럼 단정 짓지 마라.
- '물리적 병목' 섹션은 실제 데이터(뉴스, DART, 공시 등)에 관련 내용이 있을 때만 언급하며, 없을 경우 데이터에 기반한 구조적 원인으로 대체한다.

[사용 가능한 데이터 범위]
- COT: 포지션 수치, 변화율, 방향 (Gold, S&P500 등)
- Market: z-score, 변화율, 현재가, Fear & Greed Index
- Consensus: 서프라이즈/쇼크 수치, 지표 발표 결과
- FRED/ECOS: 금리, 지표값
- Sentiment: 뉴스 헤드라인 내용

[오늘의 분석 데이터]
토픽: {signal.get("topic", "")}
강도: {signal.get("strength", 0)} / 10
기대 vs 현실: {json.dumps(analysis.get("expectation_vs_reality", {}), ensure_ascii=False)}
4대 레이어 체크: {json.dumps(analysis.get("four_layer_check", {}), ensure_ascii=False)}
인과관계 체인: {level2}
유사 사례: {json.dumps(analysis.get("historical_reference", {}), ensure_ascii=False)}
관련 종목: {stocks_text}
리스크: {risk_factors}

[원본 통계 데이터 요약 (Evidence)]
{json.dumps(self.load_raw_data(), ensure_ascii=False, indent=2)}

[출력 조건]
- 반드시 7단계 구조(Hook~Risk)를 명확히 구분하여 작성하되, 자연스러운 흐름을 유지할 것.
- 인공지능이 쓴 느낌이 나면 탈락이다. 진짜 사냥꾼이 옆에서 이야기해 주는 느낌을 살려라.
- 'WHY NOW' 부분에 가장 많은 공을 들여야 한다. 실제 데이터의 수치를 최소 2회 이상 언급하며 신뢰도를 높여라.
- 제목 3개와 썸네일 문구(10자 이내)를 마지막에 추가해라.

출력 형식:
[대본 본문]
(스크립트 내용)

[제목 옵션]
1.
2.
3.

[썸네일 문구]
(문구)
"""
        return self.gemini.call(prompt, max_tokens=3000)

    def generate_shorts(self, signal: dict, analysis: dict) -> str:
        """쇼츠 스크립트 생성 (1~2분 분량)"""
        print("  쇼츠 스크립트 생성 중...")

        level2 = " → ".join(signal.get("level2_chain", [])[:3])

        prompt = f"""
너는 경제사냥꾼 유튜브 채널의 쇼츠 스크립트 작가다.
아래 분석 데이터와 원본 데이터를 기반으로 60초 분량(약 400~600자)의 '7단계 압축 스크립트'를 작성해라.

[절대 규칙]
- 롱폼과 마찬가지로 수집된 데이터에 없는 사실 창작을 엄격히 금지한다.
- 아래 7단계를 반드시 포함하며, 단계별 구분 기호(예: 1. Hook)를 본문에 명시하지 말고 자연스럽게 연결해라.

[쇼츠 7단계 압축 구조]
1. Hook: 시장의 모순을 찌르는 강력한 한 문장 (10초)
2. Expectation vs Reality: 대중의 기대와 실제 데이터의 충돌 (10초)
3. Mechanism: 이 현상을 일으킨 핵심 구조적 원인 (5초)
4. WHY NOW: 왜 하필 '오늘' 이 문제가 터졌는가 (실제 데이터 수치 포함, 10초)
5. Implication: 이로 인해 스마트머니는 어디로 이동하는가 (10초)
6. Mentionables: 우리가 주목해야 할 연결 종목이나 섹터 (10초)
7. Risk: 이 시나리오가 틀릴 수 있는 반대 변수 한 문장 (5초)

[토픽]
{signal.get("topic", "")}

[분석 데이터]
{json.dumps(analysis, ensure_ascii=False)}

[원본 통계 데이터 요약 (Evidence)]
{json.dumps(self.load_raw_data(), ensure_ascii=False)}

[출력 조건]
- 분량: 1분 이내 (400~600자 내외)
- 실제 데이터 수치를 최소 1개 이상 반드시 포함할 것.
- 경제사냥꾼의 거칠고 확신에 찬 말길(반말)을 그대로 유지해라.

출력 형식:
[쇼츠 스크립트]
(스크립트 본문)

[제목]
(제목 1개)
"""
        return self.gemini.call(prompt, max_tokens=1500)

    def save_scripts(self, longform: str, shorts: str, signal: dict):
        """스크립트 파일 저장"""
        long_path = self.output_dir / "today_script_long.md"
        short_path = self.output_dir / "today_script_short.md"

        # 데이터 근거 추출 (v3.0 교정)
        summary = self.load_raw_data()
        evidence_lines = []
        if summary["market_summary"]:
            evidence_lines.extend(summary["market_summary"].split("\n")[:3])
        if summary["cot_summary"]:
            evidence_lines.extend(summary["cot_summary"].split("\n")[:2])

        evidence_block = "[사용된 데이터 근거]\n" + "\n".join(evidence_lines) + "\n"

        header = f"""# HOIN Insight 스크립트
날짜: {self.today}
토픽: {signal.get("topic", "")}
강도: {signal.get("strength", 0)}
유형: {signal.get("content_type", "")}
생성: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

{evidence_block}
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

        analysis, stocks = self.load_analysis()

        # 분석 실패 시 중단
        if analysis is None:
            print("  ❌ AGENT-05 중단 — 분석 데이터 없음")
            print("  ANALYST 재실행 필요")
            return {"failed": True, "reason": "analysis_missing"}

        print(f"  토픽: {signal.get('topic', '')}")

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
