from typing import List, Dict

class ContextEnricher:
    """[TASK #102.3] 이벤트 맞춤형 데이터 매핑 및 컨텍스트 강화 (v1.1)"""

    # 이벤트 타입별 핵심 자산 매핑
    TYPE_ASSET_MAP = {
        "GEOPOLITICAL": ["wti_oil", "gold", "vix", "usd_krw"],
        "POLICY": ["us10y", "usd_krw", "nasdaq", "sp500"],
        "EARNINGS": ["nasdaq", "sp500", "kospi"], # 개별 기업 데이터는 stats에 없을 수 있어 지수 위주
        "SUPPLY_SHOCK": ["wti_oil", "brent", "gold"],
        "LIQUIDITY": ["kospi", "nasdaq", "vix"]
    }

    # 엔티티별 핵심 자산 매핑
    ENTITY_ASSET_MAP = {
        "Nvidia": ["nasdaq", "sp500"],
        "Samsung Electronics": ["kospi", "usd_krw"],
        "Fed": ["us10y", "usd_krw", "sp500"],
        "BHP": ["kospi", "vix"], # 원자재 관련 대형주 영향
        "UK": ["kospi", "vix"], # 연기금 이슈 등 매크로 영향
        "US": ["sp500", "nasdaq", "us10y"],
        "China": ["kospi", "wti_oil"]
    }

    def __init__(self):
        pass

    def enrich_events(self, events: List[Dict], market_data: Dict) -> List[Dict]:
        stats = market_data.get("multi_period_stats", {})
        enriched = []
        
        for ev in events:
            event_type = ev.get("event_type")
            entities = ev.get("entity", [])
            
            # 1. 관련 자산 리스트 구성 (Strict Mapping)
            related_keys = set()
            
            # 타입 기반 매핑
            related_keys.update(self.TYPE_ASSET_MAP.get(event_type, []))
            
            # 엔티티 기반 매핑
            for ent in entities:
                related_keys.update(self.ENTITY_ASSET_MAP.get(ent, []))
            
            # 2. 데이터 추출
            market_context = []
            for key in related_keys:
                if key in stats:
                    s = stats[key]
                    market_context.append({
                        "name": key,
                        "value": s.get("current"),
                        "change": s.get("chg_5d"),
                        "volatility": s.get("z_score_20d")
                    })
            
            # [RULE] 최소 2개 이상의 관련 자산 연결 필수
            if len(market_context) >= 2:
                ev["related_market_data"] = {"assets": market_context}
                enriched.append(ev)
            else:
                # 관련 데이터가 부족하면 탈락
                continue
                
        return enriched
