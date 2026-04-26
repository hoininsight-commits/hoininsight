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
        
        # [v15.0 New Components]
        from src.topic_engine.strategy_mapper import WeeklyStrategyMapper
        from src.topic_engine.stock_analyst import StockAnalyst
        from src.topic_engine.arbiter import TopicArbiter
        self.strategy_mapper = WeeklyStrategyMapper()
        self.stock_analyst = StockAnalyst()
        self.arbiter = TopicArbiter()

    def run(self, raw_data: dict):
        print(f"🚀 Topic Selection Engine v15.0 (The Hunter's Logic) 가동")
        
        # 1. 데이터 추출
        sentiment_block = raw_data.get("sentiment", {})
        sentiment_data_inner = sentiment_block.get("data", {})
        if isinstance(sentiment_data_inner, dict) and "data" in sentiment_data_inner:
            news_headlines = sentiment_data_inner.get("data", {}).get("news_headlines", [])
        else:
            news_headlines = sentiment_data_inner.get("news_headlines", [])
            
        market_block = raw_data.get("market", {})
        market_data_inner = market_block.get("data", {})
        if isinstance(market_data_inner, dict) and "data" in market_data_inner:
            market_data = market_data_inner.get("data", {})
        else:
            market_data = market_data_inner
        
        dart_block = raw_data.get("dart", {})
        dart_data_inner = dart_block.get("data", {})
        if isinstance(dart_data_inner, dict) and "data" in dart_data_inner:
            dart_disclosures = dart_data_inner.get("data", {}).get("disclosures", [])
        else:
            dart_disclosures = dart_data_inner.get("disclosures", [])
        
        # 2. 후보 생성 및 [v15.1] 엄격한 오늘 날짜 필터링 (4월 26일)
        raw_events = self.event_builder.build_events(news_headlines, dart_disclosures)
        
        # [v15.1] '오늘(Today)' 발생한 핵심 이슈만 추출하여 최신성 극대화
        today_str = "2026-04-26"
        today_events = [e for e in raw_events if today_str in e.get("event", "") or e.get("is_breaking")]
        
        # 주간 전략 지도 제거 (사용자 요청)
        # StrategyMapper 호출 로직 삭제됨
        
        filtered_events = self.event_filter.filter(today_events if today_events else raw_events)
        signals = self.signal_builder.build_signals(market_data)
        
        # 3. 컨텍스트 강화 및 패키징
        enriched_events = self.context_enricher.enrich_events(filtered_events, market_data)
        all_candidates = self.packer.pack_all(enriched_events, signals)
        
        # 4. Social 데이터 결합
        social_candidates = self._create_social_candidates(raw_data)
        all_candidates.extend(social_candidates)
        
        # 5. [v15.1] 옥석 가리기 - DART 질적 분석 레이어
        # (기존 Hidden Gem 탐지 로직 유지)
        for cand in all_candidates:
            if cand.get("source") == "DART":
                disclosure_summary = cand.get("summary", "")
                company = cand.get("entity", ["Unknown"])[0]
                quality = self.stock_analyst.analyze_disclosure_quality(f"{cand['event']}\n{disclosure_summary}")
                if quality:
                    cand["survival_quality"] = quality
                    if quality.get("survival_score", 0) > 80:
                        cand["evidence_score"] += 0.5
                        cand["is_hidden_gem"] = True

        # 6. Hunter's Eye: Mismatch Detection
        for cand in all_candidates:
            ev_type = cand.get("candidate_type", "DATA")
            if ev_type in ["SOCIAL", "PRED_MARKET"]:
                cand["recency_score"] = 1.0
                continue
            cand["is_mismatch"] = False # 로직 간소화

        # 7. Axis Detection
        market_axis = self.axis_detector.detect_market_axis(all_candidates, market_data)
        
        # 8. 최종 선정 (Arbiter Priority - 오늘 최고의 이슈 1개에 집중)
        # 3일치가 아닌 오늘 가장 파괴적인 이슈를 선정하도록 유도
        arbiter_selection = self.arbiter.select_best(all_candidates[:10], market_axis)
        selection = arbiter_selection if arbiter_selection else {"MAIN": all_candidates[0] if all_candidates else None, "SECONDARY": [], "EARLY": []}
        
        # 9. Evidence Building & Why Hypothesis
        main_cand = selection.get("MAIN")
        if main_cand:
            social_data = raw_data.get("social", {})
            evidence_bundle = self.evidence_builder.build_evidence_bundle(main_cand, market_data, raw_events, social_data)
            main_cand["evidence_bundle"] = evidence_bundle

            # [v15.0] 메인 토픽에 대해서는 항상 가설 및 메커니즘 분석 수행
            if True: 
                print(f"  🧠 Generating Why Hypothesis for MAIN: {main_cand['event']}")
                hypothesis = self.why_generator.generate_hypothesis(evidence_bundle)
                if hypothesis:
                    main_cand["why_hypothesis"] = hypothesis.get("why_hypothesis", "N/A")
                    main_cand["mechanism"] = hypothesis.get("mechanism", "N/A")
                    main_cand["predictive_chain"] = hypothesis.get("predictive_chain", "N/A")
                    main_cand["historical_parallel"] = hypothesis.get("historical_parallel", "N/A")
                    if hypothesis.get("refined_title"):
                        main_cand["event"] = hypothesis["refined_title"]

            # 10. Stock & Sector Analysis
            stock_report = self.stock_analyst.analyze_stocks(main_cand, evidence_bundle)
            if stock_report:
                main_cand["stocks_analysis"] = stock_report

        self._save_json(selection, "topic_selection.json")
        print(f"  🏆 v15.0 Selection Complete: {selection['MAIN']['event'] if selection['MAIN'] else 'NONE'}")

        return selection


    def _save_json(self, data, filename):
        path = self.topic_dir / filename
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    def _create_social_candidates(self, raw_data):
        """[v12.0 Fast-Hunter] 소셜/예측 시장 데이터를 독립적인 토픽 후보로 생성"""
        social_data = raw_data.get("social", {})
        inner_data = social_data.get("data", {}).get("data", {})
        hn_posts = inner_data.get("hacker_news", [])
        poly_odds = inner_data.get("polymarket", [])
        
        candidates = []
        
        # 1. HN High Momentum (70 Points 이상으로 완화, Breaking 가중치)
        for post in hn_posts:
            points = post.get("points", 0)
            is_breaking = post.get("is_breaking", False)
            
            if points >= 70 or is_breaking:
                recency = 1.2 if is_breaking else 1.0
                candidates.append({
                    "candidate_id": f"soc_hn_{post.get('objectID', 'na')}",
                    "candidate_type": "SOCIAL",
                    "event": f"[SOCIAL_HOT] {post.get('title')}",
                    "entity": ["Community"],
                    "core_facts": [
                        {"name": "hn_points", "value": points, "mismatch": False}
                    ],
                    "recency_score": recency,
                    "evidence_score": min(1.0, points / 300.0), # 300P 이상이면 만점
                    "structure_axis": "flow",
                    "is_breaking": is_breaking,
                    "why_now": f"Hacker News에서 {points} Points 획득하며 커뮤니티 급상승"
                })
        
        # 2. Polymarket High Volume (24시간 거래량 기준)
        for bet in poly_odds:
            vol = bet.get("volume24h", 0)
            is_breaking = bet.get("is_breaking", False)
            
            if vol > 100000 or is_breaking: # $100k 이상 거래로 완화
                recency = 1.2 if is_breaking else 1.0
                candidates.append({
                    "candidate_id": f"soc_poly_{bet.get('title', 'na')[:10]}",
                    "candidate_type": "PRED_MARKET",
                    "event": f"[PRED_MARKET] {bet.get('title')}",
                    "entity": ["Prediction"],
                    "core_facts": [
                        {"name": "yes_prob", "value": bet.get("outcomes", [{}])[0].get("probability", 0), "mismatch": False},
                        {"name": "volume24h", "value": f"${vol/1000:.0f}k", "mismatch": False}
                    ],
                    "recency_score": recency,
                    "evidence_score": min(1.0, vol / 1000000.0), # $1M 이상이면 만점
                    "structure_axis": "flow",
                    "is_breaking": is_breaking,
                    "why_now": f"예측 시장에서 24시간 내 {vol/1000:.0f}k 달러 거래되며 자본 집중"
                })
                
        return candidates
