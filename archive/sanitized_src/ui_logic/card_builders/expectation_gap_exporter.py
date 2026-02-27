import json
from pathlib import Path

class ExpectationGapExporter:
    """
    [IS-110] Market Expectation vs Reality Gap Exporter
    시장 기대치와 현실의 괴리를 설명하는 한국어 대본을 추출합니다.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.ui_dir = base_dir / "data" / "ui"
        self.export_dir = base_dir / "exports"
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def run(self):
        data_path = self.ui_dir / "expectation_gap_card.json"
        if not data_path.exists():
            return

        data = json.loads(data_path.read_text(encoding='utf-8'))

        # 1. Long Form Script
        long_script = self._generate_long(data)
        (self.export_dir / "expectation_gap_long.txt").write_text(long_script, encoding='utf-8')

        # 2. Shorts Script
        shorts_script = self._generate_shorts(data)
        (self.export_dir / "expectation_gap_shorts.txt").write_text(shorts_script, encoding='utf-8')

        print(f"[GAP_SCRIPT] Exported scripts.")

    def _generate_long(self, d: dict) -> str:
        script = f"""# [경사의 눈] 시장 기대 vs 현실 괴리 분석

[오프닝]
"{d['headline']}" 
숫자는 좋은데 왜 주가는 빠질까? 오늘 우리는 시장의 기대 구조를 뚫어봅니다.

[1. 시장이 원했던 것]
{chr(10).join([f"- {e}" for e in d['expectation']])}

[2. 냉정한 현실 데이터]
{chr(10).join([f"- {r}" for r in d['reality']])}

[3. 괴리 발생 지점]
{d['one_liner']}
{chr(10).join([f"- {l}" for l in d['core_logic']])}

[4. 시장의 반응]
{chr(10).join([f"- {m}" for m in d['market_reaction']])}

[5. 대응 전략]
{chr(10).join([f"- {w}" for w in d['what_to_watch']])}

[리스크]
{d['risk_note']}
"""
        return script

    def _generate_shorts(self, d: dict) -> str:
        script = f"""# [경사 쇼츠] {d['gap_type']} 시그널

(훅) {d['one_liner']}
(기대) {d['expectation'][0]}
(현실) {d['reality'][0]}
(결론) {d['headline']}! 눈높이 조정 구간입니다.
"""
        return script

if __name__ == "__main__":
    exporter = ExpectationGapExporter(Path("."))
    exporter.run()
