import json
from typing import Dict, Any, List, Optional

class ContentPackageComposer:
    """
    IS-35: CONTENT_PACKAGE_COMPOSER
    Transforms approved IssueSignal decisions into publish-ready content.
    """

    def compose(self, data: Dict[str, Any], defense_text: Optional[str] = None) -> Optional[Dict[str, Any]]:
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
            package["content"] = self._compose_long_form(data, defense_text)
        elif "숏츠" in output_form or "SHORT" in str(output_form).upper():
            package["content"] = self._compose_short_form(data, defense_text)
        elif "텍스트" in output_form or "TEXT" in str(output_form).upper():
            package["content"] = self._compose_text_card(data, defense_text)
        else:
            return None

        return package

    def _compose_long_form(self, data: Dict[str, Any], defense_text: Optional[str] = None) -> str:
        """5-step Mandated Voice Structure for IS-39."""
        trigger = data.get("trigger_sentence", "트리거 신호 없음")
        flow = data.get("capital_flow_summary", "자본의 이동이 시작됐다.")
        tickers = data.get("bottleneck_tickers", [])
        proof = data.get("proof_pack", {})

        blocks = []
        # 1. 정의 (Definition)
        blocks.append("## 1. 정의\n지금 시장에서 발생하는 현상은 단순한 변동이 아니다. 이는 자본의 구조적 강제에 의한 필연적 결과다. 우리는 이 신호의 본질을 '정의'해야 한다.")
        
        # 2. 표면 해석 (Surface Interpretation)
        blocks.append("## 2. 표면 해석\n언론은 이를 수급의 이슈나 단기적인 심리 변화로 읽는다. 하지만 이는 표면에 나타난 그림자일 뿐이다. 실제 데이터는 다른 이야기를 하고 있다.")
        
        # 3. 시장의 오해 (Market Misunderstanding)
        blocks.append("## 3. 시장의 오해\n대부분의 참여자는 이 현상이 곧 해소될 것이라 믿는다. 하지만 그들은 틀렸다. 근본적인 병목 현상을 간과하고 있다. 질문은 필요 없다. 데이터가 증명한다.")
        
        # 4. 구조적 강제 (Structural Coercion)
        blocks.append(f"## 4. 구조적 강제\n{trigger}\n이 사실이 자본을 움직이게 만든다. 자본은 탈출구가 없다. 특정 방향으로 이동하도록 이미 결정됐다.")
        
        # 5. 결론 (Conclusion)
        if defense_text:
            blocks.append(f"### ⚠️ 방어 기제\n{defense_text}")
            
        ticker_str = ", ".join(tickers) if tickers else "핵심 병목 지점"
        blocks.append(f"## 5. 결론\n{flow}\n결론은 명확하다. 자본은 {ticker_str}(으)로 집중된다. 이 흐름을 거스르는 선택지는 없다. 분석은 완료됐다.")

        return "\n\n".join(blocks)

    def _compose_short_form(self, data: Dict[str, Any], defense_text: Optional[str] = None) -> Dict[str, str]:
        """3 variants of Short Form content with voice lock."""
        trigger = data.get("trigger_sentence", "")
        
        variants = {}
        
        # 15s
        variants["15초"] = f"정의한다. {trigger} 현상은 필연적마다. 자본은 이 길목으로 이동해야만 한다. 선택지는 없다."
        
        # 30s
        variants["30초"] = f"표면 해석은 무의미하다. {trigger} 사실이 모든 것을 결정한다. 시장은 오해하고 있지만 자본은 이미 움직였다. 구조적 강제는 시작됐다."
        
        # 45s
        variants["45초"] = f"결론은 하나다. {trigger} 신호가 구조를 바꿨다. 자본은 특정 병목 지점으로 집중되어야 한다. 우리는 이 흐름을 읽고 결과를 받아들여야 한다. 분석은 끝났다."

        if defense_text:
            for k in variants:
                variants[k] = variants[k].strip() + f" {defense_text}"

        return variants

    def _compose_text_card(self, data: Dict[str, Any], defense_text: Optional[str] = None) -> str:
        """5-line Text Card in Voice-Locked tone."""
        trigger = data.get("trigger_sentence", "")
        
        lines = []
        lines.append(f"제목: [경제 헌터 확정] {trigger[:30]}")
        lines.append("")
        lines.append(f"1. 정의: 신규 트리거에 의한 구조적 변화 확정.")
        lines.append(f"2. 신호: {trigger}")
        lines.append("3. 시장의 오해: 일시적 현상으로 치부함.")
        lines.append("4. 강제: 자본의 필연적 이동 시작됨.")
        lines.append("5. 결론: 핵심 병목 티커 집중 관찰 필요.")
        
        if defense_text:
            lines.append("")
            lines.append(f"[방어] {defense_text}")
        
        return "\n".join(lines)
