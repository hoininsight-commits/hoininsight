import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
from src.core.filters import SignalFilters
from src.core.gemini_client import GeminiClient
from src.agents.extensions.detector_extensions import DetectorEnricher
from src.agents.extensions.flow_overlay import FlowOverlay
from src.engine.interpretation_layer import InterpretationLayer
from src.engine.anomaly_overlay import AnomalyOverlay
from src.engine.scenario_engine import ScenarioEngine

class DetectorAgent:
    """이상징후 탐지자 — 숫자와 뉴스 맥락을 결합하여 시장의 신호를 포착함 (v7.1 News Integration)"""

    def __init__(self):
        self.base_dir = Path(os.getenv("HOIN_BASE_DIR", Path(__file__).resolve().parents[2]))
        self.today = datetime.now().strftime("%Y%m%d")
        self.raw_dir = self.base_dir / f"data/raw/{self.today}"
        self.signal_dir = self.base_dir / f"data/signals/{self.today}"
        self.signal_dir.mkdir(parents=True, exist_ok=True)
        self.filters = SignalFilters()
        self.gemini = GeminiClient()
        self.enricher = DetectorEnricher(self.base_dir, self.today)
        
        # [TASK #087-089] Engine Components
        self.interpreter = InterpretationLayer(self.base_dir / "data/event_interpretation")
        self.overlay = AnomalyOverlay(self.base_dir / "data/anomaly_overlay")
        self.scenario_engine = ScenarioEngine(self.base_dir / "data/scenario_pack")

    def load_all_data(self) -> dict:
        """모든 수집 데이터 및 90일 히스토리 로드"""
        all_data = {}
        files = ["market", "macro", "sentiment", "fred", "ecos", "dart", "consensus", "cot", "social"]
        for name in files:
            p = self.raw_dir / f"{name}.json"
            if p.exists():
                try:
                    all_data[name] = json.loads(p.read_text())
                    print(f"  ✅ {name}.json 로드")
                except Exception as e:
                    print(f"  ❌ {name}.json 로드 실패: {e}")
        
        # 90일 히스토리 로드 (추세 분석용)
        hist_p = self.base_dir / "data/raw/history/market_90d.json"
        if hist_p.exists():
            try:
                all_data["history_90d"] = json.loads(hist_p.read_text()).get("history_90d", {})
            except: pass

        return all_data

    def build_data_summary(self, all_data: dict) -> str:
        """AI에게 줄 데이터 요약 생성 (제한 해제)"""
        market_block = all_data.get("market", {})
        market = market_block.get("data", {})
        stats  = market.get("multi_period_stats", {})
        fred   = all_data.get("fred", {}).get("data", {})
        ecos   = all_data.get("ecos", {}).get("data", {})
        sentiment = all_data.get("sentiment", {}).get("data", {})
        headlines = sentiment.get("news_headlines", [])
        
        stats_lines = []
        for key, s in stats.items():
            if not s: continue
            stats_lines.append(
                f"{key}: 현재={s.get('current')} "
                f"| 20일Z-score={s.get('z_score_20d')} "
            )

        fred_lines = [f"{k}: {v}" for k, v in fred.items() if v is not None] if fred else []
        ecos_lines = [f"{k}: {v}" for k, v in ecos.items() if v is not None] if ecos else []
        
        foreign_net = market.get("kospi_foreign_net")
        if foreign_net is not None:
            fred_lines.append(f"kospi_foreign_net: {foreign_net}")

        # [TASK #084] 상위 15개 제한 제거 (최대한 많이 전달하되 토큰 효율성 고려)
        news_lines = [f"[{h.get('source','')}] {h.get('title','')}" for h in headlines[:50]]

        summary = f"""
=== 시장 지표 (Z-score) ===
{chr(10).join(stats_lines) if stats_lines else "데이터 없음"}

=== 거시 지표 (FRED/ECOS) ===
{fred_lines}
{ecos_lines}

=== 오늘 뉴스 헤드라인 ===
{chr(10).join(news_lines) if news_lines else "없음"}
"""
        return summary

    def discover_autonomous_narratives(self, all_data: dict) -> list:
        """AI 자율 담론 사냥 (제한 해제)"""
        sentiment = all_data.get("sentiment", {}).get("data", {})
        headlines = sentiment.get("news_headlines", [])
        market = all_data.get("market", {}).get("data", {})
        
        if not headlines or not self.gemini: return []

        system_prompt = """
        You are a JSON-only response system.
        NEVER output explanations, comments, or natural language.
        ALWAYS respond with valid JSON only.
        """

        # [TASK #084] 상위 50개 헤드라인 전달
        prompt = f"""{system_prompt}
너는 HOIN Insight의 '경제사냥꾼' 엔진이다. 지표와 뉴스를 분석해 오늘 시장에서 가장 '이상한(Anomaly)' 서사 3가지를 선정해라.
[오늘 지표] {json.dumps(market, ensure_ascii=False)}
[뉴스] {json.dumps([h.get('title') for h in headlines[:50]], ensure_ascii=False)}

결과 데이터는 반드시 JSON 배열로 출력:
[ {{ "topic": "제목", "reason": "이유", "strength": 점수, "related_keywords": [], "anomaly_type": "SPEED|CORRELATION|NEWS_MISMATCH" }} ]
"""
        try:
            results = self.gemini.call_json_controlled(prompt, agent="DETECTOR")
            return results if isinstance(results, list) else []
        except: return []

    def detect_events_layer(self, all_data: dict) -> list:
        """[TASK #084] 뉴스 헤드라인을 실제 '이벤트' 데이터로 변환"""
        sentiment = all_data.get("sentiment", {}).get("data", {})
        headlines = sentiment.get("news_headlines", [])
        if not headlines: return []

        print(f"  📢 이벤트 레이어 가동: {len(headlines)}개 뉴스 분석 중...")
        
        prompt = f"""
너는 뉴스 헤드라인에서 핵심 경제/산업 이벤트를 추출하는 전문가다.
헤드라인을 보고 시장에 영향을 줄 수 있는 굵직한 이벤트들을 추출하여 JSON 배열로 응답하라.

[이벤트 타입 정의]
- SUPPLY_SHOCK: 파업, 생산 중단, 공급망 병목
- EARNINGS: 실적 발표, 가이드라인 수정
- GEOPOLITICAL: 전쟁, 휴전, 제재, 외교적 마찰
- POLICY: 금리 결정, 정부 규제, 정책 변화
- LIQUIDITY: 유동성 변화, 자금 유입/유출

[출력 형식]
[
  {{
    "event": "이벤트명",
    "entity": "관련 기업/국가",
    "sector": "관련 섹터",
    "type": "위 정의된 타입 중 하나",
    "impact_score": 0.0~1.0
  }}
]

[입력 헤드라인]
{json.dumps([h.get('title') for h in headlines[:50]], ensure_ascii=False)}
"""
        try:
            events = self.gemini.call_json_controlled(prompt, agent="DETECTOR")
            return events if isinstance(events, list) else []
        except: return []

    def detect_anomalies(self, summary: str, candidates: list) -> list:
        """[TASK #085] LLM 기반 자율 이상징후 탐지 (Fact Pack 보강용)"""
        if not self.gemini: return []
        
        prompt = f"""
        당신은 금융 시장의 숨겨진 이상징후(Anomaly)를 사냥하는 전문가입니다.
        제공된 데이터 요약과 후보군을 분석하여, 데이터 간의 모순이나 기술적인 이상 현상을 추가로 포착하세요.
        
        [데이터 요약]
        {summary}
        
        [기존 후보군]
        {json.dumps([c.get('topic') for c in candidates], ensure_ascii=False)}
        
        [지시사항]
        1. 기존 후보군과 중복되지 않는 새로운 관점의 이상징후만 제안하세요.
        2. '숫자가 보여주는 모순'에 집중하세요 (예: 금리 상승에도 기술주 폭등 등).
        3. 반드시 JSON 리스트 형식으로만 응답하세요.
        
        [응답 형식]
        [
          {{
            "topic": "이상징후 제목",
            "anomaly_type": "NEWS_MISMATCH|SPEED|CORRELATION|SENTIMENT_DIVERGENCE",
            "strength": 0.0~10.0,
            "why_anomalous": "왜 이상한지 기술",
            "why_now": "지금 이 시점에 왜 중요한지 기술",
            "key_indicators": ["지표명1", "지표명2"]
          }}
        ]
        """
        try:
            res = self.gemini.call_json_controlled(prompt, agent="DETECTOR")
            return res if isinstance(res, list) else []
        except: return []

    def detect_correlation_anomalies(self, all_data: dict) -> list:
        """[TASK #085] 수치 기반 통계적 이상징후 탐지 (Python Logic)"""
        anomalies = []
        market_data = all_data.get("market", {}).get("data", {})
        stats = market_data.get("multi_period_stats", {})
        
        if not stats: return []

        # 1. 안전자산 역설 (달러/채권 동반 하락 + 증시 급등)
        dxy_z = stats.get("dxy", {}).get("z_score_20d", 0) or 0
        us10y_z = stats.get("us10y", {}).get("z_score_20d", 0) or 0
        sp500_z = stats.get("sp500", {}).get("z_score_20d", 0) or 0
        
        if dxy_z < -1.0 and us10y_z < -1.0 and sp500_z > 1.0:
            anomalies.append({
                "topic": "안전자산 동반 이탈과 유동성 재배치",
                "anomaly_type": "CORRELATION",
                "strength": 8.8,
                "why_anomalous": f"달러(Z:{dxy_z})와 금리(Z:{us10y_z})가 동시 하락하며 증시(Z:{sp500_z})로 자금 쏠림",
                "why_now": "안전자산 동반 하락 및 긴축 우려 해소로 인한 증시 1.0% 이상 상승 (리스크 온)",
                "key_indicators": ["dxy", "us10y", "sp500"]
            })

        # 2. 유가-인플레이션 디커플링
        wti_z = stats.get("wti_oil", {}).get("z_score_20d", 0) or 0
        if wti_z > 1.5 and us10y_z < -1.0:
             anomalies.append({
                "topic": "유가 급등에도 기대인플레이션 차단",
                "anomaly_type": "CORRELATION",
                "strength": 8.2,
                "why_anomalous": f"유가(Z:{wti_z}) 상승이 금리(Z:{us10y_z})에 반영되지 않는 기현상",
                "why_now": "에너지 가격 1.5% 이상 상승 충격을 압도하는 소비 둔화로 인한 국채금리 하락",
                "key_indicators": ["wti_oil", "us10y"]
            })

        return anomalies

    def _validate_why_now(self, text: str) -> dict:
        """[TASK #083-2] WHY NOW 수치 기반 검증 로직"""
        import re
        if not text:
            return {"why_now_valid": False, "contains_numeric": False, "contains_change": False, "contains_threshold": False}
        
        # 1. 숫자 포함 여부 (contains_numeric)
        has_number = bool(re.search(r'\d+', text))
        
        # 2. 변화 크기 포함 여부 (contains_change): %, bp, 상승, 하락, 돌파, 폭락 등
        change_keywords = ["%", "bp", "상승", "하락", "폭등", "폭락", "증가", "감소", "급등", "급락"]
        has_change = any(kw in text for kw in change_keywords) or bool(re.search(r'\d+에서 \d+', text))
        
        # 3. 임계점 또는 조건 포함 여부 (contains_threshold): 이상, 이하, 돌파, 초과, 돌입, 진입
        threshold_keywords = ["이상", "이하", "돌파", "초과", "돌입", "진입", "기준", "평균", "임계", "Z-score"]
        has_threshold = any(kw in text for kw in threshold_keywords)
        
        is_valid = has_number and has_change and has_threshold
        
        return {
            "why_now_valid": is_valid,
            "contains_numeric": has_number,
            "contains_change": has_change,
            "contains_threshold": has_threshold
        }

    def select_best(self, anomalies: list, all_data: dict, events: list = None) -> tuple:
        """[TASK #085 & #086] 신규 스코어링 및 멀티 콘텐츠 구조 적용"""
        if not anomalies: anomalies = []
        corr_anomalies = self.detect_correlation_anomalies(all_data)
        
        market_data = all_data.get("market", {}).get("data", {})
        sentiment_data = all_data.get("sentiment", {})
        mismatch = self._detect_news_mismatch(market_data, sentiment_data)
        
        all_candidates = anomalies + corr_anomalies
        if mismatch: all_candidates.append(mismatch)

        # 1. Enrichment & Flow
        all_candidates = self.enricher.enrich_candidates(all_candidates, all_data)
        overlay = FlowOverlay(self.base_dir)
        all_candidates = [overlay.apply(a, all_data) for a in all_candidates]

        # 2. [TASK #085] Scoring Refactor
        for a in all_candidates:
            base_score = a.get("strength", 5.0)
            bonus = 0.0
            penalty = 0.0
            
            # 뉴스 트리거 결합
            trigger = self._find_news_trigger(a, sentiment_data)
            if trigger: a["news_trigger"] = trigger

            # [TASK #085-2] Scoring Refactor (Event-First Tuning)
            event_match = None
            if events:
                for e in events:
                    if e.get("entity", "").lower() in a["topic"].lower() or \
                       any(k.lower() in e.get("event", "").lower() for k in a.get("related_keywords", [])):
                        event_match = e
                        break
            
            event_bonus = 0.0
            multi_signal_bonus = 0.0

            if event_match:
                a["event_context"] = event_match
                event_bonus += 2.0 # event_context exists
                
                e_type = event_match.get("type", "")
                if e_type in ["GEOPOLITICAL", "SUPPLY_SHOCK"]: event_bonus += 2.0
                elif e_type in ["POLICY", "EARNINGS"]: event_bonus += 1.5
                
                impact_val = event_match.get("impact_score", 0)
                if impact_val >= 0.85: event_bonus += 2.0
                elif impact_val >= 0.7: event_bonus += 1.5
                
                print(f"  ✨ [Event Scoring] {a['topic']}: Type={e_type}, Impact={impact_val} -> Bonus={event_bonus}")

            # MULTI-SIGNAL BONUS (Numeric Anomaly + Event Anomaly)
            is_numeric = a.get("anomaly_type") in ["SPEED", "CORRELATION"]
            if is_numeric and event_match:
                multi_signal_bonus += 2.0
                print(f"  💎 [Multi-Signal] Applied (+2.0) for {a['topic']}")

            # [TASK #083-2] WHY NOW HARDENING & Numeric Injection
            # 1. 팩트 데이터 기반 수치 강제 주입 (Validation 통과용)
            stats = all_data.get("market", {}).get("data", {}).get("multi_period_stats", {})
            injected_facts = []
            for ind in a.get("key_indicators", []):
                if ind in stats:
                    s = stats[ind]
                    injected_facts.append(f"{ind}({s.get('current', 0)} / Z-score:{s.get('z_score_20d', 0)})")
            
            if injected_facts:
                a["why_now"] = (a.get("why_now", "") + " " + " / ".join(injected_facts)).strip()

            why_now_text = a.get("why_now", "") or a.get("news_trigger", "")
            valid_info = self._validate_why_now(why_now_text)
            a["why_now_validation"] = valid_info
            
            if not valid_info["why_now_valid"]:
                penalty += 10.0 # Force Drop
                print(f"  ❌ [Hardening Fail] Dropping '{a['topic']}' - WHY_NOW lacks numeric/change/threshold")

            # Final Score Calculation
            final_score = base_score + event_bonus + multi_signal_bonus - penalty
            a["final_score"] = round(final_score, 2)
            a["event_bonus"] = event_bonus
            a["multi_signal"] = multi_signal_bonus

        # 3. [TASK #086] Multi-Content 구조화
        # final_score 기준 정렬
        sorted_candidates = sorted(all_candidates, key=lambda x: x.get("final_score", 0), reverse=True)
        
        # [DROP 단계] why_now 수치 검증 통과 및 일정 점수 이상만 선정
        valid_candidates = [c for c in sorted_candidates if c.get("final_score", 0) > 4.0]

        # [TASK #087-089] Interpretation & Scenario Integration
        # 1. 선정된 후보들에 대한 이벤트 해석
        candidate_events = []
        for c in valid_candidates:
            if c.get("event_context"):
                candidate_events.append(c["event_context"])
            else:
                # 이벤트가 직접 매핑 안된 경우 토픽 기반 가상 이벤트 생성 (해석용)
                candidate_events.append({
                    "event": c["topic"],
                    "type": c.get("anomaly_type", "UNKNOWN"),
                    "impact_score": c.get("strength", 5.0) / 10.0
                })
        
        interpretations = self.interpreter.interpret_events(candidate_events)
        anomaly_results = self.overlay.overlay_facts(interpretations, all_data)
        scenario_results = self.scenario_engine.generate_scenarios(valid_candidates, interpretations)

        print(f"  🧠 [Engine] Interpretations: {len(interpretations)}, Overlays: {len(anomaly_results)}, Scenarios: {len(scenario_results)}")

        # 2. 결과 결합 및 분류 (Classification)
        for i, c in enumerate(valid_candidates):
            interp = interpretations[i] if i < len(interpretations) else {}
            overlay = anomaly_results[i] if i < len(anomaly_results) else {}
            scenarios = scenario_results[i] if i < len(scenario_results) else {}
            
            c["normal_flow"] = interp.get("normal_flow", {})
            c["scenarios"] = scenarios.get("scenarios", [])
            c["anomaly_overlay"] = overlay
            
            # Classification 규칙: anomaly_score 기반
            is_anomaly = overlay.get("is_anomaly", False)
            c["classification"] = "ANOMALY" if is_anomaly else "NORMAL"
            print(f"  🏷️ [Classify] {c['topic'][:30]}... -> {c['classification']} (Score: {overlay.get('anomaly_score', 0)})")

        tiered_results = {
            "MAIN": valid_candidates[0] if len(valid_candidates) > 0 else None,
            "SECONDARY": valid_candidates[1:3],
            "EARLY_SIGNAL": [c for c in valid_candidates[3:] if c.get("event_context")][:2]
        }

        return tiered_results, valid_candidates

    def generate_fact_pack(self, candidates: list, all_data: dict) -> list:
        """[TASK #083] 각 candidate에 대한 상세 팩트 패키지 생성"""
        fact_packs = []
        market_stats = all_data.get("market", {}).get("data", {}).get("multi_period_stats", {})
        fred_data = all_data.get("fred", {}).get("data", {})
        ecos_data = all_data.get("ecos", {}).get("data", {})
        
        for cand in candidates:
            pack = {
                "topic": cand["topic"],
                "core_facts": [],
                "anomaly": [cand.get("why_anomalous", "")],
                "why_now": [cand.get("why_now", "")],
                "event_context": cand.get("event_context", []),
                "normal_flow": cand.get("normal_flow", {}),
                "scenarios": cand.get("scenarios", []),
                "anomaly_overlay": cand.get("anomaly_overlay", {}),
                "classification": cand.get("classification", "NORMAL"),
                "constraints": []
            }
            
            # 핵심 지표 추출
            indicators = cand.get("key_indicators", [])
            for ind in indicators:
                if ind in market_stats:
                    s = market_stats[ind]
                    pack["core_facts"].append({
                        "name": ind,
                        "value": s.get("current"),
                        "previous": s.get("prev_1d"),
                        "change": s.get("1d_change_pct")
                    })
            
            # 추가 매크로 지표 보완
            if not pack["core_facts"]:
                # 지표가 없으면 강제로 시장 주요 지표 주입 (KOSPI, S&P500)
                for ind in ["kospi", "sp500"]:
                    if ind in market_stats:
                        s = market_stats[ind]
                        pack["core_facts"].append({
                            "name": ind,
                            "value": s.get("current"),
                            "previous": s.get("prev_1d"),
                            "change": s.get("1d_change_pct")
                        })
    def run(self, collector_result=None):
        print(f"\n🔍 AGENT-03 DETECTOR v10.1 [Topic Selection Engine v1.0]")
        all_data = self.load_all_data()
        if not all_data: return {}

        # [TASK #101] New Topic Selection Engine v1.0 가동
        from src.topic_engine.engine import TopicSelectionEngine
        topic_engine = TopicSelectionEngine(self.base_dir)
        selection = topic_engine.run(all_data)
        
        # 팩트 데이터 패키징 (WriterAgent 및 폴백 엔진용)
        fact_pack = []
        if selection and selection.get("MAIN"):
            main = selection["MAIN"]
            fact_pack.append({
                "topic": main["event"],
                "core_facts": main["core_facts"],
                "classification": main.get("evaluation", {}).get("flow_type", "NORMAL"),
                "scenarios": main.get("scenarios", []), 
                "why_now": [main.get("evaluation", {}).get("why_now_summary", "")],
                "evidence_bundle": main.get("evidence_bundle", {}),
                "mechanism": main.get("mechanism", "지표 간의 상관관계 변화 관측"),
                "strength": main.get("final_score", 5.0) * 10,
                "stocks": main.get("stocks", []),
                "stocks_analysis": main.get("stocks_analysis", {})
            })
            
            # fact_pack 저장 (WriterAgent 연동 핵심)
            fact_pack_dir = Path("data/fact_pack")
            fact_pack_dir.mkdir(parents=True, exist_ok=True)
            (fact_pack_dir / "candidates_fact_pack.json").write_text(
                json.dumps(fact_pack, ensure_ascii=False, indent=2)
            )
            
            # today_signal.json 저장 (기존 호환성)
            (self.signal_dir / "today_signal.json").write_text(json.dumps(selection["MAIN"], ensure_ascii=False, indent=2))
            
            # [BRIDGE] final_decision_card.json 생성 (Publisher 연동)
            decision_dir = self.base_dir / "data/decision" / datetime.now().strftime("%Y/%m/%d")
            decision_dir.mkdir(parents=True, exist_ok=True)
            decision_card = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "MAIN": {
                    **selection["MAIN"],
                    "stocks": selection["MAIN"].get("stocks", []),
                    "stocks_analysis": selection["MAIN"].get("stocks_analysis", {}),
                    "arbiter_rationale": selection["MAIN"].get("arbiter_rationale", "N/A"),
                    "hunter_insight": selection["MAIN"].get("hunter_insight", "N/A")
                },
                "SECONDARY": selection.get("SECONDARY", []),
                "EARLY": selection.get("EARLY", [])
            }
            (decision_dir / "final_decision_card.json").write_text(
                json.dumps(decision_card, ensure_ascii=False, indent=2)
            )
            print(f"  ✅ Decision card published to {decision_dir}")
        
        return {"selected": selection, "fact_pack": fact_pack}

    def _find_news_trigger(self, signal: dict, sentiment_data: dict) -> str:
        """관련 뉴스 헤드라인 매칭 (기존 로직 유지)"""
        topic = signal.get("topic", "").lower()
        headlines = sentiment_data.get("data", {}).get("news_headlines", [])
        
        # [DEFENSE] headlines가 dict인 경우 (V7.1에서 관측됨)
        if isinstance(headlines, dict):
            headlines = headlines.get("news_headlines", [])

        TOPIC_KEYWORDS = {
            "wti": ["호르무즈", "hormuz", "유가", "oil", "wti", "opec", "원유", "석유"],
            "gold": ["금", "gold", "귀금속", "안전자산"],
            "sp500": ["deepseek", "딥시크", "s&p", "나스닥", "nasdaq", "주가", "증시", "기술주", "ai"],
            "dxy": ["달러", "dollar", "dxy", "환율"],
            "kr_": ["코스피", "한국", "kospi", "원화"],
        }
        
        matched_keywords = []
        for key, keywords in TOPIC_KEYWORDS.items():
            if any(kw.lower() in topic for kw in keywords):
                matched_keywords.extend(keywords)
        
        if not matched_keywords:
            matched_keywords = [w for w in topic.split() if len(w) >= 2]

        best_match = None
        best_score = -1
        
        for h in headlines:
            title = h.get("title", "").lower()
            score = 0
            for kw in matched_keywords:
                if kw.lower() in title:
                    score += 10 if kw.lower() in ["deepseek", "호르무즈", "파업"] else 1
            
            if score > best_score:
                best_match = h.get("title")
                best_score = score
                
        return best_match or ""

    def _detect_news_mismatch(self, market_data: dict, sentiment_data: dict) -> dict:
        """뉴스 톤 vs 지표 방향 모순 탐지 (기존 로직 유지)"""
        headlines = sentiment_data.get("data", {}).get("news_headlines", [])
        if isinstance(headlines, dict): headlines = headlines.get("news_headlines", [])
        
        headline_text = " ".join([h.get("title", "") for h in headlines]).lower()
        
        negative_keywords = ["sink", "rout", "crash", "fear", "stumbled", "폭락", "급락", "위기"]
        sp500_z = market_data.get("multi_period_stats", {}).get("sp500", {}).get("z_score_20d", 0) or 0
        
        if any(kw in headline_text for kw in negative_keywords) and sp500_z > 1.0:
            return {
                "topic": "뉴스 악재 속 지수 상승 (Price-News 모순)",
                "anomaly_type": "NEWS_MISMATCH",
                "strength": 9.2,
                "why_anomalous": f"뉴스 톤은 부정적이나 SP500 Z-score {sp500_z:.2f}로 강한 상승 중",
                "why_now": f"악재를 압도하는 수급 유입으로 인한 SP500 {sp500_z:.2f} (Z-score 1.0 이상) 상승 국면",
                "key_indicators": ["sp500", "sentiment"]
            }
        return {}

    def _is_absolute_value_topic(self, topic: str, anomaly: dict) -> bool:
        forbidden = ["돌파", "도달", "최고가", "최저가"]
        return any(f in topic for f in forbidden) and anomaly.get("anomaly_type") == "SPEED"


if __name__ == "__main__":
    DetectorAgent().run()
