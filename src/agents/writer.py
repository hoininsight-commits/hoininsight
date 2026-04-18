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
        raw_data = {
            "market_summary": "", 
            "cot_summary": "", 
            "consensus_summary": "",
            "dart_companies": []
        }
        
        m_path = self.raw_dir / "market.json"
        c_path = self.raw_dir / "cot.json"
        cs_path = self.raw_dir / "consensus.json"
        d_path = self.raw_dir / "dart.json"

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

        if d_path.exists():
            d = json.loads(d_path.read_text())
            disclosures = d.get("data", {}).get("disclosures", [])
            raw_data["dart_companies"] = list(set([item.get("company") for item in disclosures]))
            
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
        market_state = analysis.get("market_state", {})
        
        prompt = f"""
너는 경제사냥꾼 유튜브 채널의 메인 작가다.
아래 분석 데이터를 기반으로 경제사냥꾼의 '7단계 스토리 빌드업'을 완벽히 재현한 스크립트를 작성해라.

[절대 금지]
- 제공된 [오늘의 분석 데이터] 및 [원본 통계 데이터]에 없는 수치, 사실, 현상을 창작하거나 추론하여 삽입하는 것을 엄격히 금지한다.
- 데이터로 설명되지 않는 내용은 반드시 "~로 해석될 수 있다", "~가능성이 있다" 등 추론임을 명시하는 표현을 사용하며, 이를 사실인 것처럼 단정 짓지 마라.

[시장 상태 판단 기반 서사 제약] (CRITICAL)
- 현재 시장 상태: {json.dumps(market_state, ensure_ascii=False)}
- **Risk Appetite: 상승**일 경우: "붕괴", "공포", "대탈출", "폭풍 전야" 등 공포를 조장하는 과격한 서사 절대 금지.
- 대신 "낙관 속 불안", "헤지 강화", "리스크 관리 가동" 관점에서 서술해라.
- COT 숏 포지션은 하락 확신이 아닌 "롱 포지션에 대한 보험(Hedge)" 가능성을 반드시 언급해라.

[종목 추천 절대 금지 조건]
- dart.json(아래 dart_companies 리스트)에 포함되지 않은 종목은 절대 언급하지 않는다.
- 유효한 종목 데이터가 전혀 없다면, "관련 섹터 ETF 흐름 주시"로 서술한다.

[오늘의 분석 데이터]
토픽: {signal.get("topic", "")}
강도: {signal.get("strength", 0)} / 10
기대 vs 현실: {json.dumps(analysis.get("expectation_vs_reality", {}), ensure_ascii=False)}
인과관계 체인: {level2}
유사 사례: {json.dumps(analysis.get("historical_reference", {}), ensure_ascii=False)}
관련 종목: {stocks_text}

[원본 통계 데이터 요약 (Evidence)]
{json.dumps(self.load_raw_data(), ensure_ascii=False, indent=2)}

[출력 조건]
- 반드시 7단계 구조(Hook~Risk)를 명확히 구분하여 작성할 것.
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

        market_state = analysis.get("market_state", {})

        prompt = f"""
너는 경제사냥꾼 유튜브 채널의 쇼츠 스크립트 작가다.
아래 분석 데이터와 원본 데이터를 기반으로 60초 분량(약 400~600자)의 '7단계 압축 스크립트'를 작성해라.

[절대 규칙]
- 현재 시장 상태: {json.dumps(market_state, ensure_ascii=False)}
- Risk Appetite 상승 시 "붕괴/대탈출" 표현 금지. "낙관 속 불안/헤지 대응" 위주로 서술.
- 60초 분량(400~600자)을 유지하고 경제사냥꾼의 거친 반말 어조를 사용해라.

[토픽]
{signal.get("topic", "")}

[분석 데이터]
{json.dumps(analysis, ensure_ascii=False)}

[원본 통계 데이터 요약 (Evidence)]
{json.dumps(self.load_raw_data(), ensure_ascii=False)}

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

        # 분석 데이터에서 시장 상태 로드 (직접 analysis에서 가져오거나 파일 재로드)
        analysis_path = self.analysis_dir / "today_analysis.json"
        market_state_block = ""
        if analysis_path.exists():
            try:
                analysis = json.loads(analysis_path.read_text())
                ms = analysis.get("market_state", {})
                if ms:
                    market_state_block = f"""[시장 상태 판단]
Risk Appetite: {ms.get('risk_appetite')}
Hedging Activity: {ms.get('hedging_activity')}
Directional Conviction: {ms.get('conviction')}
→ 종합: {ms.get('summary')}
"""
            except:
                pass

        # 데이터 근거 추출
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

{market_state_block}
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
