import json
from datetime import datetime
from pathlib import Path
from src.core.filters import SignalFilters
from src.core.claude_client import ClaudeClient


class DetectorAgent:
    """이상징후 탐지자 — 숫자와 뉴스 맥락을 결합하여 시장의 신호를 포착함 (v5.0 Narrative-First)"""

    def __init__(self):
        # 작업 디렉토리 고정 (IS-4.0 설계 지침)
        self.base_dir = Path("/Users/taehunlim/dev/HoinInsight")
        self.today = datetime.now().strftime("%Y%m%d")
        
        self.raw_dir = self.base_dir / f"data/raw/{self.today}"
        self.signal_dir = self.base_dir / f"data/signals/{self.today}"
        self.signal_dir.mkdir(parents=True, exist_ok=True)
        self.history_path = self.base_dir / "data/history/signal_log.json"
        self.filters = SignalFilters()
        self.claude = ClaudeClient()
    def load_raw_data(self):
        raw = {}
        # macro, market, sentiment 데이터 로드
        for name in ["macro", "market", "sentiment"]:
            p = self.raw_dir / f"{name}.json"
            if p.exists():
                try:
                    raw[name] = json.loads(p.read_text())
                except Exception as e:
                    print(f"  {name}.json 로드 실패: {e}")
        
        # 90일 히스토리 데이터 로드 (v7.0)
        hist_p = self.base_dir / "data/raw/history/market_90d.json"
        if hist_p.exists():
            try:
                raw["history_90d"] = json.loads(hist_p.read_text()).get("history_90d", {})
                print("  📊 90일 시계열 데이터 로드 완료 (Feb~Current)")
            except Exception as e:
                print(f"  90일 히스토리 로드 실패: {e}")
        return raw

    def discover_autonomous_narratives(self, raw_data: dict) -> list:
        """AI 자율 담론 사냥: 시장의 모순(Anomaly)과 기대 충돌을 스스로 포착 (v6.0)"""
        sentiment = raw_data.get("sentiment", {}).get("data", {})
        headlines = sentiment.get("news_headlines", [])
        market = raw_data.get("market", {}).get("data", {})
        history = raw_data.get("history_90d", {})
        
        if not headlines:
            return []

        print("  🧠 AI 자율 서사 탐색 중 (시장의 모순 및 기대 충돌 포착)...")
        
        # 전체 맥락을 한 번에 분석하여 '이상함'의 냄새를 맡음
        prompt = f"""
너는 '경제사냥꾼'의 핵심 탐지 엔진이다. 
아래 뉴스 헤드라인들과 시장 지표를 보고, 오늘 시장에서 가장 '이상하거나(Anomaly)', '기대를 배신하거나(Expectation vs Reality)', 
혹은 '결정적인 판도의 변화(WHY NOW)'가 느껴지는 핵심 서사 3가지를 선정해라.

[시장 지표 및 90일 추세 (v7.0)]
- 환율: {market.get('usd_krw', 'N/A')}원 (90일 고점: {history.get('usd_krw', {}).get('max_90d', 'N/A')}원)
- KOSPI: {market.get('kospi_1d_change', '0')}% (90일 평균: {history.get('kospi', {}).get('avg_90d', 'N/A')})
- WTI 유가: ${market.get('wti_oil', 'N/A')} (90일 고점: ${history.get('wti_oil', {}).get('max_90d', 'N/A')}, 90일 평균: ${history.get('wti_oil', {}).get('avg_90d', 'N/A')})

[뉴스 헤드라인]
{json.dumps([h.get('title') for h in headlines[:30]], ensure_ascii=False, indent=2)}

[사냥 지침 - 시계열 맥락 우선]
1. 추세적 위치 파악: 오늘의 숫자가 90일 최고점 대비 낮다면 '돌파'가 아닌 '조정 중 반등'으로 해석할 것.
2. 모순(Anomaly) 포착: 지표의 흐름과 뉴스의 톤이 어긋나는 지점을 찾을 것.
3. WHY NOW: 2월부터 이어진 흐름 속에서 왜 '오늘' 이 변화가 변곡점인지 설명할 것.

[출력 JSON 구조]
[
  {{
    "topic": "서사 제목 (경제사냥꾼 스타일 - 짧고 강하게)",
    "target_type": "MACRO_GEOPOLITICAL | MACRO_FINANCIAL | MICRO_SECTOR_FOCUS",
    "reason": "AI가 이 주제를 선정한 논리적 이유 (한 문장 - 왜 지금 모순적인가?)",
    "strength": 0.0~10.0 점수,
    "related_keywords": ["지정학", "유동성", "모순" 등 3~5개],
    "filters_hit": ["필터2_역설적현상", "필터4_시의성" 등 관련 필터 2~3개]
  }}
]
순수 JSON 배열만 출력해라.
"""
        try:
            results = self.claude.call_json(prompt, max_tokens=2000)
            if not isinstance(results, list): return []
            
            for res in results:
                res["context_status"] = "AI_DISCOVERED"
                res["data_evidence"] = {"ai_reason": res.get("reason", "")}
            return results
        except Exception as e:
            print(f"  ❌ AI 서사 탐색 실패: {e}")
            return []

    def build_candidates(self, raw_data):
        """뉴스 서사와 시장 지표를 결합하여 후보 생성 (v5.0)"""
        market = raw_data.get("market", {}).get("data", {})
        sentiment = raw_data.get("sentiment", {}).get("data", {})

        candidates = []

        # [NEW] 서사 자율 탐지: AI가 스스로 모순과 기대 충돌을 포착 (v6.0 TRUE HUNTER)
        narratives = self.discover_autonomous_narratives(raw_data)
        if narratives:
            print(f"  📢 AI 자율 포착 담론: {len(narratives)}건")
            candidates.extend(narratives)

        # 주요 지표 로드
        usd_krw = market.get("usd_krw", 0)
        vix = market.get("vix", 0)
        kospi_chg = market.get("kospi_1d_change", 0)
        wti = market.get("wti_oil", 0)
        gold = market.get("gold", 0)
        dxy = market.get("dxy", 0)
        us10y = market.get("us10y", 0)

        # 1. 환율 이슈
        if usd_krw and usd_krw > 1400:
            label = "위험" if usd_krw > 1500 else "주의"
            filters_hit = ["필터1_역사적임계값"]
            if usd_krw > 1480: filters_hit.append("필터4_시의성")
            strength = self.filters.calculate_strength(filters_hit, usd_krw=usd_krw)
            candidates.append({
                "topic": f"원달러 환율 {usd_krw:.0f}원 → {label} 수준",
                "filters_hit": filters_hit,
                "strength": round(strength, 1),
                "data_evidence": {"usd_krw": usd_krw},
                "related_keywords": ["환율", "원화", "달러", "외환"]
            })

        # 2. VIX 이슈
        if vix and vix > 22:
            strength = self.filters.calculate_strength(["필터1_역사적임계값"])
            candidates.append({
                "topic": f"VIX 지수 {vix:.1f} → 시장 불안정성 심화",
                "filters_hit": ["필터1_역사적임계값"],
                "strength": round(strength, 1),
                "data_evidence": {"vix": vix},
                "related_keywords": ["공포", "변동성", "VIX"]
            })

        # 3. 유가 이슈
        if wti and wti > 85:
            filters_hit = ["필터1_역사적임계값", "필터5_연결고리"]
            strength = self.filters.calculate_strength(filters_hit)
            candidates.append({
                "topic": f"WTI 유가 ${wti:.1f} → 에너지 비용 압박",
                "filters_hit": filters_hit,
                "strength": round(strength, 1),
                "data_evidence": {"wti": wti},
                "related_keywords": ["유가", "원유", "인플레이션"]
            })

        # 4. 복합 신호 (환율 + 유가)
        if usd_krw and usd_krw > 1430 and wti and wti > 88:
            filters_hit = ["필터1_역사적임계값", "필터2_역설적현상", "필터5_연결고리"]
            strength = self.filters.calculate_strength(filters_hit, usd_krw=usd_krw)
            candidates.append({
                "topic": f"환율 {usd_krw:.0f}원 + 유가 ${wti:.1f} 동시 급등 → 복합 위기",
                "filters_hit": filters_hit,
                "strength": round(strength, 1),
                "data_evidence": {"usd_krw": usd_krw, "wti": wti},
                "related_keywords": ["환율", "유가", "스태그플레이션"]
            })

        # 5. 필터기반 정밀 신호 (연결고리, 역설 등)
        f5_hit, f5_details = self.filters.filter5_causal_chain(raw_data.get("market", {}), raw_data.get("sentiment", {}))
        if f5_hit:
            for detail in f5_details[:1]:
                candidates.append({
                    "topic": detail,
                    "filters_hit": ["필터5_연결고리"],
                    "strength": 7.5,
                    "data_evidence": {"detail": detail},
                    "related_keywords": ["연결고리", "파급효과"]
                })

        # 최종 정렬: 강도 기준 (9.5+ 사건은 무조건 1순위)
        candidates.sort(key=lambda x: x["strength"], reverse=True)
        return candidates

    def validate_context(self, topic_obj, sentiment_data):
        headlines = sentiment_data.get("data", {}).get("news_headlines", [])
        keywords = topic_obj.get("related_keywords", [])
        if not headlines: return 0.5
        match_count = 0
        for h in headlines:
            title = h.get("title", "").lower()
            if any(kw.lower() in title for kw in keywords):
                match_count += 1
        return min(match_count / 3.0, 1.0)

    def select_topic(self, candidates, sentiment_data):
        print(f"  🔍 {len(candidates)}개 후보에 대해 뉴스 맥락 교차 검증 중...")
        
        # AI가 발굴한 자율 서사나 9.5+ 메가 이벤트는 수동 검증 생략 혹은 가점
        for c in candidates:
            if c.get("context_status") == "AI_DISCOVERED" or c["strength"] >= 9.5: 
                c["context_status"] = "AI_VERIFIED" if c.get("context_status") == "AI_DISCOVERED" else "MEGA_EVENT"
                print(f"    🚨 자율 포착/메가 서사 감지: {c['topic']}")
                continue
                
            score = self.validate_context(c, sentiment_data)
            orig = c["strength"]
            if score == 0:
                c["strength"] *= 0.8
                c["context_status"] = "MISSING_CONTEXT"
            else:
                c["strength"] = orig * (0.8 + 0.2 * score)
                c["context_status"] = "VERIFIED" if score > 0.5 else "WEAK_CONTEXT"
            print(f"    - [{c['context_status']}] {c['topic'][:45]}... ({orig:.1f}->{c['strength']:.1f})")

        candidates.sort(key=lambda x: x["strength"], reverse=True)
        
        if candidates:
            best = candidates[0]
            best["selected"] = True
            best["content_type"] = "롱폼" if best["strength"] >= 8.5 else "쇼츠"
            return best
        return None

    def save_results(self, candidates, selected):
        # 대시보드(Publisher) 호환 규격으로 저장
        save_data = {
            "date": self.today,
            "total_candidates": len(candidates),
            "candidates": candidates
        }
        (self.signal_dir / "candidates.json").write_text(json.dumps(save_data, ensure_ascii=False, indent=2))
        
        if selected:
            (self.signal_dir / "today_signal.json").write_text(json.dumps(selected, ensure_ascii=False, indent=2))

    def run(self):
        print(f"\n🔍 AGENT-03 DETECTOR 시작 [{self.today}]")
        raw = self.load_raw_data()
        if not raw: return {}
        candidates = self.build_candidates(raw)
        selected = self.select_topic(candidates, raw.get("sentiment", {}))
        if selected:
            print(f"  ✅ 최종 선정: {selected['topic']} (강도: {selected['strength']:.1f})")
        self.save_results(candidates, selected)
        return {"selected": selected}

if __name__ == "__main__":
    DetectorAgent().run()
