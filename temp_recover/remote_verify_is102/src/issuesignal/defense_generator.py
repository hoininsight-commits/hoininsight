from typing import List, Dict, Any, Optional

class DefenseGenerator:
    """
    IS-42: DEFENSIVE_STATEMENT_GENERATOR
    Generates authoritative defense sentences and handles auto-insertion.
    """

    def generate_defense(self, risk_results: List[Dict[str, Any]]) -> Optional[str]:
        """Generates a combined defense string based on MEDIUM/HIGH risks."""
        high_risks = [r for r in risk_results if r["risk_level"] == "높음"]
        med_risks = [r for r in risk_results if r["risk_level"] == "중간"]

        if not high_risks and not med_risks:
            return None

        # Authoritative defense templates (IS-39 Voice Lock)
        defenses = []
        if high_risks:
            defenses.append("이 신호는 매수 지시가 아니다. 자본의 책임은 각자에게 있다.")
        
        if med_risks:
            defenses.append("분석 결과는 확정된 미래가 아닌 데이터의 방향성만을 보고한다.")

        if not defenses:
            return "이 모든 기록은 구조적 변화를 추적하는 내부 데이터다. 맹신은 금물이다."

        return " ".join(defenses[:2])

    def apply_to_content(self, pkg: Dict[str, Any], defense_text: str):
        """Logic to insert defense text at mandated positions."""
        if not defense_text:
            return

        # 1. Long Form (Insert before last block - conclusion)
        if "content" in pkg and isinstance(pkg["content"], str):
            content = pkg["content"]
            if "## 5. 결론" in content:
                pkg["content"] = content.replace("## 5. 결론", f"### ⚠️ 방어 기제\n{defense_text}\n\n## 5. 결론")
            else:
                pkg["content"] = content + f"\n\n### ⚠️ 방어 기제\n{defense_text}"

        # 2. Short Forms (Append to last line of each variant)
        if "content" in pkg and isinstance(pkg["content"], dict):
            for k, v in pkg["content"].items():
                pkg["content"][k] = v.strip() + f" {defense_text}"

        # 3. Text Card (Append to bottom)
        if "text_card" in pkg:
            pkg["text_card"] = pkg["text_card"].strip() + f"\n\n[방어] {defense_text}"
