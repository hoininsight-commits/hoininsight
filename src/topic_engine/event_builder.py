from typing import List, Dict
import re

class EventBuilder:
    """[TASK #102.2] 정교화된 엔티티 추출기 및 이벤트 빌더 (v1.1)"""

    TYPE_KEYWORDS = {
        "SUPPLY_SHOCK": ["파업", "중단", "공급망", "병목", "셧다운", "strike", "disruption", "bottleneck", "shortage", "squeezed", "blockade", "품귀"],
        "POLICY": ["금리", "정부", "규제", "정책", "통화", "세금", "fed", "policy", "regulation", "rate", "tariff", "stimulus", "trump", "administration", "swap line", "스왑"],
        "EARNINGS": ["실적", "어닝", "매출", "영업이익", "가이던스", "earnings", "revenue", "profit", "guidance", "eps", "dividend", "quarterly", "어닝서프라이즈"],
        "GEOPOLITICAL": ["전쟁", "휴전", "제재", "분쟁", "핵", "war", "ceasefire", "sanction", "conflict", "hormuz", "geopolitical", "iran", "crisis", "middle east", "중동"],
        "LIQUIDITY": ["유입", "유출", "자금", "매수", "매도", "liquidity", "inflow", "outflow", "buyback", "quantitative", "pension", "fund", "private assets", "수급", "외인", "기관", "개미"]
    }

    # [TASK #092] 비정형 슬랭 맵 (Normalize entities)
    SLANG_MAP = {
        "삼전": "삼성전자",
        "닉스": "SK하이닉스",
        "삼전닉스": ["삼성전자", "SK하이닉스"],
        "전차": ["삼성전자", "현대차"],
        "삼바": "삼성바이오로직스",
        "에코": "에코프로",
        "엔솔": "LG에너지솔루션",
        "현차": "현대차",
        "기차": "기아",
        "미장": "미국 증시",
        "국장": "한국 증시",
        "개미": "개인투자자",
        "외인": "외국인투자자",
        "기관": "기관투자자"
    }

    def _extract_entities_dynamically(self, text: str) -> List[str]:
        """텍스트에서 따옴표, 대문자 조합, 혹은 주요 명사를 통해 엔티티를 동적으로 추출"""
        # [HUNTER DNA] 하드코딩 없이 텍스트 패턴으로만 추출
        entities = []
        
        # 1. 따옴표 안의 단어 (예: '삼성전자', "Nvidia")
        quoted = re.findall(r'[\'"]([^\'"]+)[\'"]', text)
        entities.extend(quoted)
        
        # 2. 대문자로 시작하는 연속된 단어 (영어 엔티티용)
        capitalized = re.findall(r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b', text)
        entities.extend(capitalized)
        
        # 3. [ ] 로 묶인 단어 (공시 등에서 자주 등장)
        bracketed = re.findall(r'\[([^\]]+)\]', text)
        for b in bracketed:
            if b not in ["뉴스", "공시", "단독", "속보"]:
                entities.append(b)

        # 4. [NEW] Slang Mapping (삼전닉스 등 대응)
        for slang, formal in self.SLANG_MAP.items():
            if slang in text:
                if isinstance(formal, list):
                    entities.extend(formal)
                else:
                    entities.append(formal)
                
        return list(set(entities)) if entities else ["Market"]

    def __init__(self):
        pass

    def build_events(self, news_headlines: List[Dict], dart_disclosures: List[Dict] = None) -> List[Dict]:
        events = []
        
        # 1. 뉴스 이벤트 빌딩
        for h in news_headlines:
            title = h.get("title", "")
            summary = h.get("summary", "")
            if not title: continue
            
            combined_text = (title + " " + summary).lower()
            
            # Event Type 분류 (v2.0: Non-Discarding Policy)
            event_type = "UNCATEGORIZED"
            for etype, keywords in self.TYPE_KEYWORDS.items():
                if any(kw.lower() in combined_text for kw in keywords):
                    event_type = etype
                    break

            # Entity 동적 추출
            entities = self._extract_entities_dynamically(combined_text)
            
            # [HUNTER'S EYE] Deep Detail 보너스 및 수치 강조
            intensity_bonus = 0.0
            if "[DEEP_DETAIL]" in summary:
                intensity_bonus += 0.5
                # 수치 데이터가 포함되어 있는지 확인
                if re.search(r'\d+', summary):
                    intensity_bonus += 0.3
            
            # 텍스트 길이와 느낌표 등으로 강도 보너스 (하드코딩 키워드 대체)
            if "!" in combined_text or combined_text.count("?") > 1:
                intensity_bonus += 0.1
            
            events.append({
                "event": title,
                "summary": summary,
                "entity": entities,
                "event_type": event_type,
                "source": "NEWS",
                "recency_score": 1.0 + intensity_bonus,
                "is_preemptive": any(re.search(r"\d+월|\d+일|화요일|expected", combined_text) for _ in [1])
            })

        # 2. DART 공시 이벤트 빌딩 (NEW)
        if dart_disclosures:
            for d in dart_disclosures:
                title = d.get("title", "")
                company = d.get("company", "")
                amount = d.get("amount", "")
                
                # 수치가 확인된 공시만 고품질 이벤트로 취급
                is_detailed = amount != "수치 확인 중"
                
                # 공시 유형 매핑
                event_type = "EARNINGS" # 기본
                if "공급계약" in title or "판매" in title:
                    event_type = "LIQUIDITY" # 매출/자금 유입 성격
                elif "투자" in title:
                    event_type = "POLICY" # 기업 정책/전략
                
                events.append({
                    "event": f"[{company}] {title}",
                    "summary": f"금액: {amount} / 링크: {d.get('link')}",
                    "entity": [company],
                    "event_type": event_type,
                    "source": "DART",
                    "recency_score": 1.5 if is_detailed else 1.1, # 수치 있는 공시는 최우선순위
                    "is_preemptive": False
                })
            
        return events
