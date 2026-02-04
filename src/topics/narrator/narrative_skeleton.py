from typing import Any, Dict, List
import json
from pathlib import Path

class NarrativeSkeletonBuilder:
    """
    IS-96-3: Narrative Skeleton Layer
    Converts Interpretation + Speakability into a script skeleton.
    """

    def build(self, unit: Dict[str, Any], speakability: Dict[str, Any]) -> Dict[str, Any]:
        flag = speakability.get("speakability_flag", "DROP")
        reasons = speakability.get("speakability_reasons", [])
        
        if flag == "DROP":
            return {
                "speakability_flag": flag,
                "drop_note": f"Topic dropped: {'; '.join(reasons)}"
            }

        # Common Data
        sector = unit.get("target_sector", "Unknown Sector")
        key = unit.get("interpretation_key", "UNKNOWN_SHIFT")
        metrics = unit.get("derived_metrics_snapshot", {})
        tags = unit.get("evidence_tags", [])
        
        # Determine Tone
        mode = unit.get("mode", "STRUCTURAL")
        prefix = "[READY] " if flag == "READY" else "[WATCH/HOLD] "
        
        # IS-96-6 Historical Framing Check
        historical_frame = None
        frame_path = Path(__file__).parent.parent.parent.parent / "data" / "decision" / "historical_shift_frame.json"
        if frame_path.exists():
            try:
                frame_data = json.loads(frame_path.read_text())
                if frame_data.get("interpretation_key") == key:
                    historical_frame = frame_data
            except:
                pass

        # 1. HOOK & CLAIM
        if historical_frame:
            # Shift Upgrade
            shift_type = historical_frame.get('shift_type', 'REGIME_SHIFT')
            hist_claim = historical_frame.get('historical_claim', '')
            hook = f"[{shift_type}] {hist_claim} {sector} 섹터가 새로운 국면에 진입했습니다."
            claim = f"Era Declaration: {unit.get('structural_narrative', '')} (Shift Confidence: High)"
        elif mode == "HYPOTHESIS_JUMP":
            hook = f"[HYPOTHESIS] 지금은 '확정'이 아니라 '가능성'이다. {sector} 섹터의 {unit.get('reasoning_chain', {}).get('trigger_event', '새로운 시그널')}을 진단합니다."
            claim = f"결정론적 가설: {unit.get('structural_narrative', '변화 가능성이 포착되었습니다.')}"
        else:
            hook = f"{prefix}{sector} 섹터에서 포착된 {key} 시그널의 실체를 확인합니다."
            claim = f"{unit.get('structural_narrative', '구조적 변화가 감지되었습니다.')}"

        # 2. EVIDENCE_3 (Derived from reasons and metrics)
        evidence = []
        if mode == "HYPOTHESIS_JUMP":
            chain = unit.get("reasoning_chain", {})
            evidence.append(f"트리거: {chain.get('trigger_event', '카탈리스트 포착')}")
            evidence.append(f"메커니즘: {chain.get('mechanism', '수급 이동 경로 분석 중')}")
            evidence.append(f"수혜 주체: {', '.join(chain.get('beneficiaries', []))}")
        else:
            evidence.append(f"명분 점수(Pretext) {metrics.get('pretext_score', 0.0)}로 구조적 타당성 확보")
            evidence.append(f"주요 데이터 태그 정렬: {', '.join(tags[:3])}")
            evidence.append(f"입증 근거: {reasons[0] if reasons else '데이터 정합성 확인'}")
        
        # 3. CHECKLIST_3
        if mode == "HYPOTHESIS_JUMP":
            checklist = unit.get("reasoning_chain", {}).get("verification_checklist", [])
        else:
            checklist = [
                f"{tags[0] if len(tags)>0 else 'POLICY'} 후속 집행 데이터 업데이트 확인",
                f"섹터 수급(FLOW_ROTATION)의 지속성 여부 체크",
                f"실적(EARNINGS_VERIFY) 기반 펀더멘털 괴리율 모니터링"
            ]

        # 4. WHAT_TO_AVOID
        avoid = [
            "단기 가격 변동성에 의한 일시적 노이즈와 구조적 추세 혼동 주의",
            "개별 종목 뉴스가 아닌 섹터 전체의 자본 이동 경로 중심 분석 필수"
        ]

        skeleton = {
            "speakability_flag": flag,
            "hook": hook,
            "claim": claim,
            "evidence_3": evidence[:3],
            "checklist_3": checklist[:3],
            "what_to_avoid": avoid[:2]
        }
        
        if historical_frame:
             skeleton["era_declaration_block"] = {
                 "shift_type": historical_frame.get("shift_type"),
                 "what_changed": historical_frame.get("what_changed", []),
                 "what_breaks_next": historical_frame.get("what_breaks_next", [])
             }

        # 5. HOLD_TRIGGER (Optional)
        if flag == "HOLD":
            trigger = "미확인 입증 데이터(정책 실행/실적 발표)의 실제 수치 확인 시 READY 전환"
            if "EARNINGS_VERIFY" not in tags:
                trigger = "차기 실적 발표(EARNINGS_VERIFY) 데이터 반영 시점까지 관망"
            skeleton["hold_trigger"] = trigger

        return skeleton

def build_narrative_skeleton(interpretation_unit: Dict[str, Any], speakability: Dict[str, Any]) -> Dict[str, Any]:
    builder = NarrativeSkeletonBuilder()
    return builder.build(interpretation_unit, speakability)
