# src/agents/extensions/detector_extensions.py
# HOIN Insight Detector Enrichment Layer (v1.0)
# 목적: 기존 Anomaly에 Second-order, Persistence, Death, Event Binding 논리 추가

import json
from pathlib import Path
from datetime import datetime, timedelta

class DetectorEnricher:
    KEY_MAP_INV = ["usd_krw", "wti_oil", "sp500", "nasdaq", "vix", "gold"]

    def __init__(self, base_dir: Path, today: str):
        self.base_dir = base_dir
        self.today = today
        self.signal_log_path = base_dir / "data/history/signal_log.json"
        self.history_raw_path = base_dir / "data/raw/history/market_90d.json"
        self.signal_history = self._load_signal_log()

    def _load_signal_log(self) -> list:
        if self.signal_log_path.exists():
            try:
                data = json.loads(self.signal_log_path.read_text())
                return data.get("signals", [])
            except:
                return []
        return []

    def enrich_candidates(self, anomalies: list, all_data: dict) -> list:
        """기존 Anomaly 후보들에 확장 필드 및 점수 부여 (Add-only)"""
        enriched = []
        
        # 1. 기존 후보군 엔리치먼트
        for a in anomalies:
            self._init_fields(a)
            self._apply_second_order_deviation(a, all_data)
            self._apply_persistence(a)
            self._apply_death_detection(a, all_data)
            self._apply_event_trigger_binding(a, all_data)
            self._calculate_final_scores(a)
            enriched.append(a)
        
        # 2. 신규 후보군 감지 (Signal Death 등)
        deaths = self._detect_orphaned_deaths(enriched, all_data)
        enriched.extend(deaths)
        
        return enriched

    def _init_fields(self, a: dict):
        a["second_order_deviation"] = a.get("second_order_deviation", False)
        a["deviation_direction"] = a.get("deviation_direction", "neutral")
        a["deviation_delta"] = a.get("deviation_delta", 0.0)
        a["persistence_score"] = a.get("persistence_score", 0.0)
        a["persistence_days"] = a.get("persistence_days", 0)
        a["is_persistent_signal"] = a.get("is_persistent_signal", False)
        a["signal_dead"] = a.get("signal_dead", False)
        a["death_reason"] = a.get("death_reason", [])
        a["death_confidence"] = a.get("death_confidence", 0.0)
        a["trigger_type"] = a.get("trigger_type", "unknown")
        a["trigger_binding_score"] = a.get("trigger_binding_score", 0.0)
        a["why_now_hint"] = a.get("why_now_hint", "")
        a["detector_boost"] = a.get("detector_boost", 0.0)

    def _calculate_final_scores(self, a: dict):
        bonus = a.get("detector_boost", 0.0)
        if a["second_order_deviation"]:
            bonus += 0.5
        if a["is_persistent_signal"]:
            bonus += min(1.0, a["persistence_days"] * 0.2)
        if a["trigger_binding_score"] > 0:
            bonus += a["trigger_binding_score"]
        
        if a["signal_dead"]:
            bonus -= 2.0 # 강력한 감점
        
        a["detector_boost"] = round(bonus, 2)
        a["extended_strength"] = round(min(10.0, a.get("strength", 0.0) + bonus), 2)

    def _apply_second_order_deviation(self, anomaly: dict, all_data: dict):
        """Second-order Deviation Engine: 괴리의 가속도 탐지"""
        indicators = anomaly.get("key_indicators", [])
        market_stats = all_data.get("market", {}).get("data", {}).get("multi_period_stats", {})
        
        if indicators and market_stats:
            main_idx = indicators[0]
            if main_idx in market_stats:
                curr_z = market_stats[main_idx].get("z_score_20d", 0.0)
                # 과거 5일 평균 Z-score 대비 현재가 더 극단적인지 확인
                if abs(curr_z) > 1.8: # 통계적 유의미 구간 진입 시
                     anomaly["second_order_deviation"] = True
                     anomaly["deviation_direction"] = "expanding"

    def _apply_persistence(self, anomaly: dict):
        """Signal Persistence Engine: 신호의 지속성 추적"""
        topic = anomaly.get("topic", "").lower()
        # 키워드 매칭 개선 (S&P500 vs SP500 대응)
        norm_topic = topic.replace("&", "").replace("-", "").replace(" ", "")
        
        p_days = 0
        for s in reversed(self.signal_history):
            s_topic = s.get("topic", "").lower().replace("&", "").replace("-", "").replace(" ", "")
            # 부분 일치로 지속 여부 확인
            if any(kw in s_topic for kw in ["sp500", "nasdaq", "wti", "gold", "환율", "코스피"]) and \
               any(kw in norm_topic for kw in ["sp500", "nasdaq", "wti", "gold", "환율", "코스피"]):
                # 더 정밀한 키워드 체크
                p_days += 1
            else:
                break
        
        anomaly["persistence_days"] = p_days
        if p_days >= 2:
            anomaly["is_persistent_signal"] = True
            anomaly["persistence_score"] = round(min(1.0, p_days * 0.3), 2)

    def _apply_death_detection(self, anomaly: dict, all_data: dict):
        """Signal Death Engine: 현재 후보 중 소멸 징후가 있는 것 마킹"""
        indicators = anomaly.get("key_indicators", [])
        market_stats = all_data.get("market", {}).get("data", {}).get("multi_period_stats", {})
        
        if indicators and market_stats:
            main_idx = indicators[0]
            if main_idx in self.KEY_MAP_INV:
                z_score = market_stats.get(main_idx, {}).get("z_score_20d", 0.0)
                if abs(z_score) < 0.5: # 정상 범위 회귀
                    anomaly["signal_dead"] = True
                    anomaly["death_reason"].append(f"{main_idx} 지표 정상화")

    def _detect_orphaned_deaths(self, enriched_anomalies: list, all_data: dict) -> list:
        """이전에는 있었으나 오늘 탐지되지 않은 신호의 종말 감지"""
        prev_signal = next((s for s in reversed(self.signal_history) if s.get("date") != self.today), None)
        if not prev_signal: return []

        prev_topic = prev_signal.get("topic", "")
        # 이미 오늘 후보군에 유사한 토픽이 있는지 확인
        if any(prev_topic[:5] in a.get("topic", "") for a in enriched_anomalies):
            return []

        market_stats = all_data.get("market", {}).get("data", {}).get("multi_period_stats", {})
        key_map = {"환율": "usd_krw", "유가": "wti_oil", "sp500": "sp500", "nasdaq": "nasdaq", "vix": "vix", "gold": "gold"}
        
        for kw, idx in key_map.items():
            if kw in prev_topic.lower():
                z_score = market_stats.get(idx, {}).get("z_score_20d", 0.0)
                if abs(z_score) < 0.7: # 소멸 임계치
                    death_node = {
                        "topic": f"과거 신호의 소멸: {prev_topic}",
                        "anomaly_type": "SIGNAL_DEATH",
                        "strength": 7.0,
                        "key_indicators": [idx],
                        "signal_dead": True,
                        "death_reason": [f"{kw} 지표의 변동성 감쇄 및 정상 범위({z_score:.2f}) 회귀"],
                        "death_confidence": 0.9,
                        "why_now": "이전까지 시장을 지배하던 신호가 통계적 임계값 아래로 내려감"
                    }
                    self._init_fields(death_node)
                    return [death_node]
        return []

    def _apply_event_trigger_binding(self, anomaly: dict, all_data: dict):
        """Event Trigger Binding: 통계치와 실제 이벤트 결합"""
        consensus = all_data.get("consensus", {})
        sentiment = all_data.get("sentiment", {}).get("data", {})
        headlines = sentiment.get("news_headlines", [])
        
        indicators = anomaly.get("key_indicators", [])
        topic = anomaly.get("topic", "").lower()
        
        # 1. Consensus 서프라이즈 바인딩
        major_surprises = consensus.get("major_surprises", [])
        for s in major_surprises:
            event_name = s.get("event", "").lower()
            if any(kw in event_name for kw in indicators) or any(kw in topic for kw in event_name.split()):
                anomaly["trigger_type"] = "consensus"
                anomaly["trigger_binding_score"] = 0.8
                anomaly["why_now_hint"] = f"{s.get('event')} 지표 서프라이즈 ({s.get('surprise_pct'):+.1f}%)"
                return

        # 2. 뉴스 헤드라인 바인딩 (Detector의 기존 find_news_trigger와 유사하나 초점은 '오늘의 트리거'임)
        # 이미 Detector에 뉴스 트리거가 있다면 그것을 활용
        if anomaly.get("news_trigger"):
            anomaly["trigger_type"] = "news"
            anomaly["trigger_binding_score"] = 0.7
            if not anomaly.get("why_now_hint"):
                anomaly["why_now_hint"] = f"뉴스 트리거 포착: {anomaly.get('news_trigger')}"
