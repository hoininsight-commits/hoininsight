# src/agents/writer.py
# AGENT-05 WRITER
# 역할: 경제사냥꾼 스타일 스크립트 자동 생성

import json
from datetime import datetime
from pathlib import Path
from src.core.gemini_client import GeminiClient
from src.prompts.writer_prompt import WRITER_PROMPT_TEMPLATE


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
        prompt = WRITER_PROMPT_TEMPLATE.format(
            stocks_json=stocks_text,
            cot_summary_detailed=raw_data.get("cot_summary", "COT 데이터 없음"),
            kospi_foreign_net=kospi_foreign_net,
            topic=signal.get("topic", ""),
            analysis_json=json.dumps(analysis, ensure_ascii=False),
            market_state_json=json.dumps(market_state, ensure_ascii=False),
        )

        return self._censor_narrative(self.gemini.call(prompt, max_tokens=3000))

    def generate_shorts(self, signal: dict, analysis: dict, stocks: dict) -> str:
        """쇼츠 스크립트 생성 (1~2분 분량)"""
        print("  쇼츠 스크립트 생성 중...")

        market_state = analysis.get("market_state", {})
        raw_data = self.load_raw_data()
        kospi_foreign_net = self._load_kospi_foreign_net()
        stocks_text = json.dumps(stocks.get("stocks", [])[:3], ensure_ascii=False, indent=2)

        # 쇼츠용 분석 데이터 압축 (full JSON 대신 핵심만 전달 → truncation 방지)
        shorts_analysis = {
            "topic": signal.get("topic", ""),
            "market_state": market_state,
            "why_now": analysis.get("why_now", ""),
            "level2_chain": signal.get("level2_chain", []),
            "key_indicators": signal.get("key_indicators", []),
        }

        # Task 2 & 4: WRITER_PROMPT_TEMPLATE를 쇼츠용으로 커스텀하여 적용
        base_rules = WRITER_PROMPT_TEMPLATE.format(
            stocks_json=stocks_text,
            cot_summary_detailed=raw_data.get("cot_summary", "COT 데이터 없음"),
            kospi_foreign_net=kospi_foreign_net,
            topic=signal.get("topic", ""),
            analysis_json=json.dumps(shorts_analysis, ensure_ascii=False),
            market_state_json=json.dumps(market_state, ensure_ascii=False),
        )

        prompt = f"""
{base_rules}

---
[쇼츠 전용 추가 지시 (CRITICAL)]
- **반드시 5단계 구조만 사용해라.** (6~7단계 절대엄금, Task 4-HOTFIX)
- 각 단계는 150자 이내로 압축해라.
- 60초 분량(약 400~600자)의 스크립트 완주가 최우선이다.
- 출력 형식:

(1단계: 후킹)
(2단계: 현상 분석)
(3단계: 통계적 근거)
(4단계: 기관의 움직임)
(5단계: 결론 및 행동 지침)

[제목]
(강렬한 제목 1개)
"""
        # max_tokens 2800으로 증가
        return self._censor_narrative(self.gemini.call(prompt, max_tokens=2800))

    def _censor_narrative(self, text: str) -> str:
        """생성된 스크립트에서 금지 표현을 코드 레벨로 차단 (후처리 검열 레이어)"""
        import re

        # 핵심 동사/명사 단위로 패턴 확장 (Task 3-HOTFIX)
        replacements = [
            # "보험" 관련 — COT 의도 해석이므로 형태 불문 차단. '성/용' 등 접미사 포함.
            (r"['\"]?보험['\"]?([성용]에?|을|으로|이)?\s*(들고\s*있는\s*걸까요[?？]?|들고\s*있다|가입했?다|든\s*이유|들기\s*시작했?다?|구매|확보|헤지|전략|적금)?", "[숏 포지션 대응]"),
            (r"['\"]?보험['\"]?([성용]에?|을|으로|이)\s*들", "[숏 포지션 유지]"),
            (r"['\"]?보험['\"]?([성용]에?|을|으로|이)\s*가입", "[숏 포지션 구축]"),
            (r"['\"]?보험['\"]?([성용]에?|을|으로|이)", "[헤지]"),
            
            # "극단적" — 단독 수식어로 쓰인 경우
            (r"극단적인\s*(과매수|과열|이탈|구간)", "통계적 상단 이탈"),
            (r"극단적인\s*(숏|롱|포지션)", r"\1"),

            # FOMO 관련 — 명사/동사 결합 차단
            (r"포모\(FOMO\)[^\s]*\s*(매수세|자금|심리)", "수급 변화"),
            (r"FOMO\s*(제대로|성|형)", ""),
            (r"포모\(FOMO\)", ""),

            # 외국인 자금 유입 — kospi_foreign_net 조건 없이 일단 차단
            (r"외국인\s*자금\s*(유입|가속|증가)", "수급 변화"),
            (r"외국인\s*(순매수|자금\s*유입\s*가속화?)", "수급"),

            # 기관 의도 해석
            (r"(헤지\s*오버레이\s*전략을\s*가동|포트폴리오\s*헤지로\s*해석)", "숏 포지션 대응 중"),

            # 기존 규칙 유지 및 보강
            (r"역대급\s*규모의?", ""),
            (r"역대급", ""),
            (r"미친\s*듯이", "급격히"),
            (r"정면\s*충돌", "충돌"),
            (r"완벽한\s*(골디락스|상황|타이밍|조건)", r"\1"),
            (r"진짜\s*고수", "기관"),
            (r"스마트\s*머니", "기관 수급"),
            (r"개인\s*(자금|투자자들이|들이)\s*(매수|매도|몰려)", "수급 변화가"),
            (r"모멘텀\s*자금", "수급"),
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
        shorts = self.generate_shorts(signal, analysis, stocks)

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
