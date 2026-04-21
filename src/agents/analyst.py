import json
import re
from datetime import datetime
from pathlib import Path
from src.core.gemini_client import GeminiClient
from src.core.sector_map import get_related_sectors, get_stocks_by_sector, get_reason_template
from src.prompts.analyst_prompt import ANALYST_PROMPT_TEMPLATE


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
        
        # 90일 히스토리 로드 (WHY NOW 분석용)
        hist_p = Path("data/raw/history/market_90d.json")
        if hist_p.exists():
            try:
                raw["history_90d"] = json.loads(hist_p.read_text())
            except: pass
        return raw

    def _filter_text(self, text: str, market_data: dict) -> str:
        """텍스트에서 SPECULATION 등급 문장을 차단하거나 INTERPRETATION으로 낮춤 (Hardened #053)"""
        if not text:
            return text

        market = market_data.get("market", {}).get("data", {})
        cot = market_data.get("cot", {})
        kospi_foreign_net = market.get("kospi_foreign_net", None)
        kospi_inst_net = market.get("kospi_inst_net", None)
        
        # [DATA_CHECK] 수급 데이터 존재 여부 확인
        has_kr_foreign_data = kospi_foreign_net is not None and abs(float(kospi_foreign_net)) > 0.001
        has_kr_inst_data = kospi_inst_net is not None and abs(float(kospi_inst_net)) > 0.001
        has_cot_data = bool(cot.get("smart_money_signals")) or bool(cot.get("top_signal"))

        # [I] 등급 여부
        is_interp = "[I]" in text

        # 1. SPECULATION 감지 및 처리 (정밀화 #053)
        
        # 조건 1: 호칭/행위자 필터링
        # 외국인 순매수가 0에 가까우면 외국인 언급 금지
        foreign_pattern = r"(외국인|외인)\s*(자금|수급|매수|매도|유입|유출|순매수|순매도|동향|움직임)"
        if not has_kr_foreign_data and re.search(foreign_pattern, text):
            text = re.sub(foreign_pattern, "시장 수급 변화", text)

        # 항상 적용: 개인/군중 심리 및 추측성 키워드 차단
        speculation_pattern = r"(개미|개인\s*투자자|포모|FOMO|모멘텀\s*자금|군중\s*심리|세력|스마트\s*머니|진짜\s*고수)"
        if re.search(speculation_pattern, text):
            text = re.sub(speculation_pattern, "시장 참여자", text)

        # 기관: COT 데이터가 있는 경우 언급 허용하되, 데이터 없으면 차단
        inst_pattern = r"(기관(?:들)?)\s*(자금|수급|매수|매도|유입|유출|순매수|순매도)"
        if not has_kr_inst_data and not has_cot_data and re.search(inst_pattern, text):
            text = re.sub(inst_pattern, "수급 환경", text)

        # 2. 심리, 자금흐름, 의도 단정 문장을 해석형으로 낮춤
        spec_patterns = [
            (r"(안심했다|낙관적이다|공포에\s*빠졌다|광기|불안\s*상태)", "로 읽힐 수 있는 가능성이 관측된다"),
            (r"(몰리고\s*있다|유입되었다|이탈했다|대규모\s*전환)", "의 변동 가능성이 시사된다"),
            (r"(방어하려\s*한다|대비하고\s*있는|관리하고\s*있는|유도)", "의 움직임으로 해석될 소지가 관측된다"),
            (r"(강력한|역대급|압도적)", "이례적인 수준의"),
            (r"(하락을\s*예상|보험을|방어적으로|선제적으로)", "포지션 변화 가능성")
        ]
        
        for pattern, repl in spec_patterns:
            if re.search(pattern, text):
                text = re.sub(pattern, repl, text)

        # 3. INTERPRETATION 문구 강제 (Task 3)
        allowed_interp_markers = ["시사한다", "해석될 수 있다", "볼 수 있다", "가능성이 있다", "관측된다", "읽힌다", "관측되는 중"]
        if is_interp and text.strip().endswith("다."):
            if not any(marker in text for marker in allowed_interp_markers):
                text = text.replace("다.", " 점이 관측된다.")

        return text

    def _filter_level2_chain(self, level2_chain: list, market_data: dict) -> list:
        """level2_chain 항목 필터링 및 3계층 검증 (Task 1 & 2)"""
        if not level2_chain:
            return level2_chain
        
        filtered = []
        for item in level2_chain:
            # [S] 태그가 붙은 문장은 필터링 단계에서 제거하도록 유도 (프롬프트에서 이미 SPECULATION은 S로 태그됨)
            if "[S]" in item:
                continue
                
            filtered_item = self._filter_text(item, market_data)
            if filtered_item:
                filtered.append(filtered_item)
        return filtered

    def load_existing_analysis(self):
        """기존 today_analysis.json 로드 (Gemini 파싱 실패 시 폴백)"""
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
        """Gemini를 이용한 레벨2 데이터 관계 분석 (3계층 관리 도입)"""
        print("  Gemini API 레벨2 분석 중...")
        
        market = raw_data.get("market", {}).get("data", {})
        
        # Hunter Context 준비 (Surface, Structure, Flow Interpretation, Chain, Beneficiary, Decision Meta 등)
        hunter_fields = ["surface", "structure", "flow_interpretation_hunter", "consequence_chain", "beneficiary", "why_now_hunter", "decision_meta"]
        hunter_context = {k: signal.get(k) for k in hunter_fields if k in signal}

        prompt = ANALYST_PROMPT_TEMPLATE.format(
            today=self.today,
            topic=signal.get("topic"),
            strength=signal.get("strength"),
            market_summary=json.dumps(market, ensure_ascii=False),
            cot_summary=json.dumps(raw_data.get("cot", {}), ensure_ascii=False),
            kospi_foreign_net=str(market.get("kospi_foreign_net", "Unknown")),
            history_90d=json.dumps(raw_data.get("history_90d", {}), ensure_ascii=False),
            hunter_context=json.dumps(hunter_context, ensure_ascii=False, indent=2)
        )

        try:
            result = self.gemini.call_json_controlled(prompt, agent="ANALYST")
            if not result or not result.get("topic_core_claim"):
                raise Exception("Empty Result or Protocol Violation")
            result["fallback_used"] = False
        except Exception as e:
            print(f"  ⚠️ ANALYST Gemini Error ({e}). Fallback 모드 가동.")
            from src.analyst.fallback_analyst import generate_fallback_analysis
            result = generate_fallback_analysis(signal)
            result["fallback_used"] = True

        # Phase 6 Task 7: 품질 검증 (Quality Gate)
        from src.validation.quality_gate import validate_minimum_quality
        if not validate_minimum_quality(result):
            print("  ⚠️ 품질 검증 실패. 제어 레이어에 의해 Fallback 강제 전환.")
            from src.analyst.fallback_analyst import generate_fallback_analysis
            result = generate_fallback_analysis(signal)
            result["fallback_used"] = True

        # 2차 필터링 적용 (3계층 준수 여부 사후 검증)
        result["level2_chain"] = self._filter_level2_chain(result.get("level2_chain", []), raw_data)
        result["why_now"] = self._filter_text(result.get("why_now", ""), raw_data)
        if "market_state" in result:
            if "summary" in result["market_state"]:
                result["market_state"]["summary"] = self._filter_text(result["market_state"].get("summary", ""), raw_data)

        return result

    def map_stocks(self, signal, analysis):
        """관련 종목 매핑 (경제사냥꾼 DNA 브리지 검증 강화 #053)"""
        target_type = signal.get("target_type", "MICRO_SECTOR_FOCUS")
        level2_chain_text = " ".join(analysis.get("level2_chain", [])).lower()
        
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
        why_anomalous = signal.get("why_anomalous", "").lower()
        topic_combined = topic_lower + " " + why_anomalous
        
        stocks = []
        for sector in related_sectors[:3]:
            # [CROSS_CHECK] level2_chain에 해당 섹터나 키워드가 언급되어 있는지 확인
            if sector.lower() not in level2_chain_text and not any(kw.lower() in level2_chain_text for kw in keywords):
                continue

            sector_stocks = get_stocks_by_sector(sector)
            for s in sector_stocks[:2]:
                stocks.append({ 
                    "ticker": s["ticker"], 
                    "name": s["name"], 
                    "sector": sector, 
                    "impact": "수혜", 
                    "reason": f"{sector} Correlation with {signal['topic']}", 
                    "impact_level": "MEDIUM", 
                    "is_primary": True 
                })

        # [BRIDGE_VALIDATION] 근거 기반 필터링 (DNA 규칙 적용 #053)
        final_stocks = []
        
        for s in stocks:
            # 1. WTI/유가 관련 -> 에너지 섹터만 허용
            if any(x in topic_combined for x in ["oil", "wti", "유가", "crude"]):
                if s.get("sector") == "에너지":
                    s["bridge_evidence"] = "Petroleum Product Margin Correlation (Price Driven)"
                    final_stocks.append(s)
                continue

            # 2. S&P500/나스닥 Z-score 관련 -> 반도체/기술주 허용하되 거시 연결 필수
            if any(x in topic_combined for x in ["sp500", "nasdaq", "나스닥", "기술주"]):
                # 금리(yield)나 달러(dxy) 연결 고리가 서사에 있는지 확인
                has_macro_link = any(x in topic_combined or x in level2_chain_text for x in ["금리", "yield", "달러", "dxy", "treasury"])
                if s.get("sector") == "반도체":
                    if has_macro_link:
                        s["reason"] = f"Macro-Driven Liquidity Flow ({signal['topic']}) -> Tech Rebound"
                        s["bridge_evidence"] = "Interest Rate Sensitivity Bridge"
                        final_stocks.append(s)
                elif s.get("sector") == "IT":
                    if has_macro_link:
                        s["bridge_evidence"] = "Growth Stock Valuation Buffer"
                        final_stocks.append(s)
                continue

            # 3. 수급 토픽 (국내)
            if "수급" in topic_combined or "매수" in topic_combined:
                if has_kr_foreign_data or has_kr_inst_data:
                    s["bridge_evidence"] = f"KR Data Driven (Foreign: {kospi_foreign_net}, Inst: {kospi_inst_net})"
                    final_stocks.append(s)
            else:
                pass

        return { "date": self.today, "topic_signal": signal["topic"], "stocks": final_stocks, "bridge_validated": True }

    def save_results(self, analysis, stocks_data):
        if not analysis or analysis == {}:
            return False
        
        # topic 또는 topic_core_claim 중 하나만 있어도 유효한 것으로 간주
        if not analysis.get("topic") and not analysis.get("topic_core_claim"):
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

        # [EXTENSION] 팩트 기반 가격 기록 (v3.0 Truth Engine)
        raw_data = self.load_raw()
        market = raw_data.get("market", {}).get("data", {})
        # 주요 지표 중 하나를 기준가로 선정 (KOSPI 우선, 없으면 S&P500)
        signal["base_price"] = market.get("kospi", market.get("sp500", 0))
        signal["date"] = self.today

        # [EXTENSION] Truth Engine Feedback Loop - Phase 1: 이전 결과 업데이트 & 가중치 조정
        try:
            from src.validation.outcome_tracker import update_pending_outcomes
            from src.decision.weight_adjuster import adjust_weights
            import json
            
            # 현재 시장 가격 정보 추출 (KOSPI/S&P500 등)
            current_market = {
                "KOSPI": market.get("kospi", 0),
                "SPX": market.get("sp500", 0),
                "current": market.get("kospi", market.get("sp500", 0))
            }
            
            # 1. PENDING 상태 업데이트
            history = update_pending_outcomes(current_market)
            
            # 2. 가중치 조정
            adjust_weights(history)
            
            from src.analysis.hunter_enricher import HunterEnricher
            enricher = HunterEnricher(Path(self.raw_dir.resolve().parents[2]))
            signal = enricher.enrich(signal)
            # 강화된 시그널 다시 저장 (Writer 등이 사용하도록)
            (self.signal_dir / "today_signal.json").write_text(json.dumps(signal, ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"  ⚠️ Truth Engine Feedback Loop 초기화 실패: {e}")

        raw_data = self.load_raw()
        analysis = self.analyze(signal, raw_data)
        if not analysis or analysis == {}:
            return {"failed": True}

        # [EXTENSION] Truth Engine Feedback Loop - Phase 2: 오늘 결과 기록
        try:
            from src.validation.outcome_tracker import record_outcome
            decision = analysis.get("decision_meta", {})
            if not decision: # HunterEnricher가 signal["decision_meta"]에 넣음
                decision = signal.get("decision_meta", {})
            
            market_data = {"entry": signal.get("base_price", 0)}
            record_outcome(signal, decision, market_data)
            print("  ✅ Truth Engine Outcome Recorded (PENDING)")
        except Exception as e:
            print(f"  ⚠️ Truth Engine Outcome Recording 실패: {e}")

        stocks_data = self.map_stocks(signal, analysis)
        self.save_results(analysis, stocks_data)
        print("✅ AGENT-04 완료\n")
        return {"analysis": analysis, "stocks": stocks_data, "failed": False}


if __name__ == "__main__":
    agent = AnalystAgent()
    agent.run()
