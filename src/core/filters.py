# src/core/filters.py

import json
from pathlib import Path


class SignalFilters:

    def __init__(self, filter_weights_path: str = "data/learning/filter_weights.json"):
        self.weights = self._load_weights(filter_weights_path)

    def _load_weights(self, path: str) -> dict:
        default = {
            "필터1_역사적임계값": 1.5,
            "필터2_역설적현상": 1.3,
            "필터3_미반영격차": 1.4,
            "필터4_시의성": 1.6,
            "필터5_연결고리": 1.2,
            "필터6_권위자변화": 1.1,
            "필터7_공포무관섹터": 1.0
        }
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return default

    # ──────────────────────────────────────────
    # 필터1: 역사적 임계값 돌파
    # ──────────────────────────────────────────
    def filter1_historical_threshold(self, market: dict, macro: dict) -> tuple:
        """역사적 임계값 돌파 감지"""
        hits = []
        data = market.get("data", {})

        usd_krw = data.get("usd_krw", 0)
        if usd_krw and usd_krw > 1400:
            label = "위험" if usd_krw > 1500 else "주의"
            hits.append(f"환율 {usd_krw:.0f}원 — {label} 수준")

        vix = data.get("vix", 0)
        if vix and vix > 20:
            label = "극단적 공포" if vix > 30 else "공포"
            hits.append(f"VIX {vix:.1f} — {label} 구간")

        wti = data.get("wti_oil", 0)
        if wti and wti > 90:
            hits.append(f"WTI ${wti:.1f} — 고유가 구간")

        fg = data.get("fear_greed_index", 50)
        if fg and fg < 20:
            hits.append(f"Fear&Greed {fg:.0f} — 극단적 공포")

        return (len(hits) > 0, hits)

    # ──────────────────────────────────────────
    # 필터2: 역설적 현상 감지
    # ──────────────────────────────────────────
    def filter2_paradox(self, market: dict, sentiment: dict) -> tuple:
        """상식과 반대되는 시장 반응 감지"""
        hits = []
        mdata = market.get("data", {})
        headlines = sentiment.get("data", {}).get("news_headlines", [])

        kospi_chg = mdata.get("kospi_1d_change", 0)
        wti = mdata.get("wti_oil", 0)
        usd_krw = mdata.get("usd_krw", 0)

        # 역설1: 전쟁/위기 뉴스인데 주가 급등
        crisis_keywords = ["전쟁", "폭격", "공격", "봉쇄", "확전", "위기"]
        has_crisis_news = any(
            kw in h.get("title", "") for h in headlines for kw in crisis_keywords
        )
        if has_crisis_news and kospi_chg and kospi_chg > 2.0:
            hits.append(f"전쟁/위기 뉴스인데 KOSPI {kospi_chg:+.1f}% 급등 — 역설적 반응")

        # 역설2: 유가 폭등인데 KOSPI 상승 (에너지 수입국 역설)
        if wti and wti > 95 and kospi_chg and kospi_chg > 1.0:
            hits.append(f"유가 ${wti:.1f} 고공행진인데 KOSPI {kospi_chg:+.1f}% 상승")

        # 역설3: 환율 폭등(원화 약세)인데 외국인 순매수
        kospi_foreign = mdata.get("kospi_foreign_net", None)
        if usd_krw and usd_krw > 1450 and kospi_foreign and kospi_foreign > 0:
            hits.append(f"환율 {usd_krw:.0f}원 급등인데 외국인 순매수 — 역설적 수급")

        # 역설4: 호재 뉴스(휴전/협상)인데 주가 하락
        good_keywords = ["휴전", "협상", "합의", "금리인하", "경기부양"]
        has_good_news = any(
            kw in h.get("title", "") for h in headlines for kw in good_keywords
        )
        if has_good_news and kospi_chg and kospi_chg < -1.5:
            hits.append(f"호재 뉴스(휴전/협상)인데 KOSPI {kospi_chg:.1f}% 하락")

        return (len(hits) > 0, hits)

    # ──────────────────────────────────────────
    # 필터3: 미반영 격차 감지
    # ──────────────────────────────────────────
    def filter3_mispricing(self, market: dict, sentiment: dict = None) -> tuple:
        """가격 미반영 격차 감지"""
        hits = []
        mdata = market.get("data", {})
        headlines = []
        if sentiment:
            headlines = sentiment.get("data", {}).get("news_headlines", [])

        usd_krw = mdata.get("usd_krw", 0)
        wti = mdata.get("wti_oil", 0)

        # 미반영1: 환율 급등 → 수출주 수혜 미반영
        if usd_krw and usd_krw > 1450:
            hits.append(
                f"환율 {usd_krw:.0f}원 — 수출주(반도체/자동차) 수혜 구조 "
                f"but 장비주·소재주 미반영 가능성"
            )

        # 미반영2: 유가 급등 → 에너지주 수혜 but 하류 미반영
        if wti and wti > 90:
            hits.append(
                f"WTI ${wti:.1f} — 정유사 직접 수혜 but "
                f"석유화학 하류(플라스틱·섬유) 원가 상승 미반영"
            )

        # 미반영3: 방산 관련 뉴스
        defense_keywords = ["방산", "미사일", "군사", "전투기", "방공"]
        has_defense = any(
            kw in h.get("title", "") for h in headlines for kw in defense_keywords
        )
        if has_defense:
            hits.append("방산 관련 뉴스 — 방산 대형주 상승 but 부품/소재주 미반영 가능")

        # 미반영4: 우주/AI 관련
        space_ai_keywords = ["우주", "AI", "반도체", "아르테미스", "스페이스X"]
        has_space_ai = any(
            kw in h.get("title", "") for h in headlines for kw in space_ai_keywords
        )
        if has_space_ai:
            hits.append("우주/AI 뉴스 — 대장주 상승 but 부품·소재 공급망 미반영 가능")

        return (len(hits) > 0, hits)

    # ──────────────────────────────────────────
    # 필터4: 시의성
    # ──────────────────────────────────────────
    def filter4_timeliness(self, sentiment: dict) -> tuple:
        """시의성 감지 — 지금 당장이거나 지금 모르면 손해"""
        hits = []
        headlines = sentiment.get("data", {}).get("news_headlines", [])

        urgent_keywords = [
            "내일부터", "오늘부터", "당장", "지금 바로", "긴급",
            "D-1", "마감", "오늘 마감", "오늘 발표", "오늘 결정",
            "오전 중", "오후 중", "장중"
        ]

        event_keywords = [
            "금통위", "FOMC", "CPI", "PPI", "고용보고서",
            "실적발표", "IPO", "상장", "오펙", "OPEC"
        ]

        for h in headlines:
            title = h.get("title", "")
            for kw in urgent_keywords:
                if kw in title:
                    hits.append(f"즉각 시의성: {title[:40]}")
                    break
            for kw in event_keywords:
                if kw in title:
                    hits.append(f"예정 이벤트: {title[:40]}")
                    break

        return (len(hits) > 0, hits)

    # ──────────────────────────────────────────
    # 필터5: A→B 연결고리
    # ──────────────────────────────────────────
    def filter5_causal_chain(self, market: dict, sentiment: dict) -> tuple:
        """전혀 다른 영역으로의 파급 효과 감지"""
        hits = []
        mdata = market.get("data", {})
        headlines = sentiment.get("data", {}).get("news_headlines", [])

        usd_krw = mdata.get("usd_krw", 0)
        wti = mdata.get("wti_oil", 0)

        # 연결1: 중동 전쟁 → 호르무즈 → 유가 → 한국 제조업 원가
        war_keywords = ["전쟁", "호르무즈", "이란", "중동", "봉쇄"]
        has_war = any(kw in h.get("title", "") for h in headlines for kw in war_keywords)
        if has_war and wti and wti > 90:
            hits.append(
                f"중동 전쟁 → 호르무즈 → WTI ${wti:.1f} "
                f"→ 한국 제조업 원가 상승 연결고리"
            )

        # 연결2: 환율 급등 → 수입물가 → 소비자물가 → 금리
        if usd_krw and usd_krw > 1450:
            hits.append(
                f"환율 {usd_krw:.0f}원 → 수입물가 상승 "
                f"→ CPI 압력 → 한은 금리 동결 지속 연결고리"
            )

        # 연결3: AI 투자 → 전력 수요 → 원자력/LNG 수혜
        ai_keywords = ["AI", "데이터센터", "엔비디아", "HBM"]
        has_ai = any(kw in h.get("title", "") for h in headlines for kw in ai_keywords)
        if has_ai:
            hits.append(
                "AI 투자 확대 → 전력 수요 폭증 "
                "→ 원자력·LNG 발전사 수혜 연결고리"
            )

        # 연결4: 미국 금리 정책 → 달러 강세 → 신흥국 자금 이탈 → 한국
        fomc_keywords = ["FOMC", "연준", "파월", "금리동결", "금리인상"]
        has_fomc = any(kw in h.get("title", "") for h in headlines for kw in fomc_keywords)
        if has_fomc and usd_krw and usd_krw > 1430:
            hits.append(
                "연준 긴축 유지 → 달러 강세 "
                f"→ 환율 {usd_krw:.0f}원 → 외국인 이탈 연결고리"
            )

        return (len(hits) > 0, hits)

    # ──────────────────────────────────────────
    # 필터6: 권위자 행동 변화
    # ──────────────────────────────────────────
    def filter6_authority_change(self, sentiment: dict) -> tuple:
        """권위자 행동 변화 감지"""
        hits = []
        authority_signals = sentiment.get("data", {}).get("authority_signals", [])

        for signal in authority_signals:
            person = signal.get("person", "")
            action = signal.get("action", "")
            hits.append(f"{person} — {action[:40]}")

        headlines = sentiment.get("data", {}).get("news_headlines", [])
        authority_names = [
            "버핏", "이재용", "머스크", "파월", "이창용",
            "트럼프", "옐런", "라가르드"
        ]
        change_keywords = ["번복", "취소", "전환", "깜짝", "충격", "예상 밖"]

        for h in headlines:
            title = h.get("title", "")
            has_authority = any(name in title for name in authority_names)
            has_change = any(kw in title for kw in change_keywords)
            if has_authority and has_change:
                hits.append(f"권위자 이상 발언: {title[:40]}")

        return (len(hits) > 0, hits)

    # ──────────────────────────────────────────
    # 필터7: 시장 공포 무관 섹터
    # ──────────────────────────────────────────
    def filter7_uncorrelated_sector(self, market: dict, sentiment: dict) -> tuple:
        """시장 하락 중 특정 섹터만 상승 감지"""
        hits = []
        mdata = market.get("data", {})
        headlines = sentiment.get("data", {}).get("news_headlines", [])

        kospi_chg = mdata.get("kospi_1d_change", 0)
        vix = mdata.get("vix", 0)

        market_is_fearful = (
            (kospi_chg and kospi_chg < -1.0) or
            (vix and vix > 22)
        )

        if not market_is_fearful:
            return (False, hits)

        uncorrelated_keywords = {
            "방산": ["방산", "미사일", "군사", "방위"],
            "바이오": ["신약", "임상", "FDA", "바이오"],
            "우주항공": ["우주", "아르테미스", "위성", "발사"],
            "필수소비재": ["식품", "생활용품", "화장품"],
            "금": ["금값", "금 ETF", "안전자산"],
        }

        for sector, keywords in uncorrelated_keywords.items():
            has_sector_news = any(
                kw in h.get("title", "") for h in headlines for kw in keywords
            )
            if has_sector_news:
                chg_str = f"{kospi_chg:.1f}%" if kospi_chg else f"VIX {vix:.1f}"
                hits.append(
                    f"시장 하락({chg_str}) 중 "
                    f"{sector} 섹터 뉴스 — 공포 무관 수혜 가능"
                )

        return (len(hits) > 0, hits)

    # ──────────────────────────────────────────
    # 강도 계산
    # ──────────────────────────────────────────
    def calculate_strength(self, filters_hit: list, usd_krw: float = 0.0, vix: float = 0.0) -> float:
        """필터 적중 기반 강도 계산 (수치 크기 보너스 포함)"""
        if not filters_hit:
            return 0.0
        base = len(filters_hit) * 2.0
        weight_bonus = sum(self.weights.get(f, 1.0) for f in filters_hit)
        magnitude_bonus = 0.0
        if usd_krw > 1500:
            magnitude_bonus += 1.0
        elif usd_krw > 1480:
            magnitude_bonus += 0.5
        if vix > 25:
            magnitude_bonus += 0.5
        return min(base + weight_bonus * 0.5 + magnitude_bonus, 10.0)

    def determine_content_type(self, strength: float) -> str:
        if strength >= 8.0:
            return "롱폼"
        elif strength >= 6.0:
            return "쇼츠"
        elif strength >= 4.0:
            return "후보"
        else:
            return "탈락"

    def run_all_filters(self, raw_data: dict) -> dict:
        """전체 필터 실행"""
        market = raw_data.get("market", {})
        macro = raw_data.get("macro", {})
        sentiment = raw_data.get("sentiment", {})

        results = {}
        all_hits = []

        checks = [
            ("필터1_역사적임계값", self.filter1_historical_threshold(market, macro)),
            ("필터2_역설적현상",   self.filter2_paradox(market, sentiment)),
            ("필터3_미반영격차",   self.filter3_mispricing(market, sentiment)),
            ("필터4_시의성",       self.filter4_timeliness(sentiment)),
            ("필터5_연결고리",     self.filter5_causal_chain(market, sentiment)),
            ("필터6_권위자변화",   self.filter6_authority_change(sentiment)),
            ("필터7_공포무관섹터", self.filter7_uncorrelated_sector(market, sentiment)),
        ]

        for name, (hit, details) in checks:
            results[name] = {"hit": hit, "details": details}
            if hit:
                all_hits.append(name)

        strength = self.calculate_strength(all_hits)
        content_type = self.determine_content_type(strength)

        return {
            "filters_hit": all_hits,
            "filter_results": results,
            "strength": round(strength, 1),
            "content_type": content_type
        }
