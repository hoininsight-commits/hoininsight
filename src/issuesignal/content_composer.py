import json
from typing import Dict, Any, List, Optional

class ContentPackageComposer:
    """
    IS-35: CONTENT_PACKAGE_COMPOSER
    Transforms approved IssueSignal decisions into publish-ready content.
    """

    def compose(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Main entry point for composition.
        """
        output_form = data.get("output_form_ko") or data.get("output_form")
        
        if not output_form or "침묵" in str(output_form) or "SILENT" in str(output_form):
            return None

        package = {
            "type": output_form,
            "composed_at": data.get("current_time_str", ""),
            "trigger_sentence": data.get("trigger_sentence", "트리거 문장 없음")
        }

        if "대형 영상" in output_form or "LONG" in str(output_form).upper():
            package["content"] = self._compose_long_form(data)
        elif "숏츠" in output_form or "SHORT" in str(output_form).upper():
            package["content"] = self._compose_short_form(data)
        elif "텍스트" in output_form or "TEXT" in str(output_form).upper():
            package["content"] = self._compose_text_card(data)
        else:
            return None

        return package

    def _compose_long_form(self, data: Dict[str, Any]) -> str:
        """7-block Economic Hunter script."""
        trigger = data.get("trigger_sentence", "")
        flow = data.get("capital_flow_summary", "자본의 흐름이 포착되었습니다.")
        tickers = data.get("bottleneck_tickers", [])
        kill_switch = data.get("kill_switch", "데이터가 반전될 경우 무효화됩니다.")
        proof = data.get("proof_pack", {})

        blocks = []
        # 1. OPENING
        blocks.append("## 1. 오프닝\n질문은 받지 않습니다. 지금부터 발생하는 현상은 경제적 법칙에 의한 필연적 결과입니다. 우리는 시장의 소음이 아닌, 자본의 강제적 이동만을 추적해야 합니다.")
        
        # 2. SURFACE
        blocks.append("## 2. 표면\n뉴스는 지금 현상을 단순한 수급 문제나 일시적 변동으로 설명합니다. 하지만 이는 본질을 가리는 막에 불과합니다.")
        
        # 3. MISS
        blocks.append("## 3. 간과한 지점\n시장이 놓치고 있는 핵심은 따로 있습니다. 보도되지 않은 하드 에비던스가 가리키는 방향은 정반대입니다.")
        
        # 4. REAL TRIGGER
        blocks.append(f"## 4. 진짜 트리거\n{trigger}\n이 사실만이 유일하게 유의미한 신호입니다.")
        
        # 5. CAPITAL FLOW
        blocks.append(f"## 5. 자본의 이동\n{flow}\n이동은 이미 시작되었으며 되돌릴 수 없습니다.")
        
        # 6. TICKERS
        ticker_str = ", ".join(tickers) if tickers else "관련 핵심 기업"
        blocks.append(f"## 6. 병목 티커\n이 과정에서 병목 현상이 발생하는 지점은 {ticker_str}입니다. 이들은 구조적 필연성에 의해 수혜가 발생해야 합니다.")
        
        # 7. KILL SWITCH
        blocks.append(f"## 7. 킬 스위치\n{kill_switch}\n이 조건이 충족되지 않는다면 본 분석은 즉시 파기해야 합니다.")

        return "\n\n".join(blocks)

    def _compose_short_form(self, data: Dict[str, Any]) -> Dict[str, str]:
        """3 variants of Short Form content."""
        trigger = data.get("trigger_sentence", "")
        flow = data.get("capital_flow_summary", "")
        
        variants = {}
        
        # 15s
        variants["15초"] = f"{trigger} 사실에 집중해야 합니다. 자본은 반드시 그 방향으로 이동해야 합니다."
        
        # 30s
        variants["30초"] = f"{trigger} 현상이 포착되었습니다. 이는 단순한 우연이 아닌 구조적 필연입니다. 자본은 해당 섹터로 이동해야 하며, 우리는 그 길목을 지켜야 합니다."
        
        # 45s
        variants["45초"] = f"{trigger} 사실로 인해 시장의 판도가 바뀝니다. {flow} 자본의 대이동은 불가피합니다. 질문 없이 이 흐름에 몸을 맡겨야 합니다. 결론적으로 자본은 특정 병목 지점으로 이동해야만 합니다."

        return variants

    def _compose_text_card(self, data: Dict[str, Any]) -> str:
        """5-7 line Text Card."""
        trigger = data.get("trigger_sentence", "")
        kill_switch = data.get("kill_switch", "")
        
        lines = []
        lines.append(f"제목: [경제 헌터 신호] {trigger[:30]}...")
        lines.append("")
        lines.append(f"- 핵심 신호: {trigger}")
        lines.append("- 분석 상태: 신규 트리거 확정")
        lines.append("- 현재 상황: 자본의 강제적 이동 감지")
        lines.append("- 권고 사항: 핵심 병목 티커 관찰")
        lines.append(f"- 킬 스위치: {kill_switch}")
        
        return "\n".join(lines)
