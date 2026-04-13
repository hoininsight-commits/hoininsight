import json
from datetime import datetime
from pathlib import Path
from src.core.filters import SignalFilters


class DetectorAgent:

    def __init__(self):
        self.today = datetime.now().strftime("%Y%m%d")
        self.raw_dir = Path(f"data/raw/{self.today}")
        self.signal_dir = Path(f"data/signals/{self.today}")
        self.signal_dir.mkdir(parents=True, exist_ok=True)
        self.history_path = Path("data/history/signal_log.json")
        self.filters = SignalFilters()

    def load_raw_data(self):
        raw = {}
        for name in ["macro", "market", "sentiment"]:
            p = self.raw_dir / f"{name}.json"
            if p.exists():
                raw[name] = json.loads(p.read_text())
        return raw

    def build_candidates(self, raw_data):
        """7개 필터 실행 후 후보 목록 생성"""
        market = raw_data.get("market", {}).get("data", {})
        macro = raw_data.get("macro", {}).get("data", {})
        sentiment = raw_data.get("sentiment", {}).get("data", {})

        # 시장 지표 로드 (기본 + 추가)
        usd_krw = market.get("usd_krw", 0)
        vix = market.get("vix", 0)
        kospi_chg = market.get("kospi_1d_change", 0)
        wti = market.get("wti_oil", 0)
        gold = market.get("gold", 0)
        dxy = market.get("dxy", 0)
        us10y = market.get("us10y", 0)
        nasdaq = market.get("nasdaq", 0)
        sp500 = market.get("sp500", 0)
        brent = market.get("brent", 0)

        candidates = []

        # 후보 1: 환율 이슈
        if usd_krw and usd_krw > 1400:
            label = "위험" if usd_krw > 1500 else "주의"
            filters_hit = ["필터1_역사적임계값"]
            if usd_krw > 1500:
                filters_hit.append("필터4_시의성")
            strength = self.filters.calculate_strength(filters_hit, usd_krw=usd_krw)
            candidates.append({
                "topic": f"원달러 환율 {usd_krw:.0f}원 → {label} 수준",
                "filters_hit": filters_hit,
                "strength": round(strength, 1),
                "data_evidence": {"usd_krw": usd_krw},
                "related_keywords": ["환율", "원화", "달러", "외환"]
            })

        # 후보 2: VIX 공포 구간
        vix = market.get("vix", 0)
        if vix and vix > 20:
            label = "극단적 공포" if vix > 30 else "공포"
            filters_hit = ["필터1_역사적임계값"]
            if vix > 30:
                filters_hit.append("필터2_역설적현상")
            strength = self.filters.calculate_strength(filters_hit)
            candidates.append({
                "topic": f"VIX {vix:.1f} → {label} 구간 진입",
                "filters_hit": filters_hit,
                "strength": round(strength, 1),
                "data_evidence": {"vix": vix},
                "related_keywords": ["공포", "변동성", "시장심리", "VIX"]
            })

        # 후보 3: KOSPI 급락
        kospi_chg = market.get("kospi_1d_change", 0)
        if kospi_chg and kospi_chg < -2.0:
            filters_hit = ["필터1_역사적임계값", "필터4_시의성"]
            strength = self.filters.calculate_strength(filters_hit)
            candidates.append({
                "topic": f"KOSPI 하루 {kospi_chg:.1f}% 급락",
                "filters_hit": filters_hit,
                "strength": round(strength, 1),
                "data_evidence": {"kospi_change": kospi_chg},
                "related_keywords": ["코스피", "급락", "외국인", "한국증시"]
            })

        # 후보 4: 유가 이슈
        wti = market.get("wti_oil", 0)
        if wti and wti > 90:
            label = "위험" if wti > 100 else "주의"
            filters_hit = ["필터1_역사적임계값", "필터5_연결고리"]
            strength = self.filters.calculate_strength(filters_hit)
            candidates.append({
                "topic": f"WTI 유가 ${wti:.1f} → {label} 수준",
                "filters_hit": filters_hit,
                "strength": round(strength, 1),
                "data_evidence": {"wti": wti},
                "related_keywords": ["유가", "원유", "에너지", "인플레이션", "호르무즈"]
            })

        # 후보 5: 권위자 신호
        for signal in sentiment.get("authority_signals", []):
            filters_hit = ["필터6_권위자변화", "필터4_시의성"]
            strength = self.filters.calculate_strength(filters_hit)
            candidates.append({
                "topic": f"{signal.get('person')} → {signal.get('action')}",
                "filters_hit": filters_hit,
                "strength": round(strength, 1),
                "data_evidence": signal,
                "related_keywords": [signal.get('person', '')]
            })

        # 복합 신호: 환율 + 유가 동시
        if usd_krw and usd_krw > 1400 and wti and wti > 85:
            filters_hit = [
                "필터1_역사적임계값", "필터2_역설적현상",
                "필터4_시의성", "필터5_연결고리"
            ]
            strength = self.filters.calculate_strength(filters_hit, usd_krw=usd_krw, vix=vix)
            candidates.append({
                "topic": f"환율 {usd_krw:.0f}원 + 유가 ${wti:.1f} 동시 급등 → 복합 위기 신호",
                "filters_hit": filters_hit,
                "strength": round(strength, 1),
                "data_evidence": {"usd_krw": usd_krw, "wti": wti},
                "related_keywords": ["환율", "유가", "인플레이션", "스태그플레이션"]
            })

        # 복합 신호: 환율 극단 + VIX 공포 동시
        if usd_krw and usd_krw > 1480 and vix and vix > 20:
            filters_hit_ev = [
                "필터1_역사적임계값", "필터2_역설적현상",
                "필터4_시의성", "필터3_미반영격차"
            ]
            strength_ev = self.filters.calculate_strength(filters_hit_ev, usd_krw=usd_krw, vix=vix)
            candidates.append({
                "topic": f"환율 {usd_krw:.0f}원 + VIX {vix:.1f} 동시 위기 → 복합 공포 신호",
                "filters_hit": filters_hit_ev,
                "strength": round(strength_ev, 1),
                "data_evidence": {"usd_krw": usd_krw, "vix": vix},
                "related_keywords": ["환율", "VIX", "공포", "변동성", "위기"]
            })

        # 후보 6: 연결고리 신호 (필터5)
        f5_hit, f5_details = self.filters.filter5_causal_chain(
            raw_data.get("market", {}), raw_data.get("sentiment", {})
        )
        if f5_hit:
            for detail in f5_details[:1]:  # 가장 강한 연결고리 1개만
                filters_hit_f5 = ["필터5_연결고리"]
                if usd_krw and usd_krw > 1450:
                    filters_hit_f5.append("필터1_역사적임계값")
                strength_f5 = self.filters.calculate_strength(filters_hit_f5)
                candidates.append({
                    "topic": detail,
                    "filters_hit": filters_hit_f5,
                    "strength": round(strength_f5, 1),
                    "data_evidence": {"detail": detail},
                    "related_keywords": ["연결고리", "파급효과"]
                })

        # 후보 7: 역설적 현상 (필터2)
        f2_hit, f2_details = self.filters.filter2_paradox(
            raw_data.get("market", {}), raw_data.get("sentiment", {})
        )
        if f2_hit:
            for detail in f2_details[:1]:
                filters_hit_f2 = ["필터2_역설적현상", "필터4_시의성"]
                strength_f2 = self.filters.calculate_strength(filters_hit_f2)
                candidates.append({
                    "topic": detail,
                    "filters_hit": filters_hit_f2,
                    "strength": round(strength_f2, 1),
                    "data_evidence": {"detail": detail},
                    "related_keywords": ["역설", "반전", "이상"]
                })

        # --- 추가 지표 기반 필터링 (필터1, 2, 5) ---

        # 1. 필터1 (역사적 임계값) 추가
        if gold > 3000:
            f1_hit = ["필터1_역사적임계값"]
            strength = self.filters.calculate_strength(f1_hit) + 0.5
            candidates.append({
                "topic": f"금 가격 {gold:,.0f}달러 돌파 → 역사적 최고가",
                "filters_hit": f1_hit,
                "strength": round(strength, 1),
                "data_evidence": {"gold": gold},
                "related_keywords": ["금", "안전자산", "인플레이션"]
            })

        if dxy > 105:
            f1_hit = ["필터1_역사적임계값"]
            strength = self.filters.calculate_strength(f1_hit)
            if dxy > 108: strength += 0.5
            candidates.append({
                "topic": f"달러인덱스 {dxy:.1f} 돌파 → 슈퍼 달러 재현",
                "filters_hit": f1_hit,
                "strength": round(strength, 1),
                "data_evidence": {"dxy": dxy},
                "related_keywords": ["달러", "강달러", "DXY"]
            })

        if us10y > 4.5:
            f1_hit = ["필터1_역사적임계값"]
            strength = self.filters.calculate_strength(f1_hit)
            if us10y > 5.0: strength += 0.5
            candidates.append({
                "topic": f"미 국채 10년물 금리 {us10y:.2f}% 급등 → 긴축 우려",
                "filters_hit": f1_hit,
                "strength": round(strength, 1),
                "data_evidence": {"us10y": us10y},
                "related_keywords": ["국채금리", "미국채", "금리"]
            })

        # 2. 필터2 (역설적 현상) 추가
        if gold > 2800 and kospi_chg < -1.5:
            f2_hit = ["필터2_역설적현상"]
            strength = self.filters.calculate_strength(f2_hit)
            if gold > 3000: strength += 0.5
            candidates.append({
                "topic": "금값 급등 + 코스피 하락 → 위험자산 이탈 뚜렷",
                "filters_hit": f2_hit,
                "strength": round(strength, 1),
                "data_evidence": {"gold": gold, "kospi_chg": kospi_chg},
                "related_keywords": ["안전자산", "도피", "시장불안"]
            })

        if vix > 30 and wti > 95: # NASDAQ 급락 프록시로 VIX/WTI 활용
            f2_hit = ["필터2_역설적현상"]
            candidates.append({
                "topic": "기술주 급락 + 유가 급등 → 스태그플레이션 공포",
                "filters_hit": f2_hit,
                "strength": round(self.filters.calculate_strength(f2_hit), 1),
                "data_evidence": {"vix": vix, "wti": wti},
                "related_keywords": ["스태그플레이션", "나스닥", "유가"]
            })

        # 3. 필터5 (연결고리) 추가
        if wti > 90 and brent > 95:
            f5_hit = ["필터5_연결고리"]
            candidates.append({
                "topic": "WTI-브렌트유 동시 폭등 → 수입물가 전방위 압박",
                "filters_hit": f5_hit,
                "strength": round(self.filters.calculate_strength(f5_hit), 1),
                "data_evidence": {"wti": wti, "brent": brent},
                "related_keywords": ["유가", "에너지", "인플레이션"]
            })

        if dxy > 105 and usd_krw > 1400:
            f5_hit = ["필터5_연결고리"]
            strength = self.filters.calculate_strength(f5_hit)
            if dxy > 108: strength += 0.5
            candidates.append({
                "topic": "강달러 → 원달러 환율 동반 상승 → 수출입 복합 영향",
                "filters_hit": f5_hit,
                "strength": round(strength, 1),
                "data_evidence": {"dxy": dxy, "usd_krw": usd_krw},
                "related_keywords": ["환율", "달러", "연결고리"]
            })

        # 강도 기준 내림차순 정렬
        candidates.sort(key=lambda x: x["strength"], reverse=True)
        return candidates

    def select_topic(self, candidates):
        """강도 기준 최종 토픽 선정"""
        for c in candidates:
            if c["strength"] >= 6.0:
                c["selected"] = True
                c["content_type"] = "롱폼" if c["strength"] >= 8.0 else "쇼츠"
                c["reject_reason"] = None
                return c

        # 선정 기준 미달 시 최상위 후보 반환
        if candidates:
            best = candidates[0]
            best["selected"] = False
            best["content_type"] = None
            best["reject_reason"] = f"최고 강도 {best['strength']} → 임계값(6.0) 미달"
            return best

        return None

    def save_results(self, candidates, selected):
        """결과 저장"""
        all_candidates = []
        for i, c in enumerate(candidates):
            is_selected = (
                selected and
                c["topic"] == selected.get("topic") and
                selected.get("selected")
            )
            all_candidates.append({
                "rank": i + 1,
                "topic": c["topic"],
                "filters_hit": c["filters_hit"],
                "filter_count": len(c["filters_hit"]),
                "strength": c["strength"],
                "selected": is_selected,
                "content_type": c.get("content_type") if is_selected else None,
                "reject_reason": None if is_selected else "더 강한 신호가 선정됨"
            })

        # candidates.json 저장
        (self.signal_dir / "candidates.json").write_text(
            json.dumps({
                "date": self.today,
                "total_candidates": len(all_candidates),
                "selected_count": 1 if (selected and selected.get("selected")) else 0,
                "candidates": all_candidates
            }, ensure_ascii=False, indent=2)
        )

        # today_signal.json 저장
        if selected and selected.get("selected"):
            (self.signal_dir / "today_signal.json").write_text(
                json.dumps({
                    "date": self.today,
                    "topic": selected["topic"],
                    "strength": selected["strength"],
                    "content_type": selected["content_type"],
                    "filters_hit": selected["filters_hit"],
                    "data_evidence": selected.get("data_evidence", {}),
                    "related_keywords": selected.get("related_keywords", []),
                    "level2_chain": [],
                    "is_republish": False,
                    "urgency": "HIGH" if selected["strength"] >= 8.0 else "MEDIUM"
                }, ensure_ascii=False, indent=2)
            )

        # signal_log.json 업데이트
        log = {"signals": []}
        if self.history_path.exists():
            try:
                log = json.loads(self.history_path.read_text())
            except Exception:
                pass

        log["signals"].append({
            "date": self.today,
            "topic": selected["topic"] if selected else "없음",
            "strength": selected["strength"] if selected else 0,
            "selected": selected.get("selected", False) if selected else False,
            "total_candidates": len(candidates)
        })

        self.history_path.write_text(
            json.dumps(log, ensure_ascii=False, indent=2)
        )

    def run(self, collector_result=None):
        print(f"\n🔍 AGENT-03 DETECTOR 시작 [{self.today}]")

        raw_data = self.load_raw_data()
        if not raw_data:
            print("  Raw 데이터 없음 → AGENT-01 먼저 실행 필요")
            return {}

        candidates = self.build_candidates(raw_data)
        print(f"  감지된 후보 신호: {len(candidates)}개")

        selected = self.select_topic(candidates)

        if selected and selected.get("selected"):
            print(f"  ✅ 선정 완료: {selected['topic']}")
            print(f"  강도: {selected['strength']} / 유형: {selected['content_type']}")
        else:
            print("  오늘 선정 기준 충족 신호 없음")
            if selected:
                print(f"  최상위 후보: {selected['topic']} (강도 {selected['strength']})")

        self.save_results(candidates, selected)
        print("✅ AGENT-03 완료\n")
        return {"selected": selected, "candidates": candidates}


if __name__ == "__main__":
    agent = DetectorAgent()
    agent.run()
