import json
import csv
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional

class DailyRunOrchestrator:
    """
    IS-99-1: Daily Run Orchestrator & Artifact Exporter
    Transforms multipack JSON into operational MD, JSON, and CSV files.
    """

    def __init__(self, input_dir: str = "data/decision", export_dir: str = "exports"):
        self.input_dir = Path(input_dir)
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def run(self) -> Dict[str, Any]:
        multipack_path = self.input_dir / "content_pack_multipack.json"
        if not multipack_path.exists():
            raise FileNotFoundError(f"Multipack source not found: {multipack_path}")

        multipack = json.loads(multipack_path.read_text(encoding="utf-8"))
        today = multipack.get("date", datetime.now().strftime("%Y-%m-%d"))

        # 1. Export JSON (Machine-readable)
        self._export_json(multipack)

        # 2. Export MD (Human-readable)
        self._export_markdown(multipack, today)

        # 3. Export CSV (Summary Table)
        self._export_csv(multipack)

        return multipack

    def _export_json(self, multipack: Dict):
        output_path = self.export_dir / "daily_upload_pack.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(multipack, f, ensure_ascii=False, indent=2)
        print(f"[OK] Exported JSON: {output_path}")

    def _export_markdown(self, multipack: Dict, date: str):
        output_path = self.export_dir / "daily_upload_pack.md"
        
        lines = [f"# 📅 DAILY CONTENT PACK — {date}\n"]
        
        long_items = [p for p in multipack["packs"] if p["format"] == "LONG"]
        short_items = [p for p in multipack["packs"] if p["format"] == "SHORT"]

        # Long Form
        lines.append("## 🎬 LONG FORM (1)")
        if long_items:
            p = long_items[0]
            a = p["assets"]
            lines.append(f"- Title: {a.get('title', 'N/A')}")
            lines.append(f"- Hook: {a['long_script']['sections'][0]['text']}")
            lines.append(f"- Core Claim: {a.get('one_liner', 'N/A')}")
            
            # Evidence
            lines.append("- Evidence:")
            for s in a["long_script"]["sections"]:
                if s["name"] == "EVIDENCE":
                    lines.append(f"  {s['text']}")
            
            # Mentionables
            m_list = [f"{m['name']} ({m['why_must']})" for m in a.get("mentionables", [])]
            lines.append(f"- Mentionables: {', '.join(m_list) or 'None'}")
            
            # Risks
            lines.append(f"- Risk / Checkpoint: {a['decision_card'].get('risks', ['None'])[0]}")
            
            # Citations
            c_list = [c["evidence_tag"] for c in a.get("evidence_sources", []) if c["status"] == "VERIFIED"]
            lines.append(f"- Citation Summary: {', '.join(c_list) or 'None'}")
        else:
            lines.append("  (No Long Content Ready)")

        lines.append("\n---\n")

        # Shorts
        lines.append("## 🎞 SHORTS (4)")
        for i, s_item in enumerate(short_items):
            a = s_item["assets"]
            lines.append(f"### SHORT #{i+1}")
            lines.append(f"- Hook: {a['shorts_script'].get('hook', 'N/A')}")
            lines.append(f"- One-Line Claim: {a.get('one_liner', 'N/A')}")
            lines.append(f"- Evidence Anchor: {a['shorts_script'].get('evidence_3', ['N/A'])[0]}")
            lines.append("- CTA: 오늘 브리핑이 유익했다면 구독과 알림 설정 부탁드립니다.\n")

        lines.append("\n---\n")

        # Operational Notes
        lines.append("## 📌 운영 메모")
        lines.append(f"- Speakability Summary: {multipack['summary'].get('ready_count', 0)} READY")
        lines.append(f"- Fallback Promotion: {multipack['summary'].get('hold_included', 0)} HOLD units promoted")
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"[OK] Exported Markdown: {output_path}")

    def _export_csv(self, multipack: Dict):
        output_path = self.export_dir / "daily_upload_pack.csv"
        headers = ["type", "title", "primary_asset", "confidence", "speakability"]
        
        with open(output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for p in multipack["packs"]:
                writer.writerow([
                    p["format"],
                    p["assets"].get("title", "N/A"),
                    p["topic_id"],
                    "HIGH" if p["status"]["speakability"] == "READY" else "MEDIUM",
                    p["status"]["speakability"]
                ])
        print(f"[OK] Exported CSV: {output_path}")

def run_orchestrator(input_dir: str = "data/decision"):
    orch = DailyRunOrchestrator(input_dir=input_dir)
    return orch.run()

if __name__ == "__main__":
    run_orchestrator()
