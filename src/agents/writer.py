# src/agents/writer.py
# AGENT-05 WRITER
# 역할: 경제사냥꾼 스타일 스크립트 자동 생성

import json
from datetime import datetime
from pathlib import Path
from src.core.gemini_client import GeminiClient
from src.prompts.writer_prompt import WRITER_PROMPT_TEMPLATE


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

    def _load_kospi_foreign_net(self) -> str:
        """market.json에서 kospi_foreign_net 로드"""
        market_path = self.raw_dir / "market.json"
        if market_path.exists():
            try:
                m = json.loads(market_path.read_text())
                return str(m.get("data", {}).get("kospi_foreign_net", "0.0"))
            except Exception:
                pass
        return "0.0"

    def generate_longform(self, signal: dict, analysis: dict, stocks: dict) -> str:
        """롱폼 스크립트 생성 (15~20분 분량) — writer_prompt.py 연결됨"""
        print("  롱폼 스크립트 생성 중... [writer_prompt.py WRITER_PROMPT_TEMPLATE 적용]")

        raw_data = self.load_raw_data()
        kospi_foreign_net = self._load_kospi_foreign_net()
        level2 = "\n".join(signal.get("level2_chain", []))
        market_state = analysis.get("market_state", {})
        stocks_text = json.dumps(stocks.get("stocks", [])[:3], ensure_ascii=False, indent=2)

        # WRITER_PROMPT_TEMPLATE 채우기 (writer_prompt.py 규칙 전달)
        base_rules = WRITER_PROMPT_TEMPLATE.format(
            stocks_json=stocks_text,
            cot_summary_detailed=raw_data.get("cot_summary", "COT 데이터 없음"),
            kospi_foreign_net=kospi_foreign_net,
            topic=signal.get("topic", ""),
            analysis_json=json.dumps(analysis, ensure_ascii=False),
            market_state_json=json.dumps(market_state, ensure_ascii=False),
        )

        prompt = f"""
{base_rules}

---
[추가 데이터 근거 (Evidence)]
{raw_data.get("market_summary", "")}

[인과관계 체인 (level2_chain)]
{level2}

[추가 분석]
강도: {signal.get("strength", 0)} / 10
기대 vs 현실: {json.dumps(analysis.get("expectation_vs_reality", {}), ensure_ascii=False)}
유사 사례: {json.dumps(analysis.get("historical_reference", {}), ensure_ascii=False)}

[절대 금지]
- 위 데이터에 없는 수치·사실·현상을 창작 또는 추론하여 삽입 금지.
- 데이터로 설명 불가한 내용은 "~로 해석될 수 있다", "~가능성이 있다" 등 추론임을 명시할 것.

[시장 상태 서사 제약] (CRITICAL)
- Risk Appetite 상승 시: "붕괴/공포/대탈출/폭풍 전야" 서사 절대 금지.
- 대신 "낙관 속 불안/헤지 강화/리스크 관리 가동"으로 서술.
- COT 숏 포지션 = 하락 확신이 아닌 "롱 포지션 헤지" 가능성 병기 필수.
"""
        return self._censor_narrative(self.gemini.call(prompt, max_tokens=3000))

    def generate_shorts(self, signal: dict, analysis: dict) -> str:
        """쇼츠 스크립트 생성 (1~2분 분량)"""
        print("  쇼츠 스크립트 생성 중...")

        market_state = analysis.get("market_state", {})
        raw_data = self.load_raw_data()

        # 쇼츠용 분석 데이터 압축 (full JSON 대신 핵심만 전달 → truncation 방지)
        shorts_analysis = {
            "topic": signal.get("topic", ""),
            "market_state": market_state,
            "why_now": analysis.get("why_now", ""),
            "level2_chain": signal.get("level2_chain", []),
            "key_indicators": signal.get("key_indicators", []),
        }

        prompt = f"""
너는 경제사냥꾼 유튜브 채널의 쇼츠 스크립트 작가다.
아래 분석 데이터를 기반으로 60초 분량(약 400~600자)의 '5단계 압축 스크립트'를 완주해라.

[금지 표현 — 절대 사용 금지]
- "역대급", "미친 듯이", "보험을 들", "'보험'", "FOMO성", "포모(FOMO)", "외국인 자금 유입"
- "개인 자금", "개미들", "모멘텀 자금", "극단적인 과매수", "스마트 머니"
- Risk Appetite 상승 시: "붕괴/대탈출/공포" 표현 금지

[시장 상태]
{json.dumps(market_state, ensure_ascii=False)}

[토픽 및 핵심 데이터]
토픽: {signal.get("topic", "")}
{json.dumps(shorts_analysis, ensure_ascii=False)}

[원본 통계 (Evidence)]
{raw_data.get("market_summary", "")}
{raw_data.get("cot_summary", "")}

출력 형식 (반드시 5단계 모두 완주):
[쇼츠 스크립트]

(1단계: 후킹)
(내용)

(2단계: 현상 분석)
(내용)

(3단계: 통계적 근거)
(내용)

(4단계: 기관의 움직임)
(내용)

(5단계: 결론 및 행동 지침)
(내용)

[제목]
(제목 1개)
"""
        # max_tokens 2000으로 증가 (1500 → 2000, truncation 방지 Task 4)
        return self._censor_narrative(self.gemini.call(prompt, max_tokens=2000))

    def _censor_narrative(self, text: str) -> str:
        """생성된 스크립트에서 금지 표현을 코드 레벨로 차단 (후처리 검열 레이어)"""
        import re

        # 단순 대체 규칙: (패턴, 대체문)
        # 넓은 패턴을 먼저 배치 (의문문·따옴표·부정문 형태 모두 포함)
        replacements = [
            # 역대급
            (r"역대급\s*['\"]?보험['\"]?", "Net 숏 포지션"),
            (r"역대급\s*규모의?\s*숏\s*포지션", "숏 포지션"),
            (r"역대급\s*규모의?", ""),
            (r"역대급", ""),
            # 미친/정면/완벽
            (r"미친\s*듯이", "급격히"),
            (r"정면\s*충돌", "충돌"),
            (r"완벽한\s*(골디락스|상황|타이밍|조건)", r"\1"),
            # 보험 — 의문문·따옴표·모든 활용형 포함 (확장, Task 3)
            (r"['\"]?보험['\"]?\s*을\s*(들고\s*있는\s*걸까요[?？]?|들고\s*있다|가입했?다|든\s*이유|들기\s*시작했?다?|구매|확보)", "숏 포지션을 유지하고 있다"),
            (r"['\"]?보험['\"]?\s*을\s*들", "숏 포지션을 유지"),
            (r"['\"]?보험['\"]?\s*으로\s*(꽉꽉\s*)?채워", "숏 포지션으로 대응"),
            (r"['\"]?보험['\"]?\s*을\s*가입", "숏 포지션 구축"),
            # 극단적인 (과매수/과열/이탈 등, Task 3)
            (r"극단적인\s*(과매수|과열|이탈|구간)", "통계적 상단 이탈"),
            (r"극단적인\s*(숏|롱|포지션)", r"\1"),
            # FOMO/포모 — 행위자 서술 형태 포함 (Task 3)
            (r"포모\(FOMO\)[^\s]*?\s*(매수세|자금|심리)", "수급 유입"),
            (r"FOMO\s*(제대로|성|형)", ""),
            (r"포모\(FOMO\)", ""),
            (r"FOMO성\s*매수세", "수급 유입"),
            # 외국인 자금 유입 (kospi_foreign_net 조건 무관 일괄 차단, Task 3)
            (r"외국인\s*자금\s*(유입|가속|증가)", ""),
            (r"외국인\s*(순매수|자금\s*유입\s*가속화?)", ""),
            # 기관 의도 해석 (Task 3)
            (r"헤지\s*오버레이\s*전략을\s*가동", "숏 포지션 보유 중"),
            (r"포트폴리오\s*헤지로\s*해석", "숏 포지션 보유 중"),
            # 스마트머니/진짜고수
            (r"진짜\s*고수", "기관"),
            (r"스마트\s*머니들이\s*\S+", "포지션 변화가 관찰된다"),
            (r"실체를\s*파헤쳐", "데이터를 분석해"),
            # 강력한 방향성
            (r"강력한\s*(하락\s*베팅|매수|매도|신호)", r"\1"),
            # 개인 행위자
            (r"개인\s*(자금|투자자들이|들이)\s*(매수|매도|몰려)", "수급 변화가"),
            (r"모멘텀\s*자금\s*(매수세?|유입)", "수급 유입"),
            (r"개미(들?이?)\s*(몰려|매수|매도)", "수급 변화가"),
        ]

        for pattern, repl in replacements:
            text = re.sub(pattern, repl, text, flags=re.UNICODE)

        return text

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
