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
        
        # 3. Candidate Packaging (Market-based)
        all_candidates = self.packer.pack_all(enriched_events, signals)
        
        # 4. [NEW] Social Topic Generation (Social-based)
        social_candidates = self._create_social_candidates(raw_data)
        print(f"  📢 Social Engine: {len(social_candidates)} candidates generated from HN/Polymarket")
        all_candidates.extend(social_candidates)
        
        # 5. Hunter's Eye: Mismatch & Confluence Analysis
        for cand in all_candidates:
            ev_type = cand.get("candidate_type", "DATA")
            
            # [Social Confluence Bonus]
            # 만약 소셜 후보가 뉴스나 시장 지표와 겹치면 점수 대폭 가산
            if ev_type in ["SOCIAL", "PRED_MARKET"]:
                # 소셜 데이터는 기본적으로 높은 recency 부여
                cand["recency_score"] = 1.0
                continue

            market_cand_data = cand.get("market_data", {})
            price_chg = 0
            if market_cand_data:
                first_metric = list(market_cand_data.keys())[0]
                price_chg = market_cand_data[first_metric].get("chg_5d", 0)
            
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

        # 6. 정성 평가 (Top 10 candidates)
        # filtered_candidates(축에 속하거나 강력한 것들) 중 상위 10개 추출
        filtered_candidates.sort(key=lambda x: (x["recency_score"] + x["evidence_score"]), reverse=True)
        top_candidates = filtered_candidates[:10]
        evaluations = self.evaluator.evaluate_all(top_candidates)
        
        # [NEW] Social & Prediction Data Load
        social_data = raw_data.get("social", {})

        from src.topic_engine.arbiter import TopicArbiter
        self.arbiter = TopicArbiter()

        # 7. 랭킹 및 최종 선정 (Arbiter Priority Mode)
        # Ranker는 후보군을 정렬하는 용도로 사용
        ranked_results = self.ranker.rank(all_candidates, evaluations, market_axis)
        
        # Arbiter가 상위 후보들 중 최종 MAIN을 동적으로 결정
        # Ranker에서 점수순으로 정렬된 상위 15개를 아비터에게 전달
        top_candidates = all_candidates[:15]
        
        arbiter_selection = self.arbiter.select_best(top_candidates, market_axis)
        
        if arbiter_selection:
            selection = arbiter_selection
        else:
            selection = ranked_results
        
        # 8. Evidence Building & Why Hypothesis
        main_cand = selection.get("MAIN")
        if main_cand:
            # [HUNTER'S EYE] MAIN 토픽은 증거 꾸러미 생성 시 social_data 결합
            evidence_bundle = self.evidence_builder.build_evidence_bundle(main_cand, market_data, raw_events, social_data)
            main_cand["evidence_bundle"] = evidence_bundle

            if main_cand.get("explainability_score", 0) >= 0.1:
                print(f"  🧠 Generating Why Hypothesis for MAIN: {main_cand['event']}")
                hypothesis = self.why_generator.generate_hypothesis(evidence_bundle)
                if hypothesis:
                    print(f"  🔍 Gemini Causal Insight: {hypothesis.get('predictive_chain')}")
                    main_cand["why_hypothesis"] = hypothesis.get("why_hypothesis", "N/A")
                    main_cand["mechanism"] = hypothesis.get("mechanism", "N/A")
                    main_cand["hypothesis_confidence"] = hypothesis.get("confidence", "Low")
                    main_cand["predictive_chain"] = hypothesis.get("predictive_chain", "N/A")
                    if hypothesis.get("refined_title"):
                        main_cand["event"] = hypothesis["refined_title"]
                else:
                    print(f"  ⚠️ Gemini returned empty hypothesis.")
            else:
                print(f"  ⏩ Skipping Why Hypothesis (Explainability: {main_cand.get('explainability_score', 0)})")
                main_cand["why_hypothesis"] = "Analysis pending higher explainability score"
                main_cand["mechanism"] = "Correlative shift observed"

            # 9. [NEW] Agent-04: Stock & Sector Linkage Analysis (v14.0)
            from src.topic_engine.stock_analyst import StockAnalyst
            self.stock_analyst = StockAnalyst()
            stock_report = self.stock_analyst.analyze_stocks(main_cand, evidence_bundle)
            if stock_report:
                main_cand["stocks_analysis"] = stock_report
                all_stocks = []
                for sector in stock_report.get("sectors", []):
                    for s in sector.get("stocks", []):
                        all_stocks.append({
                            "name": s["name"],
                            "reason": s.get("linkage", sector.get("reason", ""))
                        })
                main_cand["stocks"] = all_stocks

        self._save_json(selection, "topic_selection.json")
        
        if selection["MAIN"]:
            print(f"  🏆 MAIN Topic: {selection['MAIN']['event']} ({selection['MAIN']['structure_axis']})")
            
        # [PUBLISH] 결과 물리적 저장 (후속 배포 스크립트 연동)
        save_path = self.base_dir / "data/topics/topic_selection.json"
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_text(json.dumps(selection, ensure_ascii=False, indent=2))
        print(f"  ✅ Topic selection saved to {save_path}")

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
