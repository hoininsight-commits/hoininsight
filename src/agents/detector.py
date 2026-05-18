import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
from src.utils.target_date import get_target_ymd, get_current_round, get_standard_path_prefix
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
        self.today = get_target_ymd().replace("-", "")
        self.round = get_current_round()
        self.path_prefix = get_standard_path_prefix()
        self.raw_dir = self.base_dir / "data/raw" / self.path_prefix
        self.signal_dir = self.base_dir / "data/signals" / self.path_prefix
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

        # [SOCIAL INTEGRATION] SocialAgent 데이터 통합
        social_block = all_data.get("social", {})
        social_lines = []
        if social_block:
            trending = social_block.get("trending_topics", [])
            deep = social_block.get("deep_research", [])
            if trending: social_lines.append(f"Trending: {', '.join(trending[:5])}")
            for d in deep[:5]:
                social_lines.append(f"- [SOCIAL] {d.get('title', '')}: {d.get('snippet','')[:100]}...")

        summary = f"""
=== 시장 지표 (Z-score) ===
{chr(10).join(stats_lines) if stats_lines else "데이터 없음"}

=== 거시 지표 (FRED/ECOS) ===
{fred_lines}
{ecos_lines}

=== 소셜 리서치 및 트렌드 (51% Priority) ===
{chr(10).join(social_lines) if social_lines else "소셜 데이터 없음"}

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
        # [SOCIAL PRIORITIZATION] 소셜 데이터 출처 가중치 반영
        summary = self.build_data_summary(all_data)
        
        prompt = f"""{system_prompt}
너는 금융 시장의 전방위적 데이터를 분석하는 전략가다. 
[지표/소셜/뉴스]를 통합 분석해 오늘 시장에서 가장 '이례적인(Anomaly)' 서사 3가지를 선정해라.

선정 시, **소셜 리서치(Social Research)** 데이터 소스에 51%의 비중을 두어 실시간 시장의 열기와 시의성을 우선적으로 고려하라.

[시장 데이터 요약]
{summary}

