from __future__ import annotations
from datetime import datetime
from typing import List, Dict, Any, Optional
from .types import SpeakEligibility, DecisionTrace, DecisionEvidence

class SpeakEligibilityCheck:
    """
    Implements the hard-validated SPEAK ELIGIBILITY CHECK for Gate-based topics.
    Ensures traceability and enforces safety guardrails (G1, G2).
    """

    def evaluate(self, topic_data: Dict, evidence_pool: List[Dict] = None) -> SpeakEligibility:
        """
        Evaluates speak eligibility with decision traces and guardrails.
        evidence_pool: Optional list of raw events for artifact validation.
        """
        trace_map = {}
        
        # 1. EXPECTATION_COLLAPSE
        trace_map["EXPECTATION_COLLAPSE"] = self._check_expectation_collapse(topic_data, evidence_pool)
            
        # 2. LIQUIDITY_DIRECTION_LOCKIN
        trace_map["LIQUIDITY_DIRECTION_LOCKIN"] = self._check_liquidity_direction_lockin(topic_data, evidence_pool)
            
        # 3. NARRATIVE_CONVERGENCE
        trace_map["NARRATIVE_CONVERGENCE"] = self._check_narrative_convergence(topic_data, evidence_pool)
            
        # 4. NARRATIVE_SHIFT (Step 10-5)
        trace_map["NARRATIVE_SHIFT"] = self._check_narrative_shift(topic_data, evidence_pool)

        # 5. Anchor Detection (Step 10-6)
        anchors = self._detect_anchors(topic_data, evidence_pool)

        # Final Decision Logic with Guardrails
        triggered_names = [name for name, trace in trace_map.items() if trace.triggered]
        
        # Guardrail G1: Market Move Check
        is_move_insufficient = self._is_market_move_insufficient(topic_data)
        
        eligible = len(triggered_names) > 0
        
        if is_move_insufficient:
            liquidity_trace = trace_map["LIQUIDITY_DIRECTION_LOCKIN"]
            high_conf_liquidity = any(e.confidence >= 0.7 for e in liquidity_trace.evidence)
            if not (liquidity_trace.triggered and high_conf_liquidity):
                eligible = False
                for name in triggered_names:
                    trace_map[name].reasons.append("FORCED_FALSE (G1): Insufficient market move data and no high-confidence liquidity lock-in.")

        # Final Safety Guard (Step 10-6): Narrative Shift + Anchor requirement
        if "NARRATIVE_SHIFT" in triggered_names and not anchors:
            eligible = False
            summary = "Narrative shift detected, awaiting anchor confirmation"
        else:
            summary = self._generate_summary(eligible, triggered_names, is_move_insufficient)
        
        return SpeakEligibility(
            eligible=eligible,
            triggers=triggered_names if eligible else [],
            summary=summary,
            trace=trace_map,
            anchors=anchors
        )

    def _is_market_move_insufficient(self, data: Dict) -> bool:
        """Heuristic check if market move data is missing."""
        # Check why_people_confused for placeholders
        confused_text = data.get("why_people_confused", "").upper()
        if "INSUFFICIENT DATA" in confused_text or "NEEDS DATA" in confused_text:
            return True
        return False

    def _detect_anchors(self, data: Dict, evidence_pool: List[Dict]) -> List[Dict[str, Any]]:
        """
        [STEP 10-6] Detects Schedule, Capital, or Quantitative Anchors.
        """
        anchors = []
        text = (data.get("why_people_confused", "") + " " + " ".join(data.get("key_reasons", []))).lower()
        
        # 1) Schedule Anchor
        schedule_keywords = ["2026", "2027", "q1", "q2", "q3", "q4", "milestone", "일정", "발표 예정"]
        if any(k in text for k in schedule_keywords):
            anchors.append({"type": "SCHEDULE", "reason": "Future date or milestone detected in text."})
            
        # 2) Capital Anchor
        capital_keywords = ["capex", "설비투자", "계약", "수주", "order", "contract", "신규 투자"]
        if any(k in text for k in capital_keywords):
            anchors.append({"type": "CAPITAL", "reason": "Capital commitment (capex/contract) detected."})
            
        # 3) Quantitative Constraint
        quant_keywords = ["threshold", "임계점", "capacity", "limit", "한계", "threshold", "수치적 제한"]
        if any(k in text for k in quant_keywords):
            anchors.append({"type": "QUANTITATIVE", "reason": "Quantitative threshold or capacity limit detected."})
            
        # Also check evidence_pool (events)
        if evidence_pool:
            for ev in evidence_pool:
                ev_text = (ev.get("title", "") + " " + ev.get("content", "")).lower()
                if "contract" in ev_text or "수주" in ev_text:
                    anchors.append({"type": "CAPITAL", "source": ev.get("event_id"), "reason": "Contract detected in event pool."})
                if any(k in ev_text for k in ["threshold", "limit"]):
                    anchors.append({"type": "QUANTITATIVE", "source": ev.get("event_id"), "reason": "Limit detected in event pool."})
                    
        return anchors

    def _check_expectation_collapse(self, data: Dict, evidence_pool: List[Dict]) -> DecisionTrace:
        trace = DecisionTrace(trigger_name="EXPECTATION_COLLAPSE", triggered=False)
        
        text = (data.get("why_people_confused", "") + " " + " ".join(data.get("key_reasons", []))).lower()
        keywords = ["기대 경로", "전망 수정", "구조적", "일시적이지 않은", "revision", "structural", "collapsed"]
        
        has_keywords = any(k in text for k in keywords)
        
        # Guardrail G2: Expectation Artifact Check
        artifact_evidence = []
        if evidence_pool:
            for ev in evidence_pool:
                # Check for guidance/consensus revision in event title or content
                ev_text = (ev.get("title", "") + " " + ev.get("content", "")).lower()
                if any(k in ev_text for k in ["guidance", "consensus", "revision", "가이던스", "컨센서스", "수정"]):
                    artifact_evidence.append(DecisionEvidence(
                        key=f"event:{ev.get('event_id', 'unknown')}",
                        value=ev.get("title"),
                        source=ev.get("source", "N/A"),
                        timestamp=datetime.now().isoformat(), # Ideally from event
                        confidence=ev.get("trust_score", 0.5)
                    ))

        if has_keywords:
            if artifact_evidence:
                trace.triggered = True
                trace.reasons.append("Keywords detected AND explicit expectation artifact (guidance/consensus) found in evidence pool.")
                trace.evidence = artifact_evidence
            else:
                trace.reasons.append("REJECTED (G2): Keywords detected, but NO explicit guidance/consensus revision artifact found.")
        else:
            trace.reasons.append("No expectation collapse keywords detected in topic metadata.")
            
        return trace

    def _check_liquidity_direction_lockin(self, data: Dict, evidence_pool: List[Dict]) -> DecisionTrace:
        trace = DecisionTrace(trigger_name="LIQUIDITY_DIRECTION_LOCKIN", triggered=False)
        text = (data.get("why_people_confused", "") + " " + " ".join(data.get("key_reasons", []))).lower()
        keywords = ["자금 흐름", "섹터 회전", "유입", "이탈", "스타일 변화", "capital flow", "rotation", "inflow"]
        
        if any(k in text for k in keywords):
            trace.triggered = True
            trace.reasons.append("Keywords related to capital flow or asset rotation detected.")
            # Mock evidence from numbers if available
            for n in data.get("numbers", []):
                if any(k in n.get("label", "").lower() for k in ["flow", "inflow", "outflow", "자금"]):
                    trace.evidence.append(DecisionEvidence(
                        key=n.get("label"),
                        value=f"{n.get('value')} {n.get('unit')}",
                        timestamp=datetime.now().isoformat(),
                        confidence=0.8
                    ))
        else:
            trace.reasons.append("No liquidity commitment keywords detected.")
        return trace

    def _check_narrative_convergence(self, data: Dict, evidence_pool: List[Dict]) -> DecisionTrace:
        trace = DecisionTrace(trigger_name="NARRATIVE_CONVERGENCE", triggered=False)
        text = (data.get("why_people_confused", "") + " " + " ".join(data.get("key_reasons", []))).lower()
        keywords = ["핵심", "지배적", "공통된 해석", "dominant narrative", "consensus", "converged"]
        
        if any(k in text for k in keywords):
            trace.triggered = True
            trace.reasons.append("Dominant narrative indicators (e.g., 'core', 'dominant', 'consensus') found in explanation.")
        else:
            trace.reasons.append("No narrative convergence indicators found.")
        return trace

    def _check_narrative_shift(self, data: Dict, evidence_pool: List[Dict]) -> DecisionTrace:
        """
        [STEP 10-5] Detects when the reason for a market move has changed.
        """
        trace = DecisionTrace(trigger_name="NARRATIVE_SHIFT", triggered=False)
        text = (data.get("why_people_confused", "") + " " + " ".join(data.get("key_reasons", []))).lower()
        
        # 1) DRIVER_CHANGE
        driver_keywords = ["->", "에서", "전환", "중심 이동", "driver shift", "pivot"]
        detected_driver = any(k in text for k in driver_keywords)
        
        # 2) VALUE_CHAIN_SHIFT
        value_chain_keywords = ["벨류체인", "공급망", "소재", "부품", "장비", "value chain", "supply chain", "upstream", "downstream"]
        detected_vc = any(k in text for k in value_chain_keywords)
        
        # 3) LANGUAGE_SHIFT
        lang_keywords = ["필수", "구조적", "기대", "growth", "necessity", "structural", "mandatory"]
        detected_lang = any(k in text for k in lang_keywords)
        
        if detected_driver or detected_vc or detected_lang:
            trace.triggered = True
            trace.reasons.append("Narrative shift detected (Driver/Value-Chain/Language).")
        
        trace.metadata = {
            "detected_driver_change": detected_driver,
            "detected_value_chain_shift": detected_vc,
            "detected_language_shift": detected_lang,
            "evidence_sources": [ev.get("source", "N/A") for ev in (evidence_pool or [])]
        }
        
        return trace

    def _generate_summary(self, eligible: bool, triggers: List[str], move_insufficient: bool) -> str:
        if not eligible:
            if move_insufficient:
                return "SPEAK_REJECTED: Insufficient market move data (G1)."
            return "No state transition detected. Topic remains GATE_ONLY."
        
        return f"STATE TRANSITION: {', '.join(triggers)} detected. Eligible for speaking."
