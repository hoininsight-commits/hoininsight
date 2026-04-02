import json


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

    def filter1_historical_threshold(self, market: dict, macro: dict) -> tuple:
        """역사적 임계값 돌파 감지"""
        hits = []

        usd_krw = market.get("data", {}).get("usd_krw", 0)
        if usd_krw > 1400:
            hits.append(f"환율 {usd_krw}원 → 고점 수준")

        fear_greed = market.get("data", {}).get("fear_greed_index", 50)
        if fear_greed < 15:
            hits.append(f"공포탐욕지수 {fear_greed} → 극단적 공포")

        vix = market.get("data", {}).get("vix", 0)
        if vix > 30:
            hits.append(f"VIX {vix} → 고변동성 경보")

        return (len(hits) > 0, hits)

    def filter2_paradox(self, market: dict, sentiment: dict) -> tuple:
        """역설적 현상 감지"""
        hits = []
        # 향후 뉴스 감성 분석과 주가 반응 비교 로직 추가 예정
        return (False, hits)

    def filter3_mispricing(self, market: dict) -> tuple:
        """가격 미반영 격차 감지"""
        hits = []
        # 섹터 내 종목 간 수익률 분화 감지 예정
        return (False, hits)

    def filter4_timeliness(self, sentiment: dict) -> tuple:
        """시의성 감지"""
        hits = []
        headlines = sentiment.get("data", {}).get("news_headlines", [])
        timeliness_keywords = ["내일부터", "오늘부터", "D-1", "즉시", "긴급", "오늘 발표"]

        for news in headlines:
            title = news.get("title", "")
            if any(kw in title for kw in timeliness_keywords):
                hits.append(f"시의성 뉴스: {title[:30]}")

        return (len(hits) > 0, hits)

    def filter5_causal_chain(self, sentiment: dict, market: dict) -> tuple:
        """A→B 연결고리 감지"""
        hits = []
        # 섹터 간 파급 효과 감지 예정
        return (False, hits)

    def filter6_authority_change(self, sentiment: dict) -> tuple:
        """권위자 행동 변화 감지"""
        hits = []
        authority_signals = sentiment.get("data", {}).get("authority_signals", [])

        for signal in authority_signals:
            hits.append(f"{signal.get('person')} → {signal.get('action')}")

        return (len(hits) > 0, hits)

    def filter7_uncorrelated_sector(self, market: dict, sentiment: dict) -> tuple:
        """시장 공포 무관 섹터 감지"""
        hits = []
        # 시장 하락 중 특정 섹터 상승 감지 예정
        return (False, hits)

    def calculate_strength(self, filters_hit: list) -> float:
        """필터 적중 기반 강도 계산"""
        if not filters_hit:
            return 0.0

        base = len(filters_hit) * 2.0
        weight_bonus = sum(
            self.weights.get(f, 1.0) for f in filters_hit
        )
        return min(base + weight_bonus * 0.5, 10.0)

    def determine_content_type(self, strength: float) -> str:
        """강도에 따른 콘텐츠 유형 결정"""
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

        f1_hit, f1_details = self.filter1_historical_threshold(market, macro)
        results["필터1_역사적임계값"] = {"hit": f1_hit, "details": f1_details}
        if f1_hit:
            all_hits.append("필터1_역사적임계값")

        f2_hit, f2_details = self.filter2_paradox(market, sentiment)
        results["필터2_역설적현상"] = {"hit": f2_hit, "details": f2_details}
        if f2_hit:
            all_hits.append("필터2_역설적현상")

        f3_hit, f3_details = self.filter3_mispricing(market)
        results["필터3_미반영격차"] = {"hit": f3_hit, "details": f3_details}
        if f3_hit:
            all_hits.append("필터3_미반영격차")

        f4_hit, f4_details = self.filter4_timeliness(sentiment)
        results["필터4_시의성"] = {"hit": f4_hit, "details": f4_details}
        if f4_hit:
            all_hits.append("필터4_시의성")

        f5_hit, f5_details = self.filter5_causal_chain(sentiment, market)
        results["필터5_연결고리"] = {"hit": f5_hit, "details": f5_details}
        if f5_hit:
            all_hits.append("필터5_연결고리")

        f6_hit, f6_details = self.filter6_authority_change(sentiment)
        results["필터6_권위자변화"] = {"hit": f6_hit, "details": f6_details}
        if f6_hit:
            all_hits.append("필터6_권위자변화")

        f7_hit, f7_details = self.filter7_uncorrelated_sector(market, sentiment)
        results["필터7_공포무관섹터"] = {"hit": f7_hit, "details": f7_details}
        if f7_hit:
            all_hits.append("필터7_공포무관섹터")

        strength = self.calculate_strength(all_hits)
        content_type = self.determine_content_type(strength)

        return {
            "filters_hit": all_hits,
            "filter_results": results,
            "strength": round(strength, 1),
            "content_type": content_type
        }
