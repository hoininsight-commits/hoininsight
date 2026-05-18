import json
import re
from collections import Counter
from pathlib import Path
from typing import Dict, List, Any

class DeterministicTopicEngine:
    """[v27.0] Deterministic Frequency Engine
    Gemini 장애 또는 한도 초과 시, 수집된 로우 데이터의 통계적 빈도를 기반으로 핵심 이슈를 도출함.
    """

    def __init__(self):
        self.stopwords = set([
            "은", "는", "이", "가", "에", "에서", "로", "으로", "과", "와", "을", "를", "의", "및", "등", "한", "수", "더", "위", 
            "년", "월", "일", "원", "달러", "억", "조", "대해", "대한", "위해", "위한", "기자", "뉴스", "속보", "종합", 
            "특징주", "마감", "포토", "부문", "대상", "수상", "브랜드", "고객충성도", "출시", "공개", "진행", "발표", "포착", "포함", "요약",
            "the", "a", "an", "in", "on", "at", "for", "to", "of", "and", "with", "is", "are", "be", "by", "from", 
            "as", "it", "that", "this", "they", "its", "has", "have", "will", "new", "how", "what", "why", "who", 
            "when", "where", "not", "today", "now", "market", "says", "said", "first", "more", "after", "before", "over"
        ])
        
        # 가중치 설정
        self.weights = {
            "dart": 3.0,      # 공시는 가장 확실한 팩트
            "premium": 2.0,   # 프리미엄 매체 뉴스
            "social": 1.5,    # 소셜 트렌드
            "normal": 1.0     # 일반 뉴스
        }

    def analyze(self, raw_dir: Path) -> Dict[str, Any]:
        """로우 데이터 폴더를 분석하여 최상위 토픽 1개를 도출"""
        print(f"  🔍 [DeterministicEngine] Analyzing statistics in {raw_dir}...")
        
        all_entities = Counter()
        source_data = {}
        
        # 1. 데이터 로드
        files = ["sentiment.json", "dart.json", "social.json"]
        for f in files:
            p = raw_dir / f
            if p.exists():
                try:
                    source_data[f] = json.loads(p.read_text(encoding='utf-8'))
                except: pass

        if not source_data:
            return {}

        # 2. 엔티티 추출 및 빈도 계산
        # 2-1. Sentiment (News)
        if "sentiment.json" in source_data:
            headlines = source_data["sentiment.json"].get("data", {}).get("news_headlines", [])
            for h in headlines:
                title = h.get("title", "")
                source = h.get("source", "")
                weight = self.weights["premium"] if any(p in source for p in ["CNBC", "Bloomberg", "Reuters", "FT"]) else self.weights["normal"]
                
                words = self._extract_keywords(title)
                for w in words:
                    all_entities[w] += weight

        # 2-2. DART (Disclosure)
        if "dart.json" in source_data:
            disclosures = source_data["dart.json"].get("data", {}).get("disclosures", [])
            for d in disclosures:
                title = d.get("report_nm", "")
                corp = d.get("corp_name", "")
                
                # 종목명은 매우 높은 가중치
                if corp:
                    all_entities[corp] += self.weights["dart"] * 2
                
                words = self._extract_keywords(title)
                for w in words:
                    all_entities[w] += self.weights["dart"]

        # 2-3. Social
        if "social.json" in source_data:
            for skey in ["polymarket", "hacker_news"]:
                items = source_data["social.json"].get(skey, [])
                for item in items:
                    title = item.get("title", "")
                    words = self._extract_keywords(title)
                    for w in words:
                        all_entities[w] += self.weights["social"]

        # 3. 최상위 키워드 기반 토픽 구성
        common = all_entities.most_common(15)
        if not common:
            return {}

        # 상위 1~3개 키워드를 조합하여 가상 토픽 생성
        top_keywords = [item[0] for item in common[:5]]
        main_keyword = top_keywords[0]
        
        print(f"  🎯 [DeterministicEngine] Top Keywords: {top_keywords}")

        # 4. 결과 빌드 (Arbiter/Writer 호환 포맷)
        # 실제 뉴스나 공시 중에서 이 키워드를 포함하는 가장 점수 높은 항목 찾기
        best_title = f"[데이터 통계] {main_keyword} 중심 시장 변화 포착"
        best_rationale = f"수집된 {len(all_entities)}개의 데이터 노드 중 '{main_keyword}'(빈도: {all_entities[main_keyword]:.1f})가 가장 강력한 연결 고리로 포착되었습니다."
        
        return {
            "topic": best_title,
            "event": best_title,
            "arbiter_rationale": best_rationale,
            "hunter_insight": f"현재 {', '.join(top_keywords[1:4])}와(과) 연계된 수급 쏠림이 통계적으로 유의미한 수준입니다.",
            "data_chain": f"통계적 우위 키워드: {', '.join([f'{k}({v:.1f})' for k, v in common[:5]])}",
            "evidence": self._get_evidence_snippets(main_keyword, source_data),
            "tier": "MAIN/TIER_1",
            "source": "DETERMINISTIC_STATISTICS",
            "stocks": self._find_related_stocks(main_keyword, source_data)
        }

    def _get_evidence_snippets(self, keyword: str, source_data: Dict) -> List[Dict]:
        """주요 키워드와 연관된 실제 헤드라인/공시명 및 링크 추출 (저인망식 검색)"""
        snippets = [] # 리스트로 변경하여 순서 유지 및 복합 데이터 저장
        seen_texts = set()
        target_kw = keyword.lower()
        
        # 모든 데이터 파일(DART, News, Social)을 순회하며 키워드 포함 문장 수집
        for file_name, content in source_data.items():
            self._recursive_find_with_link(content, target_kw, snippets, seen_texts, file_name)
            if len(snippets) >= 8: break
                
        return snippets[:6]

    def _recursive_find_with_link(self, data: Any, keyword: str, snippets: list, seen_texts: set, source_tag: str, parent_link: str = None):
        """JSON 구조를 파고들며 키워드와 연관된 텍스트 및 링크를 수집"""
        if isinstance(data, str):
            if keyword in data.lower() and len(data) > 10 and data not in seen_texts:
                prefix = "[DART]" if "dart" in source_tag else "[NEWS]" if "sentiment" in source_tag else "[SOCIAL]"
                snippets.append({
                    "text": f"{prefix} {data[:100].strip()}",
                    "url": parent_link
                })
                seen_texts.add(data)
        elif isinstance(data, list):
            for item in data:
                self._recursive_find_with_link(item, keyword, snippets, seen_texts, source_tag, parent_link)
                if len(snippets) >= 8: return
        elif isinstance(data, dict):
            # 현재 딕셔너리에서 링크 후보 찾기
            current_link = data.get("link") or data.get("url") or data.get("href") or parent_link
            
            # 우선순위 필드 검사
            priority_keys = ["title", "report_nm", "corp_name"]
            for pk in priority_keys:
                val = data.get(pk)
                if val and isinstance(val, str) and keyword in val.lower() and val not in seen_texts:
                    prefix = "[DART]" if "dart" in source_tag else "[NEWS]" if "sentiment" in source_tag else "[SOCIAL]"
                    snippets.append({
                        "text": f"{prefix} {val[:100].strip()}",
                        "url": current_link
                    })
                    seen_texts.add(val)
                    if len(snippets) >= 8: return
            
            # 나머지 필드 탐색
            for k, v in data.items():
                if k not in priority_keys:
                    self._recursive_find_with_link(v, keyword, snippets, seen_texts, source_tag, current_link)
                if len(snippets) >= 8: return

    def _extract_keywords(self, text: str) -> List[str]:
        # 1. 숫자와 특수문자가 섞인 단어 (날짜 등) 제거를 위한 정규식
        # 한글 및 영어 단어 추출 (2자 이상)
        words = re.findall(r'[a-zA-Z가-힣]{2,}', text)
        
        filtered = []
        for w in words:
            # 불용어 체크
            if w.lower() in self.stopwords:
                continue
            # 숫자만 있는 것 제외 (위의 정규식에서 이미 어느 정도 걸러지지만 보수적으로 체크)
            if w.isdigit():
                continue
            # 연도나 날짜 패턴 (2024, 0513 등) 제외
            if re.match(r'^(20\d{2}|0\d{1,3}|\d{1,2})$', w):
                continue
            filtered.append(w)
            
        return filtered

    def _find_related_stocks(self, main_keyword: str, source_data: Dict) -> List[Dict]:
        """주요 키워드와 연관된 종목 찾기"""
        stocks = []
        seen = set()
        
        # 1. DART에서 직접 찾기
        if "dart.json" in source_data:
            disclosures = source_data["dart.json"].get("data", {}).get("disclosures", [])
            for d in disclosures:
                corp = d.get("corp_name", "")
                title = d.get("report_nm", "")
                if corp and (main_keyword in corp or main_keyword in title):
                    if corp not in seen:
                        stocks.append({"name": corp, "rationale": f"DART 공시 '{title}' 포착"})
                        seen.add(corp)
        
        # 2. 뉴스 제목에서 종목명처럼 보이는 것 찾기 (대문자 영어 등)
        if len(stocks) < 3 and "sentiment.json" in source_data:
            headlines = source_data["sentiment.json"].get("data", {}).get("news_headlines", [])
            for h in headlines:
                title = h.get("title", "")
                if main_keyword in title:
                    # 영문 대문자 단어 (종목 티커 후보)
                    tickers = re.findall(r'\b[A-Z]{2,}\b', title)
                    for t in tickers:
                        if t not in self.stopwords and t not in seen:
                            stocks.append({"name": t, "rationale": f"뉴스 제목 내 주요 키워드 '{main_keyword}'와 함께 언급됨"})
                            seen.add(t)
                if len(stocks) >= 5: break

        return stocks[:5]
