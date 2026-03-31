import json
from pathlib import Path

class PolicyCapitalScriptExporter:
    """
    [IS-109-A] Policy → Capital Script Exporter
    운영자가 정책 자본 전환 내용을 롱/숏 폼으로 즉시 활용할 수 있도록 스크립트를 추출합니다.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.ui_dir = base_dir / "data" / "ui"
        self.export_dir = base_dir / "exports"
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def run(self):
        data_path = self.ui_dir / "policy_capital_transmission.json"
        if not data_path.exists():
            print("[SCRIPT] policy_capital_transmission.json 데이터가 없어 스크립트 생성을 중단합니다.")
            return

        data = json.loads(data_path.read_text(encoding='utf-8'))

        # 1. Long Form Script
        long_script = self._generate_long(data)
        (self.export_dir / "policy_capital_long.txt").write_text(long_script, encoding='utf-8')

        # 2. Shorts Script
        shorts_script = self._generate_shorts(data)
        (self.export_dir / "policy_capital_shorts.txt").write_text(shorts_script, encoding='utf-8')

        print(f"[SCRIPT] Exported policy capital scripts to {self.export_dir}")

    def _generate_long(self, d: dict) -> str:
        who = d.get("who_gets_paid_first", {})
        pickaxe = " ".join(who.get("PICKAXE", []))
        bottleneck = " ".join(who.get("BOTTLENECK", []))
        
        script = f"""# [Policy→Capital] 롱폼 리포트 대본

[오프닝]
{d['headline']} - 단순한 정책 발표가 아니라, 실질적인 자본 파이프라인이 열리는 지점을 포착했습니다.

[메커니즘]
{chr(10).join([f"- {m}" for m in d['mechanism']])}

[수치 근거]
{chr(10).join([f"- {n}" for n in d['numbers_with_evidence']])}

[누가 먼저 돈을 받는가?]
- 가장 먼저 움직이는 곳(PICKAXE): {pickaxe if pickaxe else '데이터 확인 중'}
- 병목이 해결되는 곳(BOTTLENECK): {bottleneck if bottleneck else '데이터 확인 중'}

[자본 성격 및 시점]
이 자금은 {d['money_nature']} 성격을 가지며, 집행 시점은 {d['time_to_money']}로 예상됩니다. { '바닥 가격(Price Floor)이 형성된 상태입니다.' if d['price_floor'] else '' }

[리스크]
{d['risk_note']}
"""
        return script

    def _generate_shorts(self, d: dict) -> str:
        script = f"""# [Policy→Capital] 쇼츠/핵심 요약

(훅) {d['one_liner']}
(지표) {d['numbers_with_evidence'][0] if d['numbers_with_evidence'] else '근거 데이터 확인 완료'}
(결론) 정책이 돈으로 바뀌는 {d['time_to_money']} 시그널, {d['signal_type']} 구조를 주목하세요.
"""
        return script

if __name__ == "__main__":
    exporter = PolicyCapitalScriptExporter(Path("."))
    exporter.run()
