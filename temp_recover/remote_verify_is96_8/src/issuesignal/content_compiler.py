from pathlib import Path
from datetime import datetime
import yaml

class ContentCompiler:
    """
    (IS-9) Compiles IssueSignal output into Economic Hunter-style content.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.output_dir = base_dir / "data" / "issuesignal" / "final_packs"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def compile(self, signal_data: dict, evidence_data: dict) -> Path:
        """
        Generates EH-style multi-format content.
        """
        issue_id = signal_data.get("id", "IS-UNKNOWN")
        
        # 1. EH Style Narrative Construction
        narrative = self._build_eh_narrative(signal_data, evidence_data)
        
        # 2. Final Payload
        payload = {
            "header": {
                "issue_id": issue_id,
                "timestamp": datetime.now().isoformat(),
                "title": narrative["headline"]
            },
            "content": {
                "headline": narrative["headline"],
                "surface_view": narrative["surface_view"],
                "incompleteness": narrative["incompleteness"],
                "true_why_now": narrative["true_why_now"],
                "forced_flow": narrative["forced_flow"],
                "bottleneck_tickers": narrative["tickers"],
                "kill_switch": narrative["kill_switch"]
            },
            "scripts": {
                "long_form": self._generate_long_form(narrative),
                "shorts": self._generate_shorts(narrative)
            }
        }
        
        # 3. Save
        file_path = self.output_dir / f"{issue_id}_EH_CONTENT.yaml"
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(payload, f, allow_unicode=True, sort_keys=False)
            
        return file_path

    def _build_eh_narrative(self, signal: dict, evidence: dict) -> dict:
        """
        Strict 7-step EH structure builder.
        """
        return {
            "headline": f"[긴급] {signal.get('source')}의 발언이 암시하는 구조적 균열",
            "surface_view": "단순히 금리 인하 기대감이나 일시적인 시장 조정으로 보입니다.",
            "incompleteness": "하지만 이는 본질적인 공급망의 병목과 자본의 강제적 재편을 간과한 해석입니다.",
            "true_why_now": signal.get("why_now", "지금 당장 구조적 재편이 시작되었습니다."),
            "forced_flow": "이제 자본은 유동성 함정에서 벗어나 실물 기술 병목을 잡고 있는 곳으로 강제 이동합니다.",
            "tickers": signal.get("tickers", []),
            "kill_switch": "만약 상충하는 공식 정책이 24시간 이내에 발표될 경우 본 분석은 파기됩니다."
        }

    def _generate_long_form(self, narrative: dict) -> str:
        return f"{narrative['headline']}\n\n{narrative['surface_view']}\n{narrative['incompleteness']}\n\n{narrative['true_why_now']}\n{narrative['forced_flow']}\n\n병목 해결사: {', '.join([t['ticker'] for t in narrative['tickers']])}\n\n경보 해제 조건: {narrative['kill_switch']}"

    def _generate_shorts(self, narrative: dict) -> str:
        # ~30s compressed script
        return f"한 줄 요약: {narrative['true_why_now']}\n1. {narrative['surface_view']}? 아닙니다.\n2. 핵심은 {narrative['forced_flow']}.\n3. 그래서 {narrative['tickers'][0]['ticker'] if narrative['tickers'] else '대상의'} 움직임을 봐야 합니다.\n지금 바로 확인하세요."
