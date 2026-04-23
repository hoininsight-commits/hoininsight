from typing import List, Dict
import hashlib

class EventFilter:
    """[TASK #102.1] 의미 없는 뉴스 및 중복 뉴스 필터링 (v1.1)"""

    NOISE_KEYWORDS = ["crime", "accident", "범죄", "사고", "인터뷰", "interview", "opinion", "의견", "칼럼", "column"]

    def __init__(self):
        pass

    def filter(self, events: List[Dict]) -> List[Dict]:
        filtered = []
        seen_hashes = set()

        for ev in events:
            text = (ev["event"] + " " + ev.get("summary", "")).lower()
            
            # 1. 노이즈 제거 (사고, 범죄, 단순 의견 등)
            if any(kw in text for kw in self.NOISE_KEYWORDS):
                continue
                
            # 2. 영향력 필터 (섹터 영향, 정책, 지정학 등은 이미 Builder에서 Type으로 걸러짐)
            # 추가로 제목 길이가 너무 짧거나 내용이 부실한 경우 체크 가능
            if len(ev["event"]) < 10:
                continue

            # 3. 중복 필터 (간단한 해시 기반 중복 제거)
            # 제목의 주요 단어만 추출하여 중복 체크 (더 정교한 클러스터링 가능)
            content_hash = self._get_fuzzy_hash(ev["event"])
            if content_hash in seen_hashes:
                continue
            seen_hashes.add(content_hash)

            ev["passed_filter"] = True
            filtered.append(ev)
            
        return filtered

    def _get_fuzzy_hash(self, text: str) -> str:
        # 공백 제거 및 소문자화 후 해시 (단순 중복 제거)
        clean = "".join(text.lower().split())
        return hashlib.md5(clean.encode()).hexdigest()
