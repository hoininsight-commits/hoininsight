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

[분석 요구사항]
1. three_lens_analysis: 돈의흐름/구조적변화/정책방향 각각 한 문장
2. level2_chain: 인과관계 체인 3~5단계 (경제사냥꾼 스타일로 구체적으로)
3. historical_reference: 과거 유사 사례 1개
4. risk_factors: 리스크 정확히 3개
5. check_points: 투자 체크포인트 정확히 2개

[출력 JSON 구조]
{{
  "date": "{self.today}",
  "topic": "{signal['topic']}",
  "three_lens_analysis": {{
    "money_flow": "돈의 흐름 분석 한 문장",
    "structural_change": "구조적 변화 분석 한 문장",
    "policy_direction": "정책 방향 분석 한 문장"
  }},
  "level2_chain": ["원인1", "원인2", "결과1", "결과2", "투자 임팩트"],
  "historical_reference": {{
    "case": "과거 사례명",
    "similarity": "유사한 이유",
    "outcome": "그때 결과"
  }},
  "risk_factors": ["리스크1", "리스크2", "리스크3"],
  "check_points": ["체크포인트1", "체크포인트2"]
}}
"""
        result = self.claude.call_json(prompt, max_tokens=2000)

        # level2_chain을 today_signal.json에도 업데이트
        signal["level2_chain"] = result.get("level2_chain", [])
        signal_path = self.signal_dir / "today_signal.json"
        signal_path.write_text(json.dumps(signal, ensure_ascii=False, indent=2))

        return result

    def map_stocks(self, signal, analysis):
        """관련 종목 매핑"""
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
