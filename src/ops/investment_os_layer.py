#!/usr/bin/env python3
import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any

class InvestmentOSLayer:
    """
    Phase 24: Structural Investment OS Layer
    Combines Regime + Conflict + Linkage + Decision for operational orchestration.
    No-Behavior-Change: Interpretation only, no manual score generation.
    """

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.logger = logging.getLogger("InvestmentOS")
        self.ymd_dash = datetime.now().strftime("%Y-%m-%d")

    def _load_json(self, relative_path: str) -> Dict:
        path = self.base_dir / relative_path
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except Exception as e:
            self.logger.error(f"Failed to load {path}: {e}")
            return {}

    def run(self):
        self.logger.info(f"Running Investment OS Layer for {self.ymd_dash}...")

        # 1. Load Inputs
        regime_p = self._load_json("data_outputs/ops/regime_state.json")
        conflict_p = self._load_json("data_outputs/ops/conflict_density_pack.json")
        linkage_p = self._load_json("data_outputs/ops/stock_linkage_pack.json")
        
        # fallback for today.json / decision card
        decision_card = self._load_json("data/decision/final_decision_card.json") or {}
        if not decision_card:
            # check the cards directory for the latest
            cards_dir = self.base_dir / "data/decision/final_decision_cards"
            if cards_dir.exists():
                files = sorted(list(cards_dir.glob("*.json")), reverse=True)
                if files: decision_card = json.loads(files[0].read_text(encoding='utf-8'))

        # 2. Extract Base Data
        regime = regime_p.get("regime", {})
        r_summary = regime_p.get("regime_summary", {})
        
        # 3. Decision Card Extraction
        # In this context, we usually have one 'Main' decision or a list of topics
        topics = []
        if decision_card.get("dataset_id"):
            topics.append(decision_card)
        # Also look at conflict pack as it is broader
        topics_meta = {t["dataset_id"]: t for t in conflict_p.get("topics", [])}
        linkage_meta = {l["dataset_id"]: l for l in linkage_p.get("topics", [])}

        # 4. OS Classification & Priority Selection
        priority_topics = []
        
        # Axis mapping for regime alignment
        regime_axes = []
        if regime.get("liquidity_state") == "TIGHTENING": regime_axes += ["Liquidity", "Rates"]
        if regime.get("policy_state") == "RESTRICTIVE": regime_axes += ["Policy"]
        if regime.get("risk_state") == "RISK_OFF": regime_axes += ["Risk", "Safety"]
        if regime.get("yield_curve_state") == "INVERTED": regime_axes += ["Growth", "Curve"]

        for ds_id, meta in topics_meta.items():
            # Basic stats
            # Note: OS should NOT generate scores. It reads existing ones.
            intensity = meta.get("intensity", 0.0)
            n_score = meta.get("narrative_score", 0.0)
            
            # Axes check
            topic_axes = meta.get("axes", [])
            has_axis_alignment = any(a in topic_axes for a in regime_axes)
            
            # Classification logic
            density = meta.get("density_text", {})
            has_high_conflict = "high" in density.get("summary", "").lower() or (len(density.get("contradiction_pairs", [])) > 0)
            
            os_class = "MONITOR"
            if has_axis_alignment and (intensity > 60 or n_score > 60):
                os_class = "OPPORTUNITY"
            if has_high_conflict or (has_axis_alignment and regime.get("risk_state") == "RISK_OFF"):
                os_class = "RISK"

            # Action Checklist
            checklist = ["지표 추이 및 당국 발언 모니터링"]
            if os_class == "OPPORTUNITY":
                checklist = ["연관 종목군 수급/가격 반응 확인", "추가 지표 동행 여부 검증", "구조적 변곡점 시그널 탐색"]
            elif os_class == "RISK":
                checklist = ["리스크 임계값 설정 및 손절선 확인", "시장 심리 지표(VIX 등) 병행 감시", "안전자산 선호 강화 여부 체크"]

            # Merge with Linkage
            links = []
            link_data = linkage_meta.get(ds_id, {})
            for s in link_data.get("stocks", []):
                links.append({
                    "ticker": s.get("ticker"),
                    "name": s.get("name"),
                    "exposure_type": s.get("exposure_type"),
                    "risk_note": s.get("risk_note")
                })

            priority_topics.append({
                "dataset_id": ds_id,
                "title": meta.get("title", f"Topic: {ds_id}"),
                "intensity": intensity,
                "narrative_score": n_score,
                "why_now_type": meta.get("why_now_type", "Hybrid"),
                "conflict_density": "high" if has_high_conflict else "moderate",
                "axis": topic_axes,
                "os_classification": os_class,
                "reasoning": [
                    f"Regime {regime.get('liquidity_state')} 상태에서의 축(Axis) 정합성 확인" if has_axis_alignment else "상태 정합성 낮음",
                    f"분석 밀도({os_class}) 기반 대응 우선순위 설정"
                ],
                "linked_stocks": links,
                "action_card": {
                    "intent": os_class,
                    "checklist": checklist,
                    "invalidations": ["Regime 전환 발생 시 관점 재검토", "강도(Intensity) 급락 시 감시 해제"]
                }
            })

        # Sort priority_topics (OPPORTUNITY -> RISK -> MONITOR, then by intensity)
        class_map = {"OPPORTUNITY": 3, "RISK": 2, "MONITOR": 1}
        priority_topics.sort(key=lambda x: (class_map.get(x["os_classification"], 0), x["intensity"]), reverse=True)

        # 5. OS Summary & Stance
        stance = "NEUTRAL"
        if regime.get("risk_state") == "RISK_OFF": stance = "DEFENSIVE_BIAS"
        elif regime.get("liquidity_state") == "EASING": stance = "AGGRESSIVE_BIAS"

        os_summary = {
            "stance": stance,
            "focus": [a for a in set(regime_axes) if a],
            "do_not_do": ["무리한 추격 매수", "레버리지 확대 지양"] if stance == "DEFENSIVE_BIAS" else ["방어적 포지션 고수"],
            "today_watch": [f"{a} 관련 지표 발표" for a in set(regime_axes) if a]
        }

        # 6. Construct Final State
        os_state = {
            "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "date_kst": self.ymd_dash,
            "regime": {
                "state": regime.get("liquidity_state"),
                "liquidity": regime.get("liquidity_state"),
                "policy": regime.get("policy_state"),
                "risk": regime.get("risk_state"),
                "curve": regime.get("yield_curve_state"),
                "one_liner": r_summary.get("one_liner", "N/A")
            },
            "os_summary": os_summary,
            "priority_topics": priority_topics[:5], # Keep top 5
            "notes": {
                "data_gaps": [],
                "integrity": {
                    "no_scoring_leak": True,
                    "no_behavior_change": True
                }
            }
        }

        # Save JSON
        json_path = self.base_dir / "data_outputs/ops/investment_os_state.json"
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(os_state, indent=2, ensure_ascii=False), encoding='utf-8')

        # Generate MD Brief
        self._generate_brief(os_state)

        self.logger.info(f"Successfully generated Investment OS assets (Topics: {len(priority_topics)}).")

    def _generate_brief(self, state: Dict):
        r = state["regime"]
        s = state["os_summary"]
        p = state["priority_topics"]

        lines = [
            f"# Investment OS Operational Brief ({state['date_kst']})\n",
            f"## 🌍 Market Regime",
            f"> **{r['one_liner']}**\n",
            f"- **Stance**: `{s['stance']}`",
            f"- **Focus**: {', '.join(s['focus'])}\n",
            f"## 🚫 Do Not Do",
            "\n".join([f"- {item}" for item in s['do_not_do']]),
            "\n## 🎯 Priority Topics (Top 3)\n"
        ]

        for topic in p[:3]:
            lines.append(f"### [{topic['os_classification']}] {topic['title']}")
            lines.append(f"- **Reasoning**: {' / '.join(topic['reasoning'])}")
            lines.append("- **Checklist**:")
            for item in topic['action_card']['checklist']:
                lines.append(f"  - [ ] {item}")
            
            if topic['linked_stocks']:
                lines.append("\n| Ticker | Name | Exposure | Risk Note |")
                lines.append("|---|---|---|---|")
                for st in topic['linked_stocks']:
                    lines.append(f"| {st['ticker']} | {st['name']} | {st['exposure_type']} | {st['risk_note']} |")
            lines.append("\n---\n")

        md_path = self.base_dir / "data_outputs/ops/investment_os_brief.md"
        md_path.write_text("\n".join(lines), encoding='utf-8')

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    InvestmentOSLayer(Path(".")).run()
