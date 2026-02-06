import json
from pathlib import Path

class SectorRotationExporter:
    """
    [IS-111] Sector Rotation Script Exporter
    가속 판정 결과를 기반으로 경사 스타일의 롱/숏 폼 대본을 생성합니다.
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
        accel = data.get("acceleration", "NONE")
        to_sector = data.get("to_sector", "핵심 섹터")
        op_sentence = data.get("operator_sentence", "")

        # 1. Long Form Script
        long_script = [
            f"### [경사 롱폼] {to_sector} 자금 가속 신호 분석",
            "",
            f"운영자 요약: {op_sentence}",
            "",
            "1. 왜 지금 이쪽인가?",
        ]
        
        if accel == "ACCELERATING":
            long_script.append("- 지금은 단순한 순환매 수준이 아닙니다. 정책, 실적, 수급이 한 곳으로 모이며 '가속'이 붙었습니다.")
            long_script.append("- '아직 다 안 왔다'고 봅니다. 이제 막 구조적 전환이 숫자로 찍히기 시작했으니까요.")
        elif accel == "ROTATING":
            long_script.append("- 돈이 움직이기 시작했습니다. 하지만 아직 전력질주 단계는 아닙니다.")
            long_script.append("- 초입인지, 일회성인지는 이번 주말 수급 데이터를 더 확인해야 합니다.")
        else:
            long_script.append("- 시장 전체적으로 눈치보기가 심합니다. 특정 섹터로의 쏠림은 아직 미미합니다.")

        long_script.append("\n2. 체크 포인트")
        for ev in data.get("evidence", []):
            long_script.append(f"- {ev}")

        # 2. Shorts Form Script
        shorts_script = [
            f"### [경사 쇼츠] 돈의 속도가 변하고 있다: {to_sector}",
            "",
            "\"지금 들어가도 되나요?\"",
        ]
        
        if accel == "ACCELERATING":
            shorts_script.append("정답은 'YES'입니다. 단순 유입이 아니라 '가속' 구간입니다.")
            shorts_script.append("이미 늦었다고 생각할 때가 가장 빠를 수 있는, 수급 정체 구간을 뚫어낸 상태입니다.")
        elif accel == "ROTATING":
            shorts_script.append("돈이 돌고는 있는데, 아직은 조심스럽습니다.")
            shorts_script.append("발만 담가두고 가속 페달을 밟는지 지켜봐야 할 때입니다.")
        else:
            shorts_script.append("아직은 아닙니다. 현금을 쥐고 다음 가속 신호를 기다리세요.")

        # Save
        (self.export_dir / "sector_rotation_long.txt").write_text("\n".join(long_script), encoding='utf-8')
        (self.export_dir / "sector_rotation_shorts.txt").write_text("\n".join(shorts_script), encoding='utf-8')
        print(f"[ROTATION_EXPORT] Exported scripts to {self.export_dir}")

if __name__ == "__main__":
    exporter = SectorRotationExporter(Path("."))
    exporter.run()
