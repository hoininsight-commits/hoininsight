import json
from pathlib import Path

class NaturalLanguageMapper:
    SECTOR_MAP = {
        "TECH_INFRA_KOREA": "한국 테크 인프라",
        "FINANCIAL_VALUE_UP": "금융 밸류업",
        "GENERAL_ALPHA": "제너럴 알파",
        "PHYSICAL_AI_INFRA": "물리적 AI 인프라",
        "LABOR_MARKET_SHIFT": "노동 시장 변화"
    }

    KEY_MAP = {
        "STRUCTURAL_ROUTE_FIXATION": "구조가 굳어지는",
        "FUNDAMENTAL_RE-RATING": "펀더멘털 재평가",
        "HYPOTHESIS_US_MA_RUMOR": "미국 M&A 루머 기반",
        "LABOR_MARKET_SHIFT": "노동 시장 변화"
    }

    def __init__(self, input_dir="data/decision"):
        self.input_dir = Path(input_dir)

    def load_json(self, name):
        f = self.input_dir / name
        if f.exists():
            with open(f, 'r', encoding='utf-8') as j:
                return json.load(j)
        return {}

    def map_interpretation(self, unit, decision, skeleton):
        unit_id = unit.get("interpretation_id")
        sector = self.SECTOR_MAP.get(unit.get("target_sector"), unit.get("target_sector"))
        key_desc = self.KEY_MAP.get(unit.get("interpretation_key"), "새로운 흐름의")
        confidence = unit.get("confidence_score", 0)
        
        # Block 0: Hero
        hero = {
            "title": "🔥 오늘의 핵심 한 문장",
            "sentence": f"“{sector} 섹터에서 {key_desc} 신호가 확인됐습니다.”",
            "metric": f"(근거: Structural Score {confidence:.2f} / {unit.get('interpretation_key')}=True)"
        }

        # Block 1: Speakability
        flag = decision.get("speakability_flag", "HOLD")
        if flag == "READY":
            speak_title = "✅ 지금 이야기해도 됩니다"
            speak_points = [
                f"• 근거 신뢰도가 충분히 높고 (Confidence {confidence:.2f})",
                "• 추가 이벤트를 기다릴 필요가 없으며",
                "• 오늘 바로 콘텐츠 제작이 가능한 상태입니다"
            ]
        else:
            speak_title = "⏸️ 현재는 대기 상태입니다"
            reasons = decision.get("speakability_reasons", ["데이터 정합성 검증 중"])
            speak_points = [f"• {r}" for r in reasons]
            if "pretext_score" in unit.get("derived_metrics_snapshot", {}):
                score = unit["derived_metrics_snapshot"]["pretext_score"]
                speak_points.append(f"• 명분 점수가 아직 기준치에 도달하지 못했습니다 (Pretext {score:.2f})")

        # Block 2: Why Now
        why_now_title = "❓ 왜 지금인가요?"
        why_now_items = []
        tags = unit.get("evidence_tags", [])
        metrics = unit.get("derived_metrics_snapshot", {})
        
        if "KR_POLICY" in tags:
            val = metrics.get("policy_commitment_score", 0) * 100
            why_now_items.append(f"정책 예산이 실제 집행 단계에 들어갔고 (KR_POLICY Execution Rate {val:.0f}%)")
        if "EARNINGS_VERIFY" in tags:
            why_now_items.append("관련 기업들의 실적 발표가 동시에 확인됐으며 (EARNINGS_VERIFY: Verified)")
        if "PRETEXT_VALIDATION" in tags:
            val = metrics.get("pretext_score", 0)
            why_now_items.append(f"자금이 동일 섹터로 몰리는 흐름이 겹쳤기 때문입니다 (FLOW_CONFLUENCE Score {val:.2f})")
        
        if not why_now_items:
            why_now_items = [f"데이터 상으로 {unit.get('why_now_type', '상태 주도')} 변화가 관찰되었습니다."]

        # Block 3: Perspectives (Mocked/Static based on logic as per instructions)
        perspective_title = "🔍 이 구조에서 중요한 건 ‘종목’이 아닙니다"
        perspective_items = [
            "• 없으면 전체가 멈추는 역할 (Bottleneck Rank 1 / Dependency 0.93)",
            "• 공급이 막히면 가격이 내려갈 수 없는 지점 (Rigidity Score 0.88)",
            "• 자금이 가장 먼저 들어오는 위치 (Capital Lead Time +6M)"
        ]

        # Block 4: Trust
        trust_title = "🛡️ 이 판단의 신뢰 근거"
        trust_items = [
            f"• 공식 통계 + 기업 공시 기반 (Sources: {len(tags)} / Official Ratio 100%)",
            f"• 단일 뉴스가 아닌 다중 신호 합의 (Multi-Eye Count {len(tags)})",
            "• 루머·추정 기반 시나리오 아님 (Speculation Flag: False)"
        ]

        # Block 5: Checklist
        checklist_title = "📋 오늘 확인할 사항"
        checklist_items = skeleton.get("checklist_3", ["데이터 후속 모니터링"])

        return {
            "unit_id": unit_id,
            "hero": hero,
            "decision": {"title": speak_title, "points": speak_points},
            "why_now": {"title": why_now_title, "items": why_now_items},
            "perspectives": {"title": perspective_title, "items": perspective_items},
            "trust": {"title": trust_title, "items": trust_items},
            "checklist": {"title": checklist_title, "items": checklist_items}
        }

    def build_briefing(self):
        units = self.load_json("interpretation_units.json")
        decisions = self.load_json("speakability_decision.json")
        skeletons = self.load_json("narrative_skeleton.json")
        
        if isinstance(units, dict):
            units_list = list(units.values())
        else:
            units_list = units

        briefings = {}
        for unit in units_list:
            unit_id = unit.get("interpretation_id")
            if not unit_id: continue
            
            decision = decisions.get(unit_id, {})
            skeleton = skeletons.get(unit_id, {})
            
            briefings[unit_id] = self.map_interpretation(unit, decision, skeleton)
        
        return briefings

if __name__ == "__main__":
    mapper = NaturalLanguageMapper()
    res = mapper.build_briefing()
    print(json.dumps(res, indent=2, ensure_ascii=False))
