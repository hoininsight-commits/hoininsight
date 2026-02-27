import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class RiskTimelineNarrator:
    """
    IS-98-6: Risk Timeline Narrator
    Generates "Economic Hunter" style scripts based on Schedule Risk Calendar data.
    """

    PHASE_1_DAYS = 30
    PHASE_2_DAYS = 90
    PHASE_3_DAYS = 180

    def __init__(self, base_dir: Path = Path(".")):
        self.base_dir = base_dir
        self.ui_dir = self.base_dir / "data" / "ui"
        self.exports_dir = self.base_dir / "exports"
        self.exports_dir.mkdir(parents=True, exist_ok=True)

    def load_json(self, name: str) -> Any:
        f = self.ui_dir / name
        if f.exists():
            try:
                return json.loads(f.read_text(encoding='utf-8'))
            except:
                return {}
        return {}

    def generate_scripts(self):
        top_n = self.load_json("upcoming_risk_topN.json")
        calendar_90 = self.load_json("schedule_risk_calendar_90d.json")
        calendar_180 = self.load_json("schedule_risk_calendar_180d.json")
        
        items = top_n.get("items", [])
        as_of = top_n.get("as_of", datetime.now().strftime("%Y-%m-%d"))
        today = datetime.strptime(as_of, "%Y-%m-%d")

        if not items:
            print("[NARRATOR] No upcoming risks found.")
            return

        # 1. Main Script (Long)
        long_script = self._build_long_script(items, as_of, today)
        (self.exports_dir / "risk_timeline_script_long.txt").write_text(long_script, encoding='utf-8')

        # 2. Shorts Script
        shorts_script = self._build_shorts_script(items)
        (self.exports_dir / "risk_timeline_script_shorts.txt").write_text(shorts_script, encoding='utf-8')

        # 3. Structural Data
        narrative_data = {
            "as_of": as_of,
            "opening": "지금 시장이 무서운 이유는 악재가 있어서가 아니라, 이미 날짜가 정해진 구조적 이벤트들이 줄을 서서 기다리고 있기 때문입니다.",
            "phases": self._build_narrative_data(items, today),
            "ending": "중요한 건 방향이 아니라 그날 시장이 어떤 반응을 보이는지입니다."
        }
        (self.ui_dir / "risk_timeline_narrative.json").write_text(json.dumps(narrative_data, indent=2, ensure_ascii=False), encoding='utf-8')

        print(f"[NARRATOR] Generated scripts in {self.exports_dir}")

    def _build_long_script(self, items: List[Dict], as_of: str, today: datetime) -> str:
        # Phase 1: Near-term (<30d)
        p1_items = [i for i in items if (datetime.strptime(i["date"], "%Y-%m-%d") - today).days <= self.PHASE_1_DAYS]
        # Phase 2: Mid-term (31-90d)
        p2_items = [i for i in items if self.PHASE_1_DAYS < (datetime.strptime(i["date"], "%Y-%m-%d") - today).days <= self.PHASE_2_DAYS]
        # Phase 3: Long-term (>90d)
        p3_items = [i for i in items if (datetime.strptime(i["date"], "%Y-%m-%d") - today).days > self.PHASE_2_DAYS]

        lines = []
        lines.append("[오프닝]")
        lines.append("지금 시장이 무서운 이유는 악재가 있어서가 아니라, 이미 날짜가 정해진 구조적 이벤트들이 줄을 서서 기다리고 있기 때문입니다.")
        lines.append("단순히 심리로 흔들리는 구간이 아닙니다. 구조가 작동하는 시간을 우리가 미리 알고 있다는 것이 핵심입니다.")
        lines.append("")

        lines.append("[PHASE 1: 단기 압박 구간]")
        if p1_items:
            for item in p1_items[:2]:
                lines.append(f"가장 먼저 대응해야 할 리스크는 {item['date']}에 예정된 {item['title']}입니다.")
                lines.append(f"{item['one_liner']}")
            lines.append("이 구간에서 무너지는 건 지수가 아니라 먼저 수급이고, 그 다음이 심리입니다.")
        else:
            lines.append("당장 한 달 내에 예정된 파괴적 이벤트는 없습니다. 하지만 긴장을 늦출 단계는 아닙니다.")
        lines.append("")

        lines.append("[PHASE 2: 중기 중첩 리스크]")
        if p2_items:
            lines.append("각각 보면 별일 아닐 수 있습니다. 문제는 이 이벤트들이 같은 분기에 몰려 있다는 점입니다.")
            for item in p2_items:
                lines.append(f"- {item['date']}: {item['title']}")
            lines.append("하나만 오면 버틸 수 있지만, 악재가 중첩될 때 구조적 균열이 발생합니다.")
        else:
            lines.append("중기 구간에서는 비교적 안정적인 흐름이 예상되나, 자본의 이동 방향을 계속 추적해야 합니다.")
        lines.append("")

        lines.append("[PHASE 3: 장기 구조 전환]")
        if p3_items:
            lines.append("시장은 결과가 아니라 방향이 보이는 순간부터 움직이기 시작합니다.")
            for item in p3_items:
                lines.append(f"- {item['date']}: {item['title']} (장기 관점 리스크)")
        else:
            lines.append("현재 데이터상 180일 이상의 장기 리스크 확정분은 존재하지 않습니다.")
        lines.append("")

        lines.append("[리스크 인식의 전환]")
        lines.append("이건 공포 영상이 아닙니다. 준비된 사람과 준비 안 된 사람을 가르는 지도입니다.")
        lines.append("무작정 하락을 점치는 것이 아니라, 어떤 전제가 흔들릴 때 우리가 액션을 취해야 하는지를 정의하는 과정입니다.")
        lines.append("")

        lines.append("[가이드라인]")
        lines.append("중요한 건 방향이 아니라 그날 시장이 어떤 반응을 보이는지입니다.")
        lines.append("우리는 예측하지 않습니다. 엔진이 찍어주는 날짜에 시장의 정석적인 반응이 나오는지 확인하고 대응할 뿐입니다.")
        
        return "\n".join(lines)

    def _build_shorts_script(self, items: List[Dict]) -> str:
        shorts = []
        for item in items:
            s = []
            s.append(f"제목: {item['date']} {item['title']} 리스크 긴급 점검")
            s.append(f"지금부터 {item['title']}를 주목해야 하는 이유는 명확합니다.")
            s.append(f"{item['one_liner']}")
            s.append(f"이 이벤트의 파괴적 점수는 10점 만점에 {round(item.get('final_score', 0)*10, 1)}점 수준입니다.")
            s.append("준비되지 않은 투자자에게는 위기지만, 구조를 아는 이들에게는 기회입니다.")
            shorts.append("\n".join(s))
        return "\n\n---\n\n".join(shorts)

    def _build_narrative_data(self, items: List[Dict], today: datetime) -> List[Dict]:
        phases = []
        # Simplified phase data for JSON
        for item in items:
            diff = (datetime.strptime(item["date"], "%Y-%m-%d") - today).days
            phase = 3
            if diff <= self.PHASE_1_DAYS: phase = 1
            elif diff <= self.PHASE_2_DAYS: phase = 2
            
            phases.append({
                "phase": phase,
                "date": item["date"],
                "title": item["title"],
                "risk_score": item.get("final_score", 0)
            })
        return phases

    def run(self):
        self.generate_scripts()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default=".", help="Base directory")
    args = parser.parse_args()
    
    gen = RiskTimelineNarrator(Path(args.base))
    gen.run()
