
from typing import List, Dict

class EvidenceBuilder:
    """[NEW] Evidence Bundle Layer: 시장 반응, 뉴스, 지표를 결합하여 증거 꾸러미 생성"""

    def __init__(self):
        pass

    def build_evidence_bundle(self, candidate: Dict, market_data: Dict, events: List[Dict]) -> Dict:
        axis = candidate.get("structure_axis", "unknown")
        core_facts = candidate.get("core_facts", [])
        
        # 1. Market Reaction
        reaction = {
            "main_asset": core_facts[0].get("name") if core_facts else "Market",
            "intensity": core_facts[0].get("change") if core_facts else 0.0,
            "other_reactions": [f"{f['name']}: {f['change']}%" for f in core_facts[1:]]
        }

        # 2. Related Events (뉴스/공시 결합, 수치 포함된 것 우선)
        related_events = []
        axis_keywords = {
            "rates": ["fed", "inflation", "cpi", "yield", "rates"],
            "liquidity": ["vix", "volatility", "dollar", "liquidity", "crunch", "inflation"],
            "geopolitics": ["war", "strike", "tensions", "oil", "wti", "gold", "middle east"],
            "supply_chain": ["shipping", "port", "strike", "oil", "supply", "공급망", "병목"],
            "policy": ["stimulus", "government", "policy", "china", "tax", "정부", "투자"],
            "flow": ["nasdaq", "nvidia", "earnings", "stock", "kospi", "selling", "buying", "stimulus", "china", "policy", "실적", "공급계약"]
        }
        
        keywords = axis_keywords.get(axis, [])
        
        # 고품질 이벤트(수치 포함) 우선 정렬
        sorted_events = sorted(events, key=lambda x: x.get("recency_score", 0), reverse=True)
        
        for e in sorted_events:
            title = e.get("event", "").lower()
            summary = e.get("summary", "")
            source = e.get("source", "NEWS")
            
            # 키워드 매칭 또는 고득점 이벤트 선정
            if any(kw in title for kw in keywords) or e.get("recency_score", 0) > 1.2:
                detail = f"[{source}] {e.get('event')} - {summary}"
                related_events.append(detail)
            
            if len(related_events) >= 5: # 증거 개수 상향 (3 -> 5)
                break
        
        # 3. Supporting Assets (동일 축 내의 다른 자산 반응)
        stats = market_data.get("multi_period_stats", {})
        supporting = []
        for name, data in stats.items():
            if abs(data.get("z_score_20d", 0)) > 1.5 and name != reaction["main_asset"]:
                supporting.append(f"{name}: {data.get('chg_5d', 0)}%")
        
        # 4. Contradictions (반대 방향 혹은 설명되지 않는 움직임)
        contradictions = []
        if axis == "rates" and reaction["intensity"] > 0:
            if stats.get("nasdaq", {}).get("chg_5d", 0) > 0.5:
                contradictions.append("Interest rates rising but NASDAQ also rising")

        # 5. [NEW] Event -> Market Link (v2.1)
        event_market_link = self.build_event_market_link(axis, related_events)
        
        return {
            "axis": axis,
            "market_reaction": reaction,
            "related_events": related_events,
            "supporting_assets": supporting[:3],
            "contradictions": contradictions if contradictions else ["No clear contradictions found"],
            "event_market_link": event_market_link
        }

    def build_event_market_link(self, axis: str, events: List[str]) -> List[str]:
        """간단한 Rule 기반의 Event-Market 연결성 가이드 생성"""
        if not events:
            return []
            
        links = []
        if axis == "policy" or axis == "rates":
            links.append("policy/rates → bond yields → dollar index → growth stocks")
        elif axis == "geopolitics":
            links.append("geopolitics → oil prices → inflation expectations → bond yields")
        elif axis == "liquidity":
            links.append("liquidity/volatility → risk-off sentiment → safe-haven demand")
        elif axis == "supply_chain":
            links.append("supply_chain disruption → supply shortage → commodity prices up")
        elif axis == "flow":
            links.append("investor sentiment → sector rotation → capital flow → equity performance")
        
        # 특정 키워드에 따른 추가 링크
        event_text = " ".join(events).lower()
        if "stimulus" in event_text or "china" in event_text:
            links.append("stimulus → market liquidity up → equity positive")
        if "earnings" in event_text or "nvidia" in event_text:
            links.append("earnings/tech → investor sentiment → capital flow → equity positive")
            
        return links
