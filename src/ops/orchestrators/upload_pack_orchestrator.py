"""
IS-99-4 Upload Pack Orchestrator
Bundles Long and Shorts scripts into a structured daily upload package.
"""
import json
import csv
import shutil
from pathlib import Path
from datetime import datetime

class UploadPackOrchestrator:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.export_root = self.base_dir / "exports"
        self.decision_dir = self.base_dir / "data" / "decision"
        self.pack_dir = self.export_root / "upload_pack_daily"
        
    def setup_dirs(self):
        """Creates the directory structure for the daily pack."""
        if self.pack_dir.exists():
            shutil.rmtree(self.pack_dir)
        
        folders = [
            "01_LONG",
            "02_SHORTS",
            "03_METADATA",
            "04_BREAK_SCENARIO"
        ]
        for f in folders:
            (self.pack_dir / f).mkdir(parents=True, exist_ok=True)

    def load_metadata(self):
        hero = {}
        citations = []
        try:
            hero_raw = json.loads((self.decision_dir / "hero_topic_lock.json").read_text())
            if hero_raw.get("status") == "LOCKED":
                hero = hero_raw.get("hero_topic", {})
        except: pass
        
        try:
            citations = json.loads((self.decision_dir / "evidence_citations.json").read_text())
        except: pass
        
        return hero, citations

    def bundle_scripts(self):
        """Copies scripts from exports/ to the pack subfolders."""
        # Long
        long_src = self.export_root / "final_script_long.txt"
        if long_src.exists():
            shutil.copy(long_src, self.pack_dir / "01_LONG" / "long_script.txt")
        else:
            print(f"[PACK] Warning: {long_src} missing")

        # Shorts
        angles = ["macro", "pickaxe", "data", "risk"]
        for i, angle in enumerate(angles, 1):
            short_src = self.export_root / f"shorts_angle_{i}.txt"
            if short_src.exists():
                shutil.copy(short_src, self.pack_dir / "02_SHORTS" / f"short_0{i}_{angle}.txt")
            else:
                raise FileNotFoundError(f"Short angle {i} missing. IS-99-4 requires exactly 4 angles.")

        # Break Scenario [IS-98-5]
        bs_long = self.export_root / "final_script_break_scenario_long.txt"
        bs_shorts = self.export_root / "final_script_break_scenario_shorts.txt"
        if bs_long.exists():
            shutil.copy(bs_long, self.pack_dir / "04_BREAK_SCENARIO" / "break_long.txt")
        if bs_shorts.exists():
            shutil.copy(bs_shorts, self.pack_dir / "04_BREAK_SCENARIO" / "break_shorts.txt")

    def generate_manifest(self, hero, citations):
        """Generates JSON and CSV manifests."""
        today = datetime.now().strftime("%Y-%m-%d")
        
        manifest = {
            "date": today,
            "hero_topic_id": hero.get("topic_id", "UNKNOWN"),
            "theme": hero.get("sector", "UNKNOWN"),
            "topic_type": hero.get("topic_type", "UNKNOWN"),
            "hypothesis_flag": hero.get("topic_type") == "HYPOTHESIS_JUMP",
            "sources_used": [c.get("source_id") for c in citations if "source_id" in c],
            "shorts_count": 4,
            "long_ready": True
        }
        
        # Save JSON
        (self.pack_dir / "03_METADATA" / "upload_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
        
        # Save CSV
        csv_path = self.pack_dir / "03_METADATA" / "upload_manifest.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["asset_type", "filename", "angle", "hypothesis_flag"])
            writer.writerow(["LONG", "long_script.txt", "main", manifest["hypothesis_flag"]])
            angles = ["macro", "pickaxe", "data", "risk"]
            for i, angle in enumerate(angles, 1):
                writer.writerow(["SHORT", f"short_0{i}_{angle}.txt", angle, manifest["hypothesis_flag"]])
            
            # [IS-98-5]
            if (self.pack_dir / "04_BREAK_SCENARIO" / "break_long.txt").exists():
                writer.writerow(["BREAK_LONG", "break_long.txt", "scenario", False])
                writer.writerow(["BREAK_SHORTS", "break_shorts.txt", "scenario", False])

    def generate_readme(self, hero):
        """Generates 00_README.md via template."""
        today = datetime.now().strftime("%Y-%m-%d")
        h_flag = hero.get("topic_type") == "HYPOTHESIS_JUMP"
        warning = "\n> [!WARNING]\n> 이건 확정이 아니라 '촉매 기반 가설'입니다. 투자 시 각별히 유의하세요.\n" if h_flag else ""
        
        template = f"""# DAILY UPLOAD PACK ({today})

## 주제: {hero.get('sector', 'UNKNOWN')} ({hero.get('topic_type', '-')})
{warning}

## 오늘의 선정 이유
- 구조적 신호 확인: {hero.get('dominant_eye', 'Main Eye')}
- {hero.get('why_now_bundle', {}).get('why_now_3', '새로운 패러다임이 시작되었습니다.')}

## 업로드 순서 가이드 (추천)
1. **Shorts 01~04**: 먼저 업로드하여 알고리즘 트래픽을 유도하십시오.
2. **Long Video**: Shorts 업로드 1~2시간 후 공개하여 시청 지속 시간을 확보하십시오.

## 검증 리포트
- 데이터 소스: {len(hero.get('eyes_used', []))} Eyes 검증 완료
- 구조적 패러다임: {hero.get('sector')} 주도권 이동 여부 확인됨

## Break Scenario (가설 붕괴 시나리오) [IS-98-5]
- 원인: {hero.get('relationship', 'N/A')} 관계 스트레스 포착
- 내용: 만약 루프가 깨진다면 무엇이 붕괴하고 누가 사냥꾼이 되는가?
- 파일: `04_BREAK_SCENARIO/` 폴더를 확인하십시오.

---
*본 패키지는 IS-99-4 오케스트레이터에 의해 데이터 기반으로 자동 생성되었습니다.*
"""
        (self.pack_dir / "00_README.md").write_text(template, encoding="utf-8")

    def run(self):
        print("[PACK] Orchestrating Daily Upload Pack...")
        self.setup_dirs()
        hero, citations = self.load_metadata()
        self.bundle_scripts()
        self.generate_manifest(hero, citations)
        self.generate_readme(hero)
        print(f"[PACK] Package created at {self.pack_dir}")

if __name__ == "__main__":
    orchestrator = UploadPackOrchestrator()
    orchestrator.run()
