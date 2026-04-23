import json
import os
from pathlib import Path
from datetime import datetime
from src.topic_engine.event_builder import EventBuilder
from src.topic_engine.event_filter import EventFilter
from src.topic_engine.signal_builder import SignalBuilder
from src.topic_engine.context_enricher import ContextEnricher
from src.topic_engine.candidate_packer import CandidatePacker
from src.topic_engine.llm_evaluator import TopicEvaluator
from src.topic_engine.topic_ranker import TopicRanker
from src.topic_engine.axis_detector import AxisDetector
from src.topic_engine.evidence_builder import EvidenceBuilder
from src.topic_engine.why_generator import WhyGenerator

class TopicSelectionEngine:
    """[TASK #103] 통합 토픽 선정 엔진 v2.1 (Axis-First + Why Hypothesis)"""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.today = datetime.now().strftime("%Y%m%d")
        self.topic_dir = self.base_dir / "data/topics"
        self.topic_dir.mkdir(parents=True, exist_ok=True)
        
        self.event_builder = EventBuilder()
        self.event_filter = EventFilter()
        self.signal_builder = SignalBuilder()
        self.context_enricher = ContextEnricher()
        self.packer = CandidatePacker()
        self.axis_detector = AxisDetector()
        self.evaluator = TopicEvaluator()
        self.ranker = TopicRanker()
        self.evidence_builder = EvidenceBuilder()
        self.why_generator = WhyGenerator()

    def run(self, raw_data: dict):
        print(f"🚀 Topic Selection Engine v2.0 (Axis-First Build) 가동")
        
        # 1. 데이터 추출
        sentiment_block = raw_data.get("sentiment", {})
        # [FIX] Collector v3.0의 중첩 구조 대응 (sentiment -> data -> data)
        sentiment_data_inner = sentiment_block.get("data", {})
        if isinstance(sentiment_data_inner, dict) and "data" in sentiment_data_inner:
            news_headlines = sentiment_data_inner.get("data", {}).get("news_headlines", [])
        else:
            news_headlines = sentiment_data_inner.get("news_headlines", [])
        market_block = raw_data.get("market", {})
        # [FIX] Collector v3.0의 중첩 구조 대응 (market -> data -> data)
        market_data_inner = market_block.get("data", {})
        if isinstance(market_data_inner, dict) and "data" in market_data_inner:
            market_data = market_data_inner.get("data", {})
        else:
            market_data = market_data_inner
        
        # [FIX] DART 데이터 추출
        dart_block = raw_data.get("dart", {})
        dart_data_inner = dart_block.get("data", {})
        if isinstance(dart_data_inner, dict) and "data" in dart_data_inner:
            dart_disclosures = dart_data_inner.get("data", {}).get("disclosures", [])
        else:
            dart_disclosures = dart_data_inner.get("disclosures", [])
        
        # 2. 후보 생성 (Deterministic)
        raw_events = self.event_builder.build_events(news_headlines, dart_disclosures)
        filtered_events = self.event_filter.filter(raw_events)
        signals = self.signal_builder.build_signals(market_data)
        
        # 3. 컨텍스트 강화 (Strict Mapping)
        enriched_events = self.context_enricher.enrich_events(filtered_events, market_data)
        
        # 4. 패키징
        all_candidates = self.packer.pack_all(enriched_events, signals)
        
        # [NEW] Hunter's Eye: Price-News Mismatch 탐지
        for cand in all_candidates:
            ev_type = cand.get("event_type")
            price_chg = 0
            # 대표 지표의 5일 변화율 확인
            if cand.get("market_data"):
                # 첫 번째 지표의 변화율을 기준점으로 삼음
                first_metric = list(cand["market_data"].keys())[0]
                price_chg = cand["market_data"][first_metric].get("chg_5d", 0)
            
            # 모순 판별 (예: 금리 인하 뉴스인데 국채 금리 폭등 / 실적 악재인데 주가 폭등 등)
            # 여기서는 단순화하여 [뉴스 유형]과 [가격 변화]의 방향성을 대조
            is_mismatch = False
            if ev_type in ["EARNINGS", "SUPPLY_SHOCK", "GEOPOLITICAL"]: # 보통 악재성
                if price_chg > 2.0: # 그런데 가격은 크게 오름
                    is_mismatch = True
            elif ev_type == "POLICY": # 정책/금리 관련
                if abs(price_chg) > 3.0: # 변동성이 매우 큼 (해석의 충돌)
                    is_mismatch = True
            
            cand["is_mismatch"] = is_mismatch
            if is_mismatch:
                print(f"  🕵️‍♂️ Hunter's Eye: Mismatch detected for '{cand['event']}' (Price Chg: {price_chg:+.2f}%)")

        initial_count = len(all_candidates)
        
        if not all_candidates:
            print("  ⚠️ No valid candidates found. Skipping Axis detection.")
            return {"MAIN": None, "SECONDARY": [], "EARLY": [], "market_axis": None}

        # 5. [NEW] Axis Detection & Filtering
        market_axis = self.axis_detector.detect_market_axis(all_candidates, market_data)
        print(f"  🎯 Market Axis Detected: Primary={market_axis['primary_axis']}, Secondary={market_axis['secondary_axis']}")
        
        filtered_candidates = []
        allowed_axes = [market_axis["primary_axis"], market_axis["secondary_axis"]]
        
        for cand in all_candidates:
            # Preliminary filtering based on axis
            if cand.get("structure_axis") in allowed_axes:
                filtered_candidates.append(cand)
            elif cand.get("evidence_score", 0) >= 0.9: # Exception for very strong candidates
                # Keep them but they will likely be EARLY
                filtered_candidates.append(cand)
        
        remaining_count = len(filtered_candidates)
        print(f"  ✅ Axis Filtering: {initial_count} -> {remaining_count}")
        self._save_json(market_axis, "market_axis.json")
        self._save_json(filtered_candidates, "topic_candidates.json")
        
        if not filtered_candidates:
            return {"MAIN": None, "SECONDARY": [], "EARLY": [], "market_axis": market_axis}

        # 6. 정성 평가 (Heuristic-based, v2.2부터 LLM 호출 금지)
        filtered_candidates.sort(key=lambda x: (x["recency_score"] + x["evidence_score"]), reverse=True)
        top_candidates = filtered_candidates[:10]
        
        evaluations = self.evaluator.evaluate_all(top_candidates)
        self._save_json(evaluations, "topic_evaluations.json")
        
        # 7. 최종 랭킹 및 선정 (Axis 경쟁 로직 포함)
        selection = self.ranker.rank(filtered_candidates, evaluations, market_axis)
        selection["market_axis"] = market_axis
        selection["filtered_candidates_count"] = initial_count
        selection["remaining_candidates_count"] = remaining_count

        # 8. [CRITICAL FIX] FINAL MAIN 선정 후 LLM 호출 (v2.2)
        # 규칙: 하루 총 LLM 호출 3회 제한, MAIN 토픽만 Why 생성
        MAX_LLM_CALL = 3
        llm_call_count = 0
        
        main_cand = selection.get("MAIN")
        if main_cand:
            # [HUNTER'S EYE] MAIN 토픽은 점수와 상관없이 증거 꾸러미 강제 생성 (Fact-First)
            evidence_bundle = self.evidence_builder.build_evidence_bundle(main_cand, market_data, raw_events)
            main_cand["evidence_bundle"] = evidence_bundle

            if main_cand.get("explainability_score", 0) >= 5.0:
                # Why Hypothesis 생성 (LLM 호출 필요)
                if not evidence_bundle.get("related_events"):
                    print(f"  ⏩ Skipping Why Hypothesis (No related events found)")
                    main_cand["why_hypothesis"] = "Insufficient evidence"
                    main_cand["mechanism"] = "No clear event-driven mechanism"
                elif llm_call_count >= MAX_LLM_CALL:
                    print(f"  ⏩ Skipping Why Hypothesis (MAX_LLM_CALL reached)")
                    main_cand["why_hypothesis"] = "LLM limit reached"
                    main_cand["mechanism"] = "Analysis skipped"
                else:
                    print(f"  🧠 Generating Why Hypothesis for MAIN")
                    hypothesis = self.why_generator.generate_hypothesis(evidence_bundle)
                    llm_call_count += 1
                    if hypothesis:
                        main_cand["why_hypothesis"] = hypothesis["why_hypothesis"]
                        main_cand["mechanism"] = hypothesis["mechanism"]
                        main_cand["hypothesis_confidence"] = hypothesis["confidence"]
            else:
                print(f"  ⏩ Skipping Why Hypothesis (Explainability: {main_cand.get('explainability_score', 0)})")
                main_cand["why_hypothesis"] = "Analysis pending higher explainability score"
                main_cand["mechanism"] = "Correlative shift observed"

        self._save_json(selection, "topic_selection.json")
        
        if selection["MAIN"]:
            print(f"  🏆 MAIN Topic: {selection['MAIN']['event']} ({selection['MAIN']['structure_axis']})")
            
        return selection


    def _save_json(self, data, filename):
        path = self.topic_dir / filename
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
