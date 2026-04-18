import json
from datetime import datetime
from pathlib import Path
from src.core.gemini_client import GeminiClient
from src.core.sector_map import get_related_sectors, get_stocks_by_sector, get_reason_template


class AnalystAgent:

    def __init__(self):
        self.today = datetime.now().strftime("%Y%m%d")
        self.signal_dir = Path(f"data/signals/{self.today}")
        self.raw_dir = Path(f"data/raw/{self.today}")
        self.analysis_dir = Path(f"data/analysis/{self.today}")
        self.analysis_dir.mkdir(parents=True, exist_ok=True)
        self.gemini = GeminiClient()

    def load_signal(self):
        p = self.signal_dir / "today_signal.json"
        if not p.exists():
            return None
        return json.loads(p.read_text())

    def load_raw(self):
        raw = {}
        # collection_status 등 포함 8종 전체 로드 (Task 8)
        raw_files = ["market", "fred", "ecos", "consensus", "cot", "sentiment", "dart", "collection_status"]
        for name in raw_files:
            p = self.raw_dir / f"{name}.json"
            if p.exists():
                raw[name] = json.loads(p.read_text())
        return raw

    def _filter_text(self, text: str, market_data: dict) -> str:
        """텍스트 필드에서 데이터 근거 없는 서술을 팩트 중심 치환 (Hardened v6.0)"""
        if not text:
            return text

        market = market_data.get("market", {}).get("data", {})
        kospi_foreign_net = market.get("kospi_foreign_net", None)
        kospi_inst_net = market.get("kospi_inst_net", None)
        
        # [DATA_CHECK] 수급 데이터 존재 여부 확인 (KR 기준)
        has_kr_foreign_data = kospi_foreign_net is not None and abs(float(kospi_foreign_net)) > 0.001
        has_kr_inst_data = kospi_inst_net is not None and abs(float(kospi_inst_net)) > 0.001

        # 치환 규칙 정의 (Task 1 & 5 & #050-REWORK)
        replacements = [
            # 1. 외국인 수급: 데이터 없을 경우 치환
            {
                "condition": not has_kr_foreign_data,
                "pattern": r"(외국인|외인|foreign)\s*(수급|매수|자금|유입|매도|지탱|대응|움직임|의도)",
                "repl": "시장 수급 변화"
            },
            # 2. 기관 수급: 데이터 없을 경우 치환
            {
                "condition": not has_kr_inst_data,
                "pattern": r"(기관|inst)\s*(수급|매수|자금|유입|매도|지탱|대응|움직임|의도)",
                "repl": "시장 수급 환경"
            },
            # 3. 맹목적 금지어 (데이터 불문)
            {
                "condition": True,
                "pattern": r"(개인투자자|개미|모멘텀\s*자금|군중|세력|투기|포모|FOMO)",
                "repl": "수급"
            },
            {
                "condition": True,
                "pattern": r"(보험성|보험용|보험을\s*들고|보험이|보험\s*가입)",
                "repl": "숏 포지션 대응"
            },
            {
                "condition": True,
                "pattern": r"(완벽한\s*골디락스|완벽한\s*타이밍|완벽한\s*상황)",
                "repl": "우호적인 매크로 환경"
            },
            {
                "condition": True,
                "pattern": r"(안심하고\s*있는|심리가\s*개선|공포가\s*확산|심리를\s*대변|심리가\s*반영)",
                "repl": "변동성 지표의 변화가 관측"
            },
            # [Task 3-REWORK] 과잉 해석 문장 전수 차단
            {
                "condition": True,
                "pattern": r"(유입\s*환경\s*조성|유동성\s*유입\s*가속화|가속화|유동성\s*자산\s*유입)",
                "repl": "수급 지표의 상관관계 관측"
            },
            {
                "condition": True,
                "pattern": r"(강제\s*청산\s*압력|청산\s*유발|강제\s*청산)",
                "repl": "포지션 변동 가능성 상존"
            },
            {
                "condition": True,
                "pattern": r"(순환\s*고리\s*형성|순환\s*구조|악순환)",
                "repl": "지표 간 동조화 현상"
            },
            {
                "condition": True,
                "pattern": r"(접근\s*유도|접근을\s*강요|접근\s*중)",
                "repl": "변동성 확대 구간 진입"
            },
            {
                "condition": True,
                "pattern": r"(유발|유인|밀어올림|상승을\s*강제|상승을\s*유인)",
                "repl": "동반 변화가 관측됨"
            },
            {
                "condition": True,
                "pattern": r"(지탱|지지|방어|하락을\s*방어)",
                "repl": "데이터 지지가 확인됨"
            },
            {
                "condition": True,
                "pattern": r"(작용하며|기여|작용하여|이바지)",
                "repl": "동시에 관측됨"
            },
            {
                "condition": True,
                "pattern": r"(유도|확장|견인|압력을\s*가하며)",
                "repl": "동반 변화가 관측됨"
            },
            {
                "condition": True,
                "pattern": r"(조성|마련|환경\s*조성|구축)",
                "repl": "현상 관측"
            }
        ]

        import re
        for rule in replacements:
            if rule["condition"]:
                text = re.sub(rule["pattern"], rule["repl"], text, flags=re.IGNORECASE)
        return text

    def _filter_level2_chain(self, level2_chain: list, market_data: dict) -> list:
        """level2_chain 항목 필터링 (Task 1)"""
        if not level2_chain:
            return level2_chain
        
        filtered = []
        for item in level2_chain:
            filtered_item = self._filter_text(item, market_data)
            if filtered_item:
                filtered.append(filtered_item)
        return filtered

    def load_existing_analysis(self):
        """기존 today_analysis.json 로드 (Gemini 파싱 실패 시 폴백, Task 5)"""
        p = self.analysis_dir / "today_analysis.json"
        if p.exists():
            try:
                data = json.loads(p.read_text())
                if data and data.get("topic"):
                    return data
            except Exception:
                pass
        return None

    def analyze(self, signal, raw_data):
        """Gemini를 이용한 레벨2 데이터 관계 분석 (Hardened)"""
        print("  Gemini API 레벨2 분석 중...")
        
        prompt = f"""
너는 15년 차 시니어 시장 분석가다. 아래 제공된 Raw Data 간의 통계적 상관관계와 인과적 체인을 분석해라.
반드시 [절대 규칙]을 준수해라.

[절대 규칙] (STRICT)
1. **무근거 행위자 언급 금지**: 한국 기관/외국인 수급 데이터(kospi_foreign_net/inst_net 등)가 구체적 수치로 증명되지 않으면 "유입/매수/의도" 등으로 서술하지 마라.
2. **심리/의도 추측 금지**: "안심하고 있다", "심리가 개선되었다", "지키려는 의도다"와 같은 표현은 절대 금지다. 대신 "VIX 하락 관측", "지표 간 동조화 현상" 등으로 서술해라.
3. **인과 관계 엄격화**: A가 B를 "유도했다"는 표현보다 "A가 하락하는 가운데 B도 동반 하락하는 상관관계가 관측되었다"와 같이 중립적인 팩트 중심으로 서술해라.

[Raw Data]
{json.dumps(raw_data, ensure_ascii=False)}

[신호 원문]
토픽: {signal['topic']}
왜 발생했나: {signal['why_anomalous']}

[출력 형식 (JSON 전용)]
{{
  "topic": "{signal['topic']}",
  "market_state": {{ "risk_appetite": "상승/하락/혼조", "hedging_activity": "증가/감소/정체", "conviction": "높음/낮음", "summary": "한 문장 요약" }},
  "why_now": "왜 지금 이 현상이 중요한지 데이터 관점에서 설명 (과장 수식어 금지)",
  "expectation_vs_reality": {{ "expectation": "시장 컨센서스", "reality": "실제 관측 데이터", "conflict": "괴리 포인트" }},
  "level2_chain": ["A 지표 변화 관측", "B 지표와의 상관관계 확인", "C 지우 변화로 이어지는 흐름"],
  "key_stocks": ["관련 한국 상장 종목 2~4개"],
  "evidence_check": "사용된 핵심 데이터 필드 나열"
}}

반드시 ```json ... ``` 코드블록을 사용해서 출력해라.
"""
        result = self.gemini.call_json(prompt, max_tokens=2500)

        # Gemini 응답 파싱 실패 방어 (Task 5 & 6)
        if not result or not result.get("topic"):
            print("  ⚠️ Gemini 응답 파싱 실패 — 기존 today_analysis.json 유지")
            existing = self.load_existing_analysis()
            if existing:
                print(f"  [DEFENSE_TRACE] 기존 데이터 로드 성공: topic={existing.get('topic')[:20]}...")
                return existing
            return {}

        # 2차 필터링 적용
        result["level2_chain"] = self._filter_level2_chain(result.get("level2_chain", []), raw_data)
        result["why_now"] = self._filter_text(result.get("why_now", ""), raw_data)
        if "market_state" in result:
            result["market_state"]["summary"] = self._filter_text(result["market_state"].get("summary", ""), raw_data)

        return result

    def map_stocks(self, signal, analysis):
        """관련 종목 매핑 (v6.0: MACRO 토픽은 종목보다 시나리오에 집중)"""
        target_type = signal.get("target_type", "MICRO_SECTOR_FOCUS")
        
        # MACRO_GEOPOLITICAL 등 거대 담론은 억지 매핑 지양
        if "MACRO" in target_type:
            print(f"  📢 거대 담론({target_type}) 감지 — 종목보다 거시 시나리오에 집중합니다.")
            return { "date": self.today, "topic_signal": signal["topic"], "stocks": [], "bridge_validated": True }

        print("  종목 매핑 중...")
        keywords = signal.get("related_keywords", []) or signal.get("key_indicators", [])
        related_sectors = get_related_sectors(keywords)

        raw_data = self.load_raw()
        market = raw_data.get("market", {}).get("data", {})
        kospi_foreign_net = market.get("kospi_foreign_net", None)
        kospi_inst_net = market.get("kospi_inst_net", None)
        has_kr_foreign_data = kospi_foreign_net is not None and abs(float(kospi_foreign_net)) > 0.001
        has_kr_inst_data = kospi_inst_net is not None and abs(float(kospi_inst_net)) > 0.001

        topic_lower = signal.get("topic", "").lower()
        why_anomalous = signal.get("why_anomalous", "")
        
        stocks = []
        for sector in related_sectors[:3]:
            sector_stocks = get_stocks_by_sector(sector)
            for s in sector_stocks[:2]:
                stocks.append({ "ticker": s["ticker"], "name": s["name"], "sector": sector, "impact": "수혜", "reason": f"Sector Correlation with {signal['topic']}", "impact_level": "MEDIUM", "is_primary": True })

        # [BRIDGE_VALIDATION] 근거 기반 필터링 (Task 7 & #050-REWORK)
        final_stocks = []
        topic_str = topic_lower + " " + why_anomalous.lower()
        
        for s in stocks:
            # S&P500/Nasdaq -> 삼성전자/SK하이닉스 브리지 체크 (STRICT: Index만으로는 부족)
            if "sp500" in topic_str or "nasdaq" in topic_str:
                # KR 반도체 데이터나 직접 상관계수 데이터가 없으면 매크로 연동 종목은 제거 (Task 4-REWORK)
                pass
            # 유가 -> S-Oil/SK이노베이션 브리지 체크
            elif any(x in topic_str for x in ["oil", "wti", "유가"]):
                if s.get("sector") == "에너지":
                    s["bridge_evidence"] = "Petroleum Product Margin Correlation"
                    final_stocks.append(s)
            # 수급 데이터 (외국인/기관) 있는 경우만 수급 테마 허용
            elif "수급" in s.get("reason", ""):
                if has_kr_foreign_data or has_kr_inst_data:
                    s["bridge_evidence"] = f"KR Data Driven (Foreign: {kospi_foreign_net}, Inst: {kospi_inst_net})"
                    final_stocks.append(s)
            else:
                pass

        print(f"  [BRIDGE_TRACE] Validated {len(final_stocks)}/{len(stocks)} stocks.")
        return { "date": self.today, "topic_signal": signal["topic"], "stocks": final_stocks, "bridge_validated": True }

    def save_results(self, analysis, stocks_data):
        if not analysis or analysis == {} or not analysis.get("topic"):
            print("  ⚠️ 분석 결과 없음 — 저장 건너뜀")
            return False

        (self.analysis_dir / "today_analysis.json").write_text(json.dumps(analysis, ensure_ascii=False, indent=2))
        (self.analysis_dir / "today_stocks.json").write_text(json.dumps(stocks_data, ensure_ascii=False, indent=2))
        print(f"  저장 완료: {self.analysis_dir}")
        return True

    def run(self, detector_result=None):
        print(f"\n🧠 AGENT-04 ANALYST 시작 [{self.today}]")
        signal = self.load_signal()
        if not signal:
            print("  선정된 신호 없음")
            return {}

        raw_data = self.load_raw()
        analysis = self.analyze(signal, raw_data)
        if not analysis or analysis == {}:
            return {"failed": True}

        stocks_data = self.map_stocks(signal, analysis)
        self.save_results(analysis, stocks_data)
        print("✅ AGENT-04 완료\n")
        return {"analysis": analysis, "stocks": stocks_data, "failed": False}


if __name__ == "__main__":
    agent = AnalystAgent()
    agent.run()
