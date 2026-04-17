import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
from src.core.filters import SignalFilters
from src.core.gemini_client import GeminiClient

class DetectorAgent:
    """이상징후 탐지자 — 숫자와 뉴스 맥락을 결합하여 시장의 신호를 포착함 (v7.0 Intelligent Merge)"""

    def __init__(self):
        self.base_dir = Path(os.getenv("HOIN_BASE_DIR", Path(__file__).resolve().parents[2]))
        self.today = datetime.now().strftime("%Y%m%d")
        self.raw_dir = self.base_dir / f"data/raw/{self.today}"
        self.signal_dir = self.base_dir / f"data/signals/{self.today}"
        self.signal_dir.mkdir(parents=True, exist_ok=True)
        self.filters = SignalFilters()
        self.gemini = GeminiClient()

    def load_all_data(self):
        """서버 v7.0의 90일 히스토리 로드 기능 포함"""
        all_data = {}
        for name in ["macro", "market", "sentiment"]:
            p = self.raw_dir / f"{name}.json"
            if p.exists():
                try:
                    all_data[name] = json.loads(p.read_text())
                except: pass
        
        # 컨센서스 데이터 로드 (v4.0)
        p = self.raw_dir / "consensus.json"
        if p.exists():
            all_data["consensus"] = json.loads(p.read_text())

        # 90일 히스토리 로드 (v7.0)
        hist_p = self.base_dir / "data/raw/history/market_90d.json"
        if hist_p.exists():
            try:
                all_data["history_90d"] = json.loads(hist_p.read_text()).get("history_90d", {})
            except: pass
        
        return all_data

    def discover_autonomous_narratives(self, all_data: dict) -> list:
        """AI 자율 담론 사냥: 시장의 모순(Anomaly)과 기대 충돌을 스스로 포착 (v7.0)"""
        sentiment = all_data.get("sentiment", {}).get("data", {})
        headlines = sentiment.get("news_headlines", [])
        market = all_data.get("market", {}).get("data", {})
        history = all_data.get("history_90d", {})
        
        if not headlines or not self.gemini.client:
            return []

        prompt = f"""
너는 HOIN Insight의 '경제사냥꾼' 엔진이다. 지표와 뉴스를 분석해 오늘 시장에서 가장 '이상한(Anomaly)' 서사 3가지를 선정해라.
[오늘 지표] {market}
[90일 평균/최고점] {history}
[뉴스] {json.dumps([h.get('title') for h in headlines[:15]], ensure_ascii=False)}

결과는 반드시 JSON 배열로 출력:
[ {{ "topic": "제목", "reason": "이유", "strength": 점수, "related_keywords": [], "filters_hit": [] }} ]
"""
        try:
            results = self.gemini.call_json(prompt)
            if not isinstance(results, list): return []
            for res in results:
                res["context_status"] = "AI_DISCOVERED"
                res["data_evidence"] = {"ai_reason": res.get("reason", "")}
            return results
        except:
            return []

    def build_candidates(self, all_data):
        """v7.0 자율 탐색 + v4.0 통계 기반 통합"""
        candidates = self.discover_autonomous_narratives(all_data)
        market = all_data.get("market", {}).get("data", {})
        
        # 핵심 지표 긴급 필터
        usd_krw, vix = market.get("usd_krw", 0), market.get("vix", 0)
        if usd_krw and usd_krw > 1430:
            candidates.append({"topic": f"원달러 환율 {usd_krw}원 임계점 돌파", "strength": 7.5, "filters_hit": ["필터1_역사적임계값"], "related_keywords": ["환율", "외환"]})
        if vix and vix > 22:
            candidates.append({"topic": f"VIX {vix} 시장 공포 구간 진입", "strength": 8.1, "filters_hit": ["필터1_역사적임계값"], "related_keywords": ["VIX", "변동성"]})
        
        return candidates

    def build_data_summary(self, all_data):
        market = all_data.get("market", {}).get("data", {})
        consensus = all_data.get("consensus", {})
        sentiment = all_data.get("sentiment", {}).get("data", {})
        
        surprises = consensus.get("major_surprises", [])
        c_lines = [f"🚨 {s.get('event')}: {s.get('surprise_pct'):+.1f}%" for s in surprises]
        
        summary = f"""오늘 시장 현황: {market}
주요 서프라이즈: {c_lines if c_lines else "없음"}
뉴스 요약: {[h.get('title') for h in sentiment.get('news_headlines', [])[:3]]}
"""
        return summary

    def detect_anomalies(self, summary, candidates):
        """LLM 기반 신호 감지 (v4.0 강화 프롬프트)"""
        if not self.gemini.client: return []
        
        prompt = f"""
데이터 요약: {summary}
후보 신호: {candidates}

위 데이터를 분석해 오늘 가장 중요한 'WHY NOW' 토픽을 하나 골라라.
1순위: 컨센서스 서프라이즈
2순위: 지표 간 모순
3순위: Z-score 이상 이탈

결과는 JSON 배열(상위 3개)로 출력해라.
"""
        return self.gemini.call_json(prompt)

    def _is_absolute_value_topic(self, topic: str, anomaly: dict) -> bool:
        """v4.0 절대값 필터링"""
        import re
        topic_lower = topic.lower()
        why = anomaly.get("why_now", "").lower()
        if re.search(r'환율\s*[\d,.]+원', topic):
            if "z-score" not in why and "%" not in why: return True
        if re.search(r'유가\s*\$\d+', topic): return True
        return False

    def select_best(self, anomalies, market_data, consensus_data):
        """v4.0 3단계 Fallback 로직"""
        filtered = [a for a in (anomalies or []) if not self._is_absolute_value_topic(a.get("topic", ""), a)]
        
        if not filtered:
            # Fallback 1: Consensus
            major = consensus_data.get("major_surprises", [])
            if major:
                best = sorted(major, key=lambda x: abs(x.get("surprise_pct", 0)), reverse=True)[0]
                return {"topic": f"{best['event']} 서프라이즈 ({best['surprise_pct']:+.1f}%)", "strength": 8.5, "source": "CONSENSUS_FALLBACK", "selected": True}
            
            # Fallback 2: Z-score
            stats = market_data.get("multi_period_stats", {})
            if stats:
                best_key = max(stats, key=lambda k: abs(stats[k].get("zscore_5d", 0)))
                bz = stats[best_key].get("zscore_5d", 0)
                if abs(bz) > 2.0:
                    return {"topic": f"{best_key} Z-score {bz:.1f} 이탈", "strength": 7.0, "source": "ZSCORE_FALLBACK", "selected": True}
            return None

        best = sorted(filtered, key=lambda x: x.get("strength", 0), reverse=True)[0]
        best["selected"], best["source"] = True, "LLM"
        return best

    def save_results(self, candidates, selected):
        save_data = {"date": self.today, "candidates": candidates}
        (self.signal_dir / "candidates.json").write_text(json.dumps(save_data, ensure_ascii=False, indent=2))
        if selected:
            (self.signal_dir / "today_signal.json").write_text(json.dumps(selected, ensure_ascii=False, indent=2))

    def run(self):
        print(f"\n🔍 AGENT-03 DETECTOR 시작 [{self.today}]")
        all_data = self.load_all_data()
        if not all_data: return {}
        
        candidates = self.build_candidates(all_data)
        summary = self.build_data_summary(all_data)
        anomalies = self.detect_anomalies(summary, candidates)
        selected = self.select_best(anomalies, all_data.get("market", {}), all_data.get("consensus", {}))
        
        if selected:
            print(f"  ✅ 최종 선정: {selected['topic']} (강도: {selected.get('strength')})")
            self.save_results(candidates, selected)
        return {"selected": selected}

if __name__ == "__main__":
    DetectorAgent().run()
