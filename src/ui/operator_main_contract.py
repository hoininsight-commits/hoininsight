import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class OperatorMainContractBuilder:
    """
    IS-103: Operator-First Main UI Contract Builder
    Transforms engine outputs into a human-readable, deterministic JSON.
    """

    TECHNICAL_MAP = {
        "Rigidity": "가격 하락 저항성",
        "Dependency": "공급망 의존도",
        "Bottleneck": "핵심 병목 지점",
        "FLOW_CONFLUENCE": "자금 유입 집중",
        "STRUCTURAL_ROUTE": "구조적 고착화",
        "RATES": "금리 영향력",
        "LIQUIDITY": "유동성 수준",
        "VALUATION": "밸류업 여력",
        "EARNINGS": "실적 가시성",
        "RISK_OFF": "안전 자산 선호",
        "TECH_INFRA_KOREA": "한국 테크 인프라"
    }

    def __init__(self, base_dir: Path = Path(".")):
        self.base_dir = base_dir
        self.decision_dir = self.base_dir / "data" / "decision"
        self.ui_dir = self.base_dir / "data" / "ui"
        self.ui_dir.mkdir(parents=True, exist_ok=True)

    def load_json(self, dir_path: Path, name: str) -> Any:
        f = dir_path / name
        if f.exists():
            try:
                return json.loads(f.read_text(encoding='utf-8'))
            except:
                return {}
        return {}

    def run(self):
        # 1. Load Inputs
        hero_summary = self.load_json(self.ui_dir, "hero_summary.json")
        hook = self.load_json(self.ui_dir, "narrative_entry_hook.json")
        units = self.load_json(self.decision_dir, "interpretation_units.json")
        citations = self.load_json(self.decision_dir, "evidence_citations.json")
        mentionables = self.load_json(self.decision_dir, "mentionables.json")
        
        # Handle units potentially being list or dict
        if isinstance(units, list) and units:
            top_unit = units[0]
        elif isinstance(units, dict) and units:
            top_unit = list(units.values())[0] if units else {}
        else:
            top_unit = {}

        # Transform citations list to dict by tag
        citations_dict = {}
        if isinstance(citations, list) and citations:
            # We target the citations for the top unit's interpretation_id
            target_id = top_unit.get("interpretation_id")
            target_entry = next((item for item in citations if item.get("topic_id") == target_id), citations[0])
            for c in target_entry.get("citations", []):
                citations_dict[c.get("evidence_tag")] = c

        # 2. Build Hero
        hero = {
            "headline": hero_summary.get("headline") or f"{top_unit.get('target_sector', '전체')} 시장 구조 변화 감지",
            "one_liner": hero_summary.get("one_liner") or "단순 뉴스가 아니라 구조 변화입니다.",
            "status": hero_summary.get("status") or "HOLD",
            "why_now": hero_summary.get("why_now") or ["데이터 정합성 검토 중", "시장 반응 대기 중"],
            "risk_note": hero_summary.get("risk_note") or "확정되지 않은 테마 중심의 수급 변동성에 주의하십시오."
        }

        # 3. Build Three-Eye
        # PRICE / POLICY / CAPITAL / LABOR / AUTHORITY / SCHEDULE / EVENT
        eyes = ["PRICE", "POLICY", "CAPITAL", "LABOR", "AUTHORITY", "SCHEDULE", "EVENT", "EARNINGS"]
        three_eye = []
        tags = top_unit.get("evidence_tags", [])
        
        # Mapping for display labels
        LABEL_MAP = {
            "KR_POLICY": "정부 예산 집행율",
            "PRETEXT_VALIDATION": "내러티브 명분 점수",
            "EARNINGS_VERIFY": "기업 실적 부합도",
            "FLOW_CONFLUENCE": "자금 흐름 집중도",
            "STRUCTURAL_ROUTE_FIXATION": "구조적 경로 확정"
        }

        for eye in eyes:
            # Flexible matching: e.g. KR_POLICY matches POLICY
            matching_tags = [t for t in tags if eye in t.upper() or t.upper() in eye]
            ok = len(matching_tags) > 0
            
            # Find evidence in citations
            evidence = "구조적 근거 확인 중"
            if ok:
                for t in matching_tags:
                    if t in citations_dict:
                        cit = citations_dict[t]
                        # Handling new citation structure (status/sources) or old (value/unit)
                        val = cit.get('value', '')
                        unit = cit.get('unit', '')
                        status = cit.get('status', 'PENDING')
                        src = "다수 출처" if len(cit.get('sources', [])) > 1 else cit.get('sources', ['공식 데이터'])[0] if cit.get('sources') else '공식 데이터'
                        
                        label = LABEL_MAP.get(t, self.TECHNICAL_MAP.get(t, t))
                        if val:
                            evidence = f"{label}: {val}{unit} ({src})"
                        else:
                            evidence = f"{label}: ({status})"
                        break
            
            three_eye.append({
                "eye": eye,
                "ok": ok,
                "evidence": evidence
            })

        # 4. Build Numbers (Top 4)
        numbers = []
        for tag in tags[:4]:
            if tag in citations_dict:
                cit = citations_dict[tag]
                label = LABEL_MAP.get(tag, self.TECHNICAL_MAP.get(tag, tag))
                val = cit.get("value", "")
                unit = cit.get("unit", "")
                status = cit.get("status", "N/A")
                date = datetime.now().strftime("%Y-%m-%d") # Fallback date
                
                if val:
                    numbers.append(f"{label}: {val}{unit} (검증: {status})")
                else:
                    numbers.append(f"{label}: 자료 검증 중 (현황: {status})")
        
        if not numbers or numbers[0] == "핵심 지표 데이터 분석 완료 단계입니다.":
            # Fallback numbers from derived_metrics_snapshot
            metrics = top_unit.get("derived_metrics_snapshot", {})
            for k, v in metrics.items():
                label = LABEL_MAP.get(k, k.replace("_", " ").title())
                numbers.append(f"{label}: {v} (Derived Metric)")
            if len(numbers) > 4:
                numbers = numbers[:4]

        # 5. Mentionables by Role
        # Pickaxe: Top Mentionables, Bottleneck: First one with Bottleneck tag or first item
        m_list = mentionables if isinstance(mentionables, list) else []
        roles = {
            "BOTTLENECK": [],
            "PICKAXE": [],
            "HEDGE": []
        }
        
        for m in m_list:
            sentence = f"{m.get('topic', '주요 키워드')} 관련 신호 포착 ({m.get('source', 'Source')})"
            if m.get("role") == "BOTTLENECK":
                roles["BOTTLENECK"].append(sentence)
            elif m.get("role") == "HEDGE":
                roles["HEDGE"].append(sentence)
            else:
                roles["PICKAXE"].append(sentence)

        # Fallback if empty
        if not roles["PICKAXE"]:
            roles["PICKAXE"] = ["시장 주도 섹터 및 테마 분석 중", "관련 종목 및 자산 수급 확인 중", "주요 오피니언 리더 소셜 신호 대기 중"]
        if not roles["BOTTLENECK"]:
            roles["BOTTLENECK"] = ["현재 단계에서 탐지된 병목이나 즉각적인 진입 장애물은 없습니다."]

        # 6. Final Card
        card = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "hero": hero,
            "three_eye": three_eye,
            "numbers": numbers,
            "mentionables_by_role": roles
        }

        # 7. Save
        output_path = self.ui_dir / "operator_main_card.json"
        output_path.write_text(json.dumps(card, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"[CONTRACT] Generated {output_path}")

if __name__ == "__main__":
    builder = OperatorMainContractBuilder()
    builder.run()
