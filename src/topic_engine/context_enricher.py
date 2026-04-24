from typing import List, Dict

class ContextEnricher:
    """[TASK #102.3] 이벤트 맞춤형 데이터 매핑 및 컨텍스트 강화 (v2.0 자율 탐지형)"""

    def __init__(self):
        pass

    def enrich_events(self, events: List[Dict], market_data: Dict) -> List[Dict]:
        """
        [v2.0] 하드코딩 없이 시장 데이터와 이벤트를 동적으로 연결합니다.
        """
        stats = market_data.get("multi_period_stats", {})
        enriched = []
        
        for ev in events:
            text = (ev["event"] + " " + ev.get("summary", "")).lower()
            entities = [e.lower() for e in ev.get("entity", [])]
            
            # 1. 자율 키워드 매핑 (Discovery)
            related_keys = set()
            
            # 모든 시장 지수 키값을 돌며 텍스트에 포함되어 있는지 확인
            for key in stats.keys():
                if key.lower() in text or any(ent in key.lower() for ent in entities):
                    related_keys.add(key)
            
            # 2. 관련 데이터가 너무 적으면 벤치마크 지수 강제 주입 (Context 보강)
            if len(related_keys) < 2:
                if any(kw in text for kw in ["한국", "국내", "코스피", "코스닥", "삼성", "hy", "kr"]):
                    related_keys.update(["kospi", "kosdaq"])
                else:
                    related_keys.update(["sp500", "nasdaq"])
            
            # 3. 데이터 추출
            market_context = []
            for key in related_keys:
                if key in stats:
                    s = stats[key]
                    market_context.append({
                        "name": key,
                        "value": s.get("current", 0.0),
                        "change": s.get("chg_5d", 0.0) if s.get("chg_5d") is not None else 0.0,
                        "z_score": s.get("z_score_20d", 0.0) if s.get("z_score_20d") is not None else 0.0
                    })
            
            # [v2.0 RULE] 하나라도 데이터가 연결되면 일단 통과
            if market_context:
                ev["related_market_data"] = {"assets": market_context}
                enriched.append(ev)
                
        return enriched
