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
        return raw

    def _filter_text(self, text: str, market_data: dict) -> str:
        """텍스트에서 SPECULATION 등급 문장을 차단하거나 INTERPRETATION으로 낮춤 (Hardened #051)"""
        if not text:
            return text

        market = market_data.get("market", {}).get("data", {})
        kospi_foreign_net = market.get("kospi_foreign_net", None)
        kospi_inst_net = market.get("kospi_inst_net", None)
        
        # [DATA_CHECK] 수급 데이터 존재 여부 확인 (KR 기준)
        has_kr_foreign_data = kospi_foreign_net is not None and abs(float(kospi_foreign_net)) > 0.001
        has_kr_inst_data = kospi_inst_net is not None and abs(float(kospi_inst_net)) > 0.001

        # 1. 태그 기반 판정
        is_interp = "[I]" in text

        # [허용 해석 표현] (Task 3)
        allowed_interp_markers = [
            "시사한다", "해석될 수 있다", "볼 수 있다", "가능성이 있다", 
            "관측된다", "읽힌다", "점이 중요하다", "관측되는 중"
        ]

        # 2. SPECULATION 감지 및 처리 (Task 2)
        # 조건 A: 행위자 언급 + 데이터 부재
        actor_pattern = r"(외국인|외인|기관|세력|개미|개인|스마트\s*머니)"
        if re.search(actor_pattern, text):
            # 외국인 데이터 없는데 외국인 언급 시
            if "외국" in text or "외인" in text:
                if not has_kr_foreign_data:
                    text = re.sub(actor_pattern, "시장 수급", text)
            # 기관 데이터 없는데 기관 언급 시
            if "기관" in text:
                if not has_kr_inst_data:
                    text = re.sub(actor_pattern, "수급 환경", text)

        # 조건 B/C/D: 심리, 자금흐름, 의도 단정 문장을 해석형으로 낮춤
        spec_patterns = [
            (r"(안심했다|낙관적이다|공포에\s*빠졌다|광기|불안\s*상태)", "로 읽힐 수 있는 가능성이 관측된다"),
            (r"(몰리고\s*있다|유입되었다|이탈했다|대규모\s*전환)", "의 변동 가능성이 시사된다"),
            (r"(방어하려\s*한다|대비하고\s*있는|관리하고\s*있는|유도)", "의 움직임으로 해석될 소지가 관측된다"),
            (r"(강력한|역대급|압도적)", "이례적인 수준의")
        ]
        
        for pattern, repl in spec_patterns:
            if re.search(pattern, text):
                # 단정형이면 해석형 어미로 교체
                text = re.sub(pattern, repl, text)

        # 3. INTERPRETATION 문구 강제 (Task 3)
        # [I] 등급인데 단정적 어미(~다)로 끝나는지 체크
        if is_interp and text.strip().endswith("다."):
            # 허용 마커가 하나도 없으면 "관측된다."로 교체 시도
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
        
        prompt = ANALYST_PROMPT_TEMPLATE.format(
            today=self.today,
            topic=signal.get("topic"),
            strength=signal.get("strength"),
            market_summary=json.dumps(market, ensure_ascii=False),
            cot_summary=json.dumps(raw_data.get("cot", {}), ensure_ascii=False),
            kospi_foreign_net=market.get("kospi_foreign_net", "0.00")
        )

        result = self.gemini.call_json(prompt, max_tokens=2500)

        # Gemini 응답 파싱 실패 방어
        if not result or not result.get("topic"):
            print("  ⚠️ Gemini 응답 파싱 실패 — 기존 today_analysis.json 유지")
            existing = self.load_existing_analysis()
            if existing:
                return existing
            return {}

        # 2차 필터링 적용 (3계층 준수 여부 사후 검증)
        result["level2_chain"] = self._filter_level2_chain(result.get("level2_chain", []), raw_data)
        result["why_now"] = self._filter_text(result.get("why_now", ""), raw_data)
        if "market_state" in result:
            result["market_state"]["summary"] = self._filter_text(result["market_state"].get("summary", ""), raw_data)

        return result

    def map_stocks(self, signal, analysis):
        """관련 종목 매핑 (근거 브리지 체크 강화)"""
        target_type = signal.get("target_type", "MICRO_SECTOR_FOCUS")
        
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

        # [BRIDGE_VALIDATION] 근거 기반 필터링
        final_stocks = []
        topic_str = topic_lower + " " + why_anomalous.lower()
        
        for s in stocks:
            if "sp500" in topic_str or "nasdaq" in topic_str:
                pass
            elif any(x in topic_str for x in ["oil", "wti", "유가"]):
                if s.get("sector") == "에너지":
                    s["bridge_evidence"] = "Petroleum Product Margin Correlation"
                    final_stocks.append(s)
            elif "수급" in s.get("reason", ""):
                if has_kr_foreign_data or has_kr_inst_data:
                    s["bridge_evidence"] = f"KR Data Driven (Foreign: {kospi_foreign_net}, Inst: {kospi_inst_net})"
                    final_stocks.append(s)
            else:
                pass

        return { "date": self.today, "topic_signal": signal["topic"], "stocks": final_stocks, "bridge_validated": True }

    def save_results(self, analysis, stocks_data):
        if not analysis or analysis == {} or not analysis.get("topic"):
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
