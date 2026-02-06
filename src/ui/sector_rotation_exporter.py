import json
from pathlib import Path

class SectorRotationExporter:
    """
    [IS-111] Sector Rotation Acceleration Exporter
    섹터 간 자금 이동의 가속도를 설명하는 한국어 대본을 추출합니다.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.ui_dir = base_dir / "data" / "ui"
        self.export_dir = base_dir / "exports"
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def run(self):
        data_path = self.ui_dir / "sector_rotation_acceleration.json"
        if not data_path.exists():
            return

        data = json.loads(data_path.read_text(encoding='utf-8'))

        # 1. Long Form Script
        long_script = self._generate_long(data)
        (self.export_dir / "sector_rotation_long.txt").write_text(long_script, encoding='utf-8')

        # 2. Shorts Script
        shorts_script = self._generate_shorts(data)
        (self.export_dir / "sector_rotation_shorts.txt").write_text(shorts_script, encoding='utf-8')

        print(f"[ROTATION_SCRIPT] Exported sector rotation scripts.")

    def _generate_long(self, d: dict) -> str:
        accel_text = "이미 가속이 붙었습니다" if d['acceleration'] == "ACCELERATING" else "이동의 초입입니다"
        script = f"""# [경사의 눈] 섹터 간 자금 이동 가속도 분석

[오프닝]
"돈은 사라지지 않는다. 다만 이동할 뿐이다."
지금 시장에서 가장 뜨거운 돈이 어디서 빠져서 어디로 가고 있는지, 그리고 그 속도가 얼마나 붙었는지 뚫어봅니다.

[1. 자금의 출처 및 목적지]
- FROM: {d['from_sector']}
- TO: {d['to_sector']}
- 현재 상태: {d['acceleration']} ({accel_text})

[2. 가속 판정 근거]
{chr(10).join([f"- {e}" for e in d['evidence']])}

[3. 경사의 핵심 요약]
{d['operator_sentence']}
단순히 종목이 움직이는 게 아니라, 섹터 전체의 엔진이 교체되고 있는 구간입니다.

[4. 관전 포인트]
지금 이 흐름이 '어디까지' 갈 수 있을지, 우리는 내러티브의 완성도를 봐야 합니다.

[리스크 및 주의사항]
{d['risk_note']}
"""
        return script

    def _generate_shorts(self, d: dict) -> str:
        accel_sign = "🚀 가속 시작!" if d['acceleration'] == "ACCELERATING" else "🔄 순환매 포착"
        script = f"""# [경사 쇼츠] {accel_sign} : 자금 대이동

(훅) {d['operator_sentence']}
(흐름) {d['from_sector']} ➔ {d['to_sector']}
(근거) {d['evidence'][0]}
(결론) 지금은 종목이 아니라 '돈의 방향'에 올라타야 할 때입니다.
"""
        return script

if __name__ == "__main__":
    exporter = SectorRotationExporter(Path("."))
    exporter.run()