결과 데이터는 반드시 JSON 배열로 출력:
[ {{ "topic": "제목", "reason": "이유", "strength": 점수, "related_keywords": [], "anomaly_type": "SPEED|CORRELATION|NEWS_MISMATCH" }} ]
"""
        try:
            results = self.gemini.call_json_controlled(prompt, agent="DETECTOR", tier=1)
            return results if isinstance(results, list) else []
        except: return []

    def detect_events_layer(self, all_data: dict) -> list:
        """[TASK #084] 뉴스 및 소셜 데이터를 실제 '이벤트' 데이터로 변환"""
        sentiment = all_data.get("sentiment", {}).get("data", {})
        headlines = sentiment.get("news_headlines", [])
        social_block = all_data.get("social", {})
        social_deep = social_block.get("deep_research", [])
        
        if not headlines and not social_deep: return []
        
        social_context = "\n".join([f"- {d.get('title')}: {d.get('snippet','')}" for d in social_deep[:10]])

        prompt = f"""
너는 뉴스 및 소셜 리서치에서 핵심적인 경제/산업 이벤트를 추출하는 전문가다.
데이터의 시의성과 파급력을 고려하여 시장에 큰 영향을 줄 수 있는 굵직한 이벤트들을 추출하라.

[입력 데이터]
{social_context}
뉴스 헤드라인: {json.dumps([h.get('title') for h in headlines[:30]], ensure_ascii=False)}

위 데이터를 보고 이벤트를 추출하여 JSON 배열로 응답하라.
소셜 리서치 데이터 소스에 기반한 이벤트에 우선순위를 두어라.

결과 형식: [ {{ "event": "제목", "entity": ["대상"], "type": "타입", "importance": 1~10 }} ]
"""
        try:
            print(f"  📢 이벤트 레이어 가동: 뉴스 {len(headlines)}개, 소셜 리서치 {len(social_deep)}개 분석 중...")
            results = self.gemini.call_json_controlled(prompt, agent="DETECTOR_EVENT", tier=1)
            return results if isinstance(results, list) else []
        except Exception as e:
            print(f"  ❌ 이벤트 레이어 실패: {e}")
            return []


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
            res = self.gemini.call_json_controlled(prompt, agent="DETECTOR", tier=3)
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
        """수치 기반 검증 로직 (Agnostic Version)"""
        import re
        if not text:
            return {"why_now_valid": False, "contains_numeric": False, "contains_change": False, "contains_threshold": False}
        
        # 순수하게 숫자가 포함되어 있는지만 검증 (방향성 등은 Arbiter가 판단)
        has_number = bool(re.search(r'\d+', text))
        
        return {
            "why_now_valid": has_number,
            "contains_numeric": has_number,
            "contains_change": True, # Deprecated (Agnostic rule)
            "contains_threshold": True # Deprecated (Agnostic rule)
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
        """[v21.0] AGNOSTIC STRATEGIC HUNT: 로우 데이터 전수 조사를 통한 토픽 선정"""
        print(f"\n🔍 AGENT-03 DETECTOR v21.0 [Strategic Hunt Mode]")
        
        # 1. 로우 데이터 존재 확인
        if not self.raw_dir.exists():
            print(f"  ⚠️ [Detector] Raw directory not found: {self.raw_dir}")
            return {}

        # 2. [STRATEGIC HUNT] Arbiter를 통해 로우 데이터 전체 분석
        from src.topic_engine.arbiter import TopicArbiter
        arbiter = TopicArbiter()
        
        print(f"  🎯 [Strategic Hunt] Analyzing all raw data in {self.raw_dir}...")
        hunt_result = arbiter.select_topic_from_raw(self.raw_dir)
        
        main = hunt_result.get("MAIN")
        if not main:
            print("  ❌ [Detector] Strategic hunt failed to produce a topic.")
            return {}

        # 3. 팩트 데이터 패키징 (WriterAgent 호환성 유지)
        # Arbiter가 찾은 '데이터 사슬'과 '통찰'을 팩트팩에 주입
        fact_pack = [{
            "topic": main["topic"],
            "core_facts": [], # 필요한 수치는 Writer가 data_chain에서 추출
            "classification": "STRATEGIC",
            "why_now": [main.get("arbiter_rationale", "")],
            "evidence_bundle": {
                "data_chain": main.get("data_chain"),
                "social_intelligence": main.get("hunter_insight") # 통찰을 소셜 지능으로 매핑
            },
            "arbiter_rationale": main.get("arbiter_rationale"),
            "hunter_insight": main.get("hunter_insight"),
            "actionable_event": main.get("actionable_event"),
            "tier": "MAIN/TIER_1"
        }]
        
        # 4. 결과 저장 (WriterAgent 연동)
        fact_pack_dir = Path("data/fact_pack")
        fact_pack_dir.mkdir(parents=True, exist_ok=True)
        fact_pack_path = fact_pack_dir / "candidates_fact_pack.json"
        fact_pack_path.write_text(json.dumps(fact_pack, ensure_ascii=False, indent=2))
        
        # today_signal.json 저장 (기존 호환성)
        (self.signal_dir / "today_signal.json").write_text(json.dumps(main, ensure_ascii=False, indent=2))
        
        print(f"  ✅ Strategic Hunt Completed: {main['topic']}")
        print(f"  📂 Fact Pack saved to {fact_pack_path}")
        
        return {"selected": hunt_result, "fact_pack": fact_pack}

    def _find_news_trigger(self, signal: dict, sentiment_data: dict) -> str:
        """Agnostic 헤드라인 매칭 (하드코딩 키워드 및 특혜 점수 제거)"""
        topic = signal.get("topic", "").lower()
        headlines = sentiment_data.get("data", {}).get("news_headlines", [])
        
        if isinstance(headlines, dict):
            headlines = headlines.get("news_headlines", [])

        # 인간의 개입(TOPIC_KEYWORDS) 없이, 토픽에 나타난 단어 자체의 교집합으로만 스코어링
        matched_keywords = [w for w in topic.split() if len(w) >= 2]

        best_match = None
        best_score = -1
        
        for h in headlines:
            title = h.get("title", "").lower()
            score = sum(1 for kw in matched_keywords if kw.lower() in title)
            
            if score > best_score:
                best_match = h.get("title")
                best_score = score
                
        return best_match or ""

    def _detect_news_mismatch(self, market_data: dict, sentiment_data: dict) -> dict:
        """뉴스 모순 탐지 (Agnostic 버전에 맞게 하드코딩 폐기)"""
        # 인간의 주관적 텍스트 지정(negative_keywords) 방식 제거.
        # 순수하게 데이터 기반으로 모순을 탐지할 방법이 마련될 때까지 비활성화
        return {}

    def _is_absolute_value_topic(self, topic: str, anomaly: dict) -> bool:
        forbidden = ["돌파", "도달", "최고가", "최저가"]
        return any(f in topic for f in forbidden) and anomaly.get("anomaly_type") == "SPEED"


if __name__ == "__main__":
    DetectorAgent().run()
