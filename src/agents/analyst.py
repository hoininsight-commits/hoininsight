import json
from datetime import datetime
from pathlib import Path
from src.core.claude_client import ClaudeClient
from src.core.sector_map import get_related_sectors, get_stocks_by_sector


class AnalystAgent:

    def __init__(self):
        self.today = datetime.now().strftime("%Y%m%d")
        self.signal_dir = Path(f"data/signals/{self.today}")
        self.raw_dir = Path(f"data/raw/{self.today}")
        self.analysis_dir = Path(f"data/analysis/{self.today}")
        self.analysis_dir.mkdir(parents=True, exist_ok=True)
        self.claude = ClaudeClient()

    def load_signal(self):
        p = self.signal_dir / "today_signal.json"
        if not p.exists():
            return None
        return json.loads(p.read_text())

    def load_raw(self):
        raw = {}
        for name in ["macro", "market", "sentiment"]:
            p = self.raw_dir / f"{name}.json"
            if p.exists():
                raw[name] = json.loads(p.read_text())
        return raw

    def analyze(self, signal, raw_data):
        """Claude API로 레벨2 분석"""
        print("  Claude API 레벨2 분석 중...")

        market = raw_data.get("market", {}).get("data", {})
        macro = raw_data.get("macro", {}).get("data", {})
        history = raw_data.get("history_90d", {}) # v7.0 히스토리 데이터

        prompt = f"""
너는 경제사냥꾼 채널 수준의 거시경제 분석 전문가다.
아래 신호를 분석해서 JSON만 출력해라. 마크다운 없이 순수 JSON만.

[오늘의 신호]
토픽: {signal['topic']}
강도: {signal['strength']}
적중 필터: {', '.join(signal['filters_hit'])}

[수집 데이터]
환율: {market.get('usd_krw', 'N/A')}원
KOSPI 등락: {market.get('kospi_1d_change', 'N/A')}%
VIX: {market.get('vix', 'N/A')}
WTI: ${market.get('wti_oil', 'N/A')}
한국 기준금리: {macro.get('korea_base_rate', 'N/A')}%
미국 기준금리: {macro.get('us_fed_rate', 'N/A')}%

[분석 요구사항 (v8.0 Soul Alignment)]
1. physical_bottleneck_analysis: 지표 뒤의 물리적 실체(에너지 해협, 용수, 전력, 공급망 병목)를 분석할 것. (제20조 준수)
   - 예: "호르무즈 해협의 물리적 통제권이 누구에게 있는가?", "반도체 단지의 용수 확보가 가능한가?"
2. power_structure_analysis: 이 사건의 이면에서 진짜 이득을 보는 권력 주체와 손해를 보는 주체를 명확히 구분할 것.
3. trend_context_check: 90일 시계열 추세 속에서 오늘의 위치 분석 (Article 19 준수).
4. four_layer_check: 금리, 유동성, 정책, 기대치를 물리적 실체와 연결하여 해석.
5. historical_reference: 과거 유사 사례 1개
6. risk_factors: 무효화 조건 또는 반대 시나리오 2~3개

[출력 JSON 구조]
{{
  "date": "{self.today}",
  "topic": "{signal['topic']}",
  "three_lens_analysis": {{
    "money_flow": "...",
    "structural_change": "...",
    "policy_direction": "..."
  }},
  "expectation_vs_reality": {{
    "expectation": "시장 기대치",
    "reality": "실제 발생 사실",
    "conflict_reason": "왜 지금 이것이 모순적인가?"
  }},
  "four_layer_check": {{
    "rates": "...",
    "liquidity": "...",
    "policy": "...",
    "expectation_gap": "..."
  }},
  "level2_chain": ["원인1", "...", "투자 임팩트"],
  "historical_reference": {{ "case": "...", "similarity": "...", "outcome": "..." }},
  "risk_factors": ["리스크/반대시나리오1", "..."]
}}

[90일 추세 요약]
- 환율 90일 평균: {history.get('usd_krw', {}).get('avg_90d', 'N/A')}원 / 고점: {history.get('usd_krw', {}).get('max_90d', 'N/A')}원
- WTI 90일 평균: ${history.get('wti_oil', {}).get('avg_90d', 'N/A')} / 고점: ${history.get('wti_oil', {}).get('max_90d', 'N/A')}
- KOSPI 90일 평균: {history.get('kospi', {}).get('avg_90d', 'N/A')}

순수 JSON만 출력해라.
"""
        result = self.claude.call_json(prompt, max_tokens=2000)

        # level2_chain을 today_signal.json에도 업데이트
        signal["level2_chain"] = result.get("level2_chain", [])
        signal_path = self.signal_dir / "today_signal.json"
        signal_path.write_text(json.dumps(signal, ensure_ascii=False, indent=2))

        return result

    def map_stocks(self, signal, analysis):
        """관련 종목 매핑 (v6.0: MACRO 토픽은 종목보다 시나리오에 집중)"""
        target_type = signal.get("target_type", "MICRO_SECTOR_FOCUS")
        
        # MACRO_GEOPOLITICAL 등 거대 담론은 억지 매핑 지양
        if "MACRO" in target_type:
            print(f"  📢 거대 담론({target_type}) 감지 — 종목보다 거시 시나리오에 집중합니다.")
            return {
                "date": self.today,
                "topic_signal": signal["topic"],
                "stocks": [],
                "target_segments": signal.get("related_keywords", []),
                "is_macro_narrative": True
            }

        print("  종목 매핑 중...")

        keywords = signal.get("related_keywords", [])
        related_sectors = get_related_sectors(keywords)

        stocks = []
        for sector in related_sectors[:3]:
            sector_stocks = get_stocks_by_sector(sector)
            for s in sector_stocks[:2]:
                stocks.append({
                    "ticker": s["ticker"],
                    "name": s["name"],
                    "sector": sector,
                    "impact": "수혜",
                    "reason": f"{signal['topic']}에 따른 {sector} 섹터 영향",
                    "impact_level": "HIGH" if signal["strength"] >= 8.0 else "MEDIUM",
                    "is_primary": True
                })

        # 섹터 맵으로 매핑이 안 된 경우 Claude 활용
        if not stocks:
            print("  섹터 맵 미매칭 — Claude 종목 추론 중...")
            prompt = f"""
토픽: {signal['topic']}
분석: {json.dumps(analysis.get('three_lens_analysis', {}), ensure_ascii=False)}

위 상황에서 영향받는 한국 코스피/코스닥 상장 종목 3개를 골라라.
실제 존재하는 종목만 사용해라.

JSON 배열만 출력 (마크다운 없이):
[
  {{"ticker":"종목코드6자리","name":"종목명","sector":"섹터명","impact":"수혜 또는 피해","reason":"이유 한 문장","impact_level":"HIGH 또는 MEDIUM","is_primary":true}}
]
"""
            result = self.claude.call_json(prompt, max_tokens=800)
            if isinstance(result, list):
                stocks = result

        return {
            "date": self.today,
            "topic_signal": signal["topic"],
            "stocks": stocks
        }

    def save_results(self, analysis, stocks_data):
        (self.analysis_dir / "today_analysis.json").write_text(
            json.dumps(analysis, ensure_ascii=False, indent=2)
        )
        (self.analysis_dir / "today_stocks.json").write_text(
            json.dumps(stocks_data, ensure_ascii=False, indent=2)
        )
        print(f"  저장 완료: {self.analysis_dir}")

    def run(self, detector_result=None):
        print(f"\n🧠 AGENT-04 ANALYST 시작 [{self.today}]")

        signal = self.load_signal()
        if not signal:
            print("  선정된 신호 없음 — AGENT-03 먼저 실행 필요")
            return {}

        print(f"  분석 대상: {signal['topic']}")

        raw_data = self.load_raw()
        analysis = self.analyze(signal, raw_data)
        stocks_data = self.map_stocks(signal, analysis)
        self.save_results(analysis, stocks_data)

        print("✅ AGENT-04 완료\n")
        return {"analysis": analysis, "stocks": stocks_data}


if __name__ == "__main__":
    agent = AnalystAgent()
    agent.run()
