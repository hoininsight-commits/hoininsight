import hashlib
from datetime import datetime
from typing import List, Dict, Any

class HypothesisJumpEngine:
    """
    IS-96-5: Hypothesis Jump Mode
    Converts CATALYST_EVENT (IS-95-2) into structured Interpretation Units.
    """

    def process_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        hypothesis_units = []
        for event in events:
            unit = self._create_unit(event)
            if unit:
                hypothesis_units.append(unit)
        return hypothesis_units

    def _create_unit(self, event: Dict[str, Any]) -> Dict[str, Any]:
        tag = event.get("tag", "UNKNOWN")
        entities = event.get("entities", [])
        title = event.get("title", "")
        
        # Deterministic Reasoning Chain Mapping
        mechanism, affected_layer, beneficiaries = self._map_logic(tag, title, entities)
        
        unit_id = f"HYP-{hashlib.sha256(event['event_id'].encode()).hexdigest()[:8]}"
        
        return {
            "interpretation_id": unit_id,
            "mode": "HYPOTHESIS_JUMP",
            "as_of_date": datetime.now().strftime("%Y-%m-%d"),
            "target_sector": self._detect_sector(entities, tag),
            "interpretation_key": f"HYPOTHESIS_{tag}",
            "why_now_type": event.get("why_now_hint", "State-driven"),
            "confidence_score": self._map_confidence(event.get("confidence", "C")),
            "evidence_tags": [tag, "HYPOTHESIS_JUMP"],
            "structural_narrative": f"{title} 기반 {mechanism}. {affected_layer} 층위의 변화가 관찰됩니다.",
            "reasoning_chain": {
                "trigger_event": title,
                "mechanism": mechanism,
                "affected_layer": affected_layer,
                "beneficiaries": beneficiaries,
                "risks": ["신뢰도 낮은 단일 출처 정보일 가능성", "데이터 확정 전 시장 오인 가능성"],
                "verification_checklist": self._generate_checklist(tag)
            },
            "derived_metrics_snapshot": {
                "pretext_score": 0.82,  # Baseline for hypothesis
                "policy_commitment_score": 0.0,
                "hypothesis_source_trust": event.get("confidence", "C")
            },
            "source_ref": event.get("source", {})
        }

    def _map_logic(self, tag: str, title: str, entities: List[str]):
        # Deterministic rule-based mapping
        t_low = title.lower()
        if "MA_RUMOR" in tag or "takeover" in t_low or "merger" in t_low or "acquisition" in t_low:
            return "자본 구조 재편 및 수급 집중", "CAPITAL_STRUCTURE", entities + ["Acquirer Shareholders"]
        if "SEC_FILING" in tag or "8-K" in t_low or "filing" in t_low:
            return "공식 거버넌스 및 계약 변곡점", "GOVERNANCE_LAYER", entities + ["Board of Directors"]
        if "CONTRACT_AWARD" in tag or "award" in t_low or "contract" in t_low or "deal" in t_low:
            return "실적 가시성 및 공급망 점유율 확대", "EBITDA_VISIBILITY", entities + ["Prime Contractor"]
        return "신규 카탈리스트 영향 분석 중", "CORE_LOGIC", entities + ["Related Sector"]

    def _detect_sector(self, entities: List[str], tag: str) -> str:
        # Simple heuristic mapping
        tech_keywords = ["NVIDIA", "AAPL", "NVDA", "SEMICON", "xAI", "SpaceX", "Tesla", "TSLA"]
        if any(e.upper() in tech_keywords for e in entities) or "SEC" in tag:
            return "TECH_INFRA"
        if "KR" in tag:
            return "KR_SEMICON_DOMESTIC"
        return "GENERAL_ALPHA"

    def _map_confidence(self, conf_str: str) -> float:
        mapping = {"A": 0.90, "B": 0.75, "C": 0.50}
        return mapping.get(conf_str, 0.40)

    def _generate_checklist(self, tag: str) -> List[str]:
        base = ["독립 소스(필링/공식 발표) 교차 확인", "관련 엔티티의 직접적 부인 여부 감시"]
        if "RUMOR" in tag:
            base.append("수급 이동(FLOW_ROTATION) 시차 발생 여부 체크")
        else:
            base.append("계약 조건의 상세 이행 스케줄 데이터 확보")
        return base
