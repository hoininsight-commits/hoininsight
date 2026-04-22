import json
import re
from typing import List, Dict

class EventGenerator:
    """[TASK #100.1] 뉴스 헤드라인에서 결정론적으로 이벤트를 추출"""
    
    TYPE_KEYWORDS = {
        "SUPPLY_SHOCK": ["파업", "중단", "공급망", "병목", "셧다운", "strike", "disruption", "bottleneck"],
        "EARNINGS": ["실적", "어닝", "매출", "영업이익", "가이던스", "earnings", "revenue", "profit", "guidance"],
        "GEOPOLITICAL": ["전쟁", "휴전", "제재", "분쟁", "핵", "war", "ceasefire", "sanction", "conflict", "hormuz"],
        "POLICY": ["금리", "정부", "규제", "정책", "통화", "세금", "fed", "policy", "regulation", "rate", "tariff"],
        "LIQUIDITY": ["유입", "유출", "자금", "매수", "매도", "liquidity", "inflow", "outflow", "buyback"]
    }
    
    SECTOR_KEYWORDS = {
        "반도체": ["반도체", "삼성전자", "SK하이닉스", "nvidia", "tsmc", "hbm", "ai chip"],
        "에너지/유가": ["유가", "wti", "oil", "에너지", "crude", "gas"],
        "금융": ["은행", "금리", "금융", "bank", "interest", "fed"],
        "빅테크": ["애플", "마이크로소프트", "구글", "메타", "테슬라", "tech", "apple", "microsoft", "google", "meta", "tesla"]
    }

    def __init__(self):
        pass

    def generate(self, news_headlines: List[Dict]) -> List[Dict]:
        events = []
        for h in news_headlines:
            title = h.get("title", "").lower()
            summary = h.get("summary", "").lower()
            combined = title + " " + summary
            
            event_type = "UNKNOWN"
            for etype, keywords in self.TYPE_KEYWORDS.items():
                if any(kw.lower() in combined for kw in keywords):
                    event_type = etype
                    break
            
            if event_type == "UNKNOWN":
                continue
                
            sector_hints = []
            for sector, keywords in self.SECTOR_KEYWORDS.items():
                if any(kw.lower() in combined for kw in keywords):
                    sector_hints.append(sector)
            
            # Entity extraction (simple regex for capitalized words in English titles or known names)
            entity = "Market"
            # Simple heuristic for entity: look for common company names
            for _, keywords in self.SECTOR_KEYWORDS.items():
                for kw in keywords:
                    if kw.lower() in combined and len(kw) > 2:
                        entity = kw
                        break
                if entity != "Market": break

            events.append({
                "event": h.get("title"),
                "entity": entity,
                "event_type": event_type,
                "sector_hint": sector_hints,
                "impact_scope": "섹터" if sector_hints else "거시",
                "source_count": 1, # Base news count
                "recency_score": 1.0 # Current news
            })
            
        # Deduplicate and group similar events (for now, simple list)
        return events[:10] # Return top 10 events found
