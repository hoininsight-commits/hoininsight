import json
import os
from datetime import datetime
from pathlib import Path
from src.core.gemini_client import GeminiClient


class DetectorAgent:
    """
    HOIN DETECTOR v5.0 — AI 기반 다중기간 이상징후 탐지
    
    핵심 원칙:
    1. 절대값 임계값 없음 — 상대적 변화와 맥락으로만 판단
    2. 사전 정의된 테마 없음 — AI가 데이터에서 직접 발굴
    3. 다중 기간 조합 — 5일(속도) + 20일(추세) + 60일(구조)
    4. 지표 간 상관관계 붕괴 감지
    5. 뉴스 맥락과 숫자의 모순 감지
    """

    def __init__(self):
        self.base_dir = Path(
            os.getenv("HOIN_BASE_DIR",
                      Path(__file__).resolve().parents[2])
        )
        self.today = datetime.now().strftime("%Y%m%d")
        self.raw_dir = self.base_dir / f"data/raw/{self.today}"
        self.signal_dir = self.base_dir / f"data/signals/{self.today}"
        self.signal_dir.mkdir(parents=True, exist_ok=True)
        self.gemini = GeminiClient()

    def load_all_data(self) -> dict:
        """모든 수집 데이터 로드"""
        all_data = {}
        files = ["market", "macro", "sentiment", "fred", "ecos", "dart", "consensus"]
        for name in files:
            p = self.raw_dir / f"{name}.json"
            if p.exists():
                try:
                    all_data[name] = json.loads(p.read_text())
                    print(f"  ✅ {name}.json 로드")
                except Exception as e:
                    print(f"  ❌ {name}.json 로드 실패: {e}")
        return all_data

    def build_data_summary(self, all_data: dict) -> str:
        """AI에게 줄 데이터 요약 생성"""
        market = all_data.get("market", {}).get("data", {})
        stats  = market.get("multi_period_stats", {})
        fred   = all_data.get("fred", {}).get("data", {})
        ecos   = all_data.get("ecos", {}).get("data", {})
        sentiment = all_data.get("sentiment", {}).get("data", {})
        headlines = sentiment.get("news_headlines", [])
        dart   = all_data.get("dart", {}).get("data", {})

        # 지표별 다중기간 요약 생성
        stats_lines = []
        for key, s in stats.items():
            if not s:
                continue
            line = (
                f"{key}: 현재={s.get('current')} "
                f"| 5일변화={s.get('chg_5d')}% "
                f"| 20일변화={s.get('chg_20d')}% "
                f"| 20일Z-score={s.get('z_score_20d')} "
                f"| 20일평균={s.get('avg_20d')} "
                f"| 60일평균={s.get('avg_60d')}"
            )
            stats_lines.append(line)

        # FRED 핵심 지표
        fred_lines = []
        if fred:
            fred_lines = [
                f"미국기준금리: {fred.get('fed_rate')}%",
                f"10Y-2Y스프레드: {fred.get('spread_10y2y')}",
                f"하이일드스프레드: {fred.get('hy_spread')}",
                f"금융스트레스지수: {fred.get('financial_stress')}",
                f"MMF잔고: {fred.get('mmf_balance')}억달러",
                f"미국실업률: {fred.get('unemployment')}%",
            ]

        # ECOS 한국 지표
        ecos_lines = []
        if ecos:
            ecos_lines = [
                f"한국기준금리: {ecos.get('kr_base_rate')}%",
                f"한국CPI: {ecos.get('kr_cpi')}",
            ]

        # 뉴스 헤드라인
        news_lines = [
            f"[{h.get('source','')}] {h.get('title','')}"
            for h in headlines[:20]
        ]

        # DART 공시
        dart_lines = []
        disclosures = dart.get("disclosures", [])
        if disclosures:
            dart_lines = [
                f"[공시] {d.get('type')} - {d.get('company')}: {d.get('title')}"
                for d in disclosures[:5]
            ]
        
        # 020: 컨센서스 섹션 추가
        consensus_data = all_data.get("consensus", {})
        surprises = consensus_data.get("major_surprises", [])
        consensus_lines = []
        if surprises:
            for s in surprises:
                direction = "📈 BEAT" if s.get("surprise_direction") == "BEAT" else "📉 MISS"
                consensus_lines.append(
                    f"{direction} {s.get('event')}: "
                    f"예상={s.get('forecast')} 실제={s.get('actual')} "
                    f"괴리={s.get('surprise')}%"
                )

        summary = f"""
=== 시장 지표 (다중기간 통계) ===
{chr(10).join(stats_lines) if stats_lines else "통계 데이터 없음"}

=== 오늘 경제지표 서프라이즈 ===
{chr(10).join(consensus_lines) if consensus_lines else "서프라이즈 없음 또는 미발표"}

=== 미국 거시 지표 (FRED) ===
{chr(10).join(fred_lines) if fred_lines else "없음"}

=== 한국 거시 지표 (ECOS) ===
{chr(10).join(ecos_lines) if ecos_lines else "없음"}

=== 오늘 뉴스 헤드라인 ===
{chr(10).join(news_lines) if news_lines else "없음"}

=== DART 주요 공시 ===
{chr(10).join(dart_lines) if dart_lines else "없음"}
"""
        return summary

    def detect_anomalies(self, data_summary: str) -> list:
        """AI가 자유롭게 이상징후를 찾는 핵심 함수"""
        if not data_summary or len(data_summary.strip()) < 100:
            print("  ⚠️ 요약 데이터가 너무 부실합니다. 분석을 건너뜁니다.")
            return []

        print("  🧠 AI 이상징후 탐지 중... (Gemini 응답 대기, 최대 30초)")

        prompt = f"""
너는 경제사냥꾼의 탐지 엔진이다. 아래 데이터를 보고 가장 이상한 징후 3개를 찾아라.
{data_summary}

[탐지 관점]
[토픽 선정 우선순위 — 반드시 이 순서를 따를 것]

1순위: 컨센서스 서프라이즈 (SHOCK/SURPRISE 등급)
   - consensus.json의 top_surprise 또는 major_surprises 확인
   - surprise_pct 절대값이 큰 것부터 우선
   - 예: "HY 스프레드가 12개월 평균 대비 117% 이상 급변"
   - 이 신호가 있으면 반드시 1순위 후보로 올릴 것

2순위: 지표 간 모순 (CORRELATION 붕괴)
   - 원래 같이/반대로 가야 하는 지표가 반대 방향
   - 예: 지정학 위기 뉴스 + 유가 하락 = 강한 모순
   - Z-score 또는 다중기간 변화율로 반드시 수치 근거 제시

3순위: Z-score 이상 이탈 (SPEED 신호)
   - Z-score > 2.0 또는 5일 변화율 급변
   - 수치 근거 없으면 채택 불가

[절대 금지 패턴]
- "환율 XXX원 돌파" 형태의 절대값 토픽
- "유가 $XX → 에너지 압박" 형태의 절대값 토픽
- "금리 XX% → 부담 가중" 형태의 절대값 토픽
- WHY NOW를 데이터로 설명 못하는 토픽
- Z-score나 서프라이즈 수치 없이 뉴스 키워드만 있는 토픽

[WHY NOW 필수 조건]
모든 토픽은 아래 질문에 데이터로 답할 수 있어야 한다:
"왜 어제가 아니라 오늘인가?"
답 못하면 토픽 아님.

[출력 규칙]
- 순수 JSON 배열만 출력.

[구조]
[
  {{
    "topic": "경제사냥꾼 스타일 제목",
    "anomaly_type": "SPEED|CORRELATION|NEWS_MISMATCH|WHY_NOW",
    "why_anomalous": "데이터 근거 (한 문장)",
    "why_now": "결정적 이유 (한 문장)",
    "key_indicators": ["지표1", "지표2"],
    "strength": 0.0~10.0,
    "signal_type": "Type1~Type9"
  }}
]
"""
        try:
            results = self.gemini.call_json(prompt, max_tokens=1500)
            if not isinstance(results, list):
                print(f"  ⚠️ AI 응답 형식이 올바르지 않습니다 (Type: {type(results)})")
                return []
            print(f"  📡 AI 이상징후 탐지 완료: {len(results)}건")
            for r in results:
                print(f"    - [{r.get('strength',0):.1f}] {r.get('topic','')[:50]}")
            return results
        except Exception as e:
            print(f"  ❌ AI 탐지 실패: {e}")
            return []

    def _is_absolute_value_topic(self, topic: str, anomaly: dict) -> bool:
        """
        절대값 기반 토픽인지 감지
        Z-score 근거 없이 환율/유가 절대값만 언급하는 토픽 필터링
        """
        import re
        topic_lower = topic.lower()

        # 환율 절대값 패턴
        krw_pattern = re.search(r'환율\s*\d{3,4}원', topic)
        if krw_pattern:
            # Z-score나 변화율 근거가 없으면 필터링
            why = anomaly.get("why_anomalous", "")
            if "z-score" not in why.lower() and "z_score" not in why.lower() \
               and "변화율" not in why and "급변" not in why \
               and "급등" not in why and "급락" not in why:
                return True

        # 유가 절대값 패턴 (단순 수준 언급)
        wti_pattern = re.search(r'유가\s*\$\d+\s*→', topic)
        if wti_pattern and "폭락" not in topic and "폭등" not in topic \
           and "급락" not in topic and "급등" not in topic:
            return True

        return False

    def _build_consensus_fallback_topic(self, consensus_data: dict) -> dict:
        """
        consensus.json에서 가장 강한 서프라이즈로 토픽 자동 생성
        """
        if not consensus_data:
            return None

        major_surprises = consensus_data.get("major_surprises", [])
        top_surprise = consensus_data.get("top_surprise")

        # top_surprise 또는 major_surprises 중 가장 강한 것 선택
        candidates = []
        if top_surprise:
            candidates.append(top_surprise)
        candidates.extend(major_surprises)

        if not candidates:
            return None

        # surprise_pct 절대값 기준 정렬
        candidates.sort(
            key=lambda x: abs(x.get("surprise_pct", 0) or 0),
            reverse=True
        )
        best = candidates[0]

        surprise_pct = best.get("surprise_pct", 0)
        event_name = best.get("event", "알 수 없는 지표")
        actual = best.get("actual")
        previous = best.get("previous")
        direction = "급등" if (best.get("change", 0) or 0) > 0 else "급락"

        topic = f"{event_name} 12개월 평균 대비 {abs(surprise_pct):.0f}% {direction}"

        return {
            "topic": topic,
            "strength": min(9.5, 6.0 + abs(surprise_pct) / 100),
            "anomaly_type": "WHY_NOW",
            "why_now": f"{event_name}의 변화량이 12개월 평균 대비 {abs(surprise_pct):.0f}% 이탈 — 오늘 처음 나타난 이상 수준",
            "why_anomalous": f"예상 {previous} → 실제 {actual} (괴리 {surprise_pct:.1f}%)",
            "key_indicators": ["consensus", event_name],
            "signal_type": "Type5",
            "source": "CONSENSUS_FALLBACK"
        }

    def _build_zscore_fallback_topic(self, market_data: dict) -> dict:
        """
        multi_period_stats에서 Z-score 최대값 지표로 토픽 생성
        """
        if not market_data:
            return None

        data_block = market_data.get("data", {})
        multi_stats = data_block.get("multi_period_stats", {})
        if not multi_stats:
            return None

        best_key = None
        best_zscore = 0.0

        for key, stats in multi_stats.items():
            zscore = abs(stats.get("z_score_20d", 0) or 0)
            if zscore > best_zscore:
                best_zscore = zscore
                best_key = key

        if not best_key or best_zscore < 2.0:
            return None

        stats = multi_stats[best_key]
        change_5d = stats.get("chg_5d", 0)
        direction = "급등" if (change_5d or 0) > 0 else "급락"

        topic = f"{best_key} 5일 Z-score {best_zscore:.1f} — 통계적 이상 {direction}"

        return {
            "topic": topic,
            "strength": min(9.0, 5.0 + best_zscore),
            "anomaly_type": "SPEED",
            "why_now": f"{best_key} Z-score {best_zscore:.1f} — 통계적으로 오늘 처음 임계값 초과",
            "why_anomalous": f"5일 변화율 {change_5d}% | 20일 Z-score {best_zscore}",
            "key_indicators": [best_key],
            "signal_type": "Type1",
            "source": "ZSCORE_FALLBACK"
        }

    def select_best(self, anomalies: list, all_data: dict = None) -> dict:
        """가장 강한 이상징후 1개 선정 (3단계 Fallback 로직 적용)"""
        if not anomalies:
            anomalies = []

        # 1. 절대값 토픽 필터링
        filtered_candidates = []
        for a in anomalies:
            if self._is_absolute_value_topic(a.get("topic", ""), a):
                print(f"  🚫 절대값 토픽 필터링: {a.get('topic', '')[:50]}")
            else:
                filtered_candidates.append(a)

        final_topic = None

        # 2. 필터링 후 후보가 있으면 최강 선정
        if filtered_candidates:
            sorted_anomalies = sorted(
                filtered_candidates,
                key=lambda x: x.get("strength", 0),
                reverse=True
            )
            final_topic = sorted_anomalies[0]
            final_topic["source"] = "LLM"
        else:
            # 3. Fallback 단계
            # 1차: 컨센서스 서프라이즈 강제 fallback
            consensus_data = all_data.get("consensus") if all_data else None
            consensus_fallback = self._build_consensus_fallback_topic(consensus_data)
            if consensus_fallback:
                print("  🔄 절대값 필터 후 후보 없음 → 컨센서스 서프라이즈 토픽으로 교체")
                final_topic = consensus_fallback
            else:
                # 2차: 모든 수집 데이터에서 Z-score 최대값 지표로 토픽 생성
                market_data = all_data.get("market") if all_data else None
                zscore_fallback = self._build_zscore_fallback_topic(market_data)
                if zscore_fallback:
                    print("  🔄 컨센서스 없음 → Z-score 최대값 토픽으로 교체")
                    final_topic = zscore_fallback
                else:
                    # 3차: 그래도 없으면 "오늘 이상징후 없음" 처리
                    print("  ⚠️ 유효한 토픽 없음 — 오늘 파이프라인 스킵")
                    final_topic = None

        if not final_topic:
            return None

        final_topic["selected"] = True
        final_topic["content_type"] = "롱폼" if final_topic.get("strength", 0) >= 8.0 else "쇼츠"
        final_topic["date"] = self.today
        return final_topic

    def save_results(self, anomalies: list, selected: dict):
        """결과 저장"""
        # 전체 후보 저장
        candidates_data = {
            "date": self.today,
            "total_candidates": len(anomalies),
            "candidates": anomalies
        }
        (self.signal_dir / "candidates.json").write_text(
            json.dumps(candidates_data, ensure_ascii=False, indent=2)
        )

        # 선정 토픽 저장
        if selected:
            # analyst가 읽을 수 있는 형식으로 저장
            signal_data = {
                "date": self.today,
                "topic": selected.get("topic", ""),
                "signal_type": selected.get("signal_type", ""),
                "anomaly_type": selected.get("anomaly_type", ""),
                "why_anomalous": selected.get("why_anomalous", ""),
                "why_now": selected.get("why_now", ""),
                "key_indicators": selected.get("key_indicators", []),
                "strength": selected.get("strength", 0),
                "content_type": selected.get("content_type", "쇼츠"),
                "selected": True,
            }
            (self.signal_dir / "today_signal.json").write_text(
                json.dumps(signal_data, ensure_ascii=False, indent=2)
            )

            # anomaly_log도 함께 저장
            (self.signal_dir / "anomaly_log.json").write_text(
                json.dumps(candidates_data, ensure_ascii=False, indent=2)
            )

    def run(self):
        print(f"\n🔍 AGENT-03 DETECTOR v5.0 시작 [{self.today}]")

        # 1. 전체 데이터 로드
        all_data = self.load_all_data()
        if not all_data:
            print("  ❌ 데이터 없음")
            return {}

        # 2. 데이터 요약 생성
        print("  📊 다중기간 데이터 요약 생성 중...")
        data_summary = self.build_data_summary(all_data)

        # 3. AI 이상징후 탐지
        print("  🧠 AI 이상징후 탐지 중...")
        anomalies = self.detect_anomalies(data_summary)

        # 022: 컨센서스 기반 룰베이스 신호 주입 (선점형)
        consensus_path = self.raw_dir / "consensus.json"
        if consensus_path.exists():
            try:
                consensus_data = json.loads(consensus_path.read_text())
                top_surprise = consensus_data.get("top_surprise")
                if top_surprise and top_surprise.get("surprise_label") in ["SHOCK", "SURPRISE"]:
                    print(f"  🚨 컨센서스 쇼크 감지: {top_surprise['event']}")
                    consensus_signal = {
                        "topic": f"기대 붕괴: {top_surprise['event']} {top_surprise['surprise_label']} 발생",
                        "anomaly_type": "WHY_NOW",
                        "why_anomalous": f"예상 {top_surprise['estimate']} → 실제 {top_surprise['actual']} (괴리 {top_surprise['surprise_score']}%)",
                        "why_now": f"시장 기대를 {top_surprise['surprise_score']}% 웃도는(하회하는) 충격적 발표",
                        "key_indicators": ["consensus", top_surprise['event']],
                        "strength": 9.5 if top_surprise['surprise_label'] == "SHOCK" else 8.5,
                        "signal_type": "Type5"
                    }
                    anomalies.insert(0, consensus_signal) # 최상단에 주입하여 우선 선정 유도
            except Exception as e:
                print(f"  ⚠️ consensus.json 분석 실패: {e}")

        if not anomalies:
            anomalies = []

        # 4. 최강 신호 선정
        selected = self.select_best(anomalies, all_data=all_data)
        if selected:
            print(f"\n  ✅ 최종 선정: {selected['topic']}")
            print(f"     강도: {selected['strength']:.1f} | 유형: {selected['content_type']}")

        # 5. 저장
        self.save_results(anomalies, selected)
        return {"selected": selected}


if __name__ == "__main__":
    DetectorAgent().run()
