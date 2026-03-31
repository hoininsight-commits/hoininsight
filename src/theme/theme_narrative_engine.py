import os
import json
from pathlib import Path
from datetime import datetime

class ThemeNarrativeEngine:
    """
    Engine to expand Early Themes into structured market narratives.
    Follows Economic Hunter style: Situation -> Structural Contradiction -> Sector Impact.
    """
    
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.early_theme_path = self.project_root / "data" / "theme" / "top_early_theme.json"
        self.signal_path = self.project_root / "data" / "ops" / "hoin_signal_today.json"
        self.benchmark_path = self.project_root / "data" / "ops" / "market_prediction_benchmark.json"
        
        self.output_dir = self.project_root / "data" / "theme"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Knowledge base for narrative expansion based on theme patterns
        self.narrative_templates = {
            "AI Power Constraint": {
                "explanation": "AI 경쟁이 가속화됨에 따라 데이터센터 수요가 폭증하고 있으며, 이는 필연적으로 막대한 전력 소모로 이어집니다.",
                "situation": "Big Tech 기업들의 AI Capex 투자가 사상 최고치를 경신 중이나, 전력망 확충 속도는 이를 따라가지 못하는 상황입니다.",
                "contradiction": "디지털 혁신의 속도(신속함)와 물리적 인프라의 건설 속도(저속함) 사이의 구조적 시차 발생.",
                "why_it_matters": "전력 부족은 단순한 비용 문제가 아니라 AI 산업 성장의 물리적 한계선(Hard Ceiling)으로 작용할 가능성이 큼."
            },
            "Defense Supply Chain Stress": {
                "explanation": "지정학적 긴장 고조로 인한 국방 예산 증액이 전 세계적인 현상으로 나타나고 있습니다.",
                "situation": "수요는 급증했으나 지난 수십 년간 효율화된 공급망은 갑작스러운 대량 생산 체제 전환에 어려움을 겪는 중입니다.",
                "contradiction": "냉전 이후 유지된 '효율 중심' 소량 생산 시스템과 '안보 중심' 대량 소모전 요구 사이의 충돌.",
                "why_it_matters": "방산 섹터의 리레이팅은 단순 테마가 아닌 국가 안보 수준의 구조적 재편 과정임."
            }
        }

    def _load_json(self, path):
        if not path.exists():
            return None
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None

    def run_narrative_expansion(self):
        print("[ThemeNarrativeEngine] Starting Narrative Expansion...")
        
        top_early = self._load_json(self.early_theme_path)
        if not top_early:
            print("[ThemeNarrativeEngine] ⚠️ No top early theme found. Skipping.")
            return None
            
        theme_name = top_early.get("theme", "Unknown")
        template = self.narrative_templates.get(theme_name, {
            "explanation": f"{theme_name}에 대한 초기 신호가 포착되었습니다.",
            "situation": "관련 데이터의 이상 변동이 관찰되고 있습니다.",
            "contradiction": "기존 시장 질서와 새로운 트렌드 사이의 잠재적 불일치가 예상됩니다.",
            "why_it_matters": "구조적 변화의 초기 단계로 모니터링이 필요합니다."
        })
        
        narrative = {
            "theme": theme_name,
            "stage": top_early.get("stage", "PRE-STORY"),
            "score": top_early.get("score", 0),
            "explanation": template["explanation"],
            "situation": template["situation"],
            "contradiction": template["contradiction"],
            "sector_impact": top_early.get("potential_sectors", []),
            "why_it_matters": template["why_it_matters"],
            "supporting_signals": top_early.get("signals", []),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Save output
        output_path = self.output_dir / "theme_narrative.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(narrative, f, indent=2, ensure_ascii=False)
            
        print(f"[ThemeNarrativeEngine] Narrative expanded for: {theme_name}")
        return narrative

if __name__ == "__main__":
    root = Path(__file__).parent.parent.parent
    engine = ThemeNarrativeEngine(root)
    engine.run_narrative_expansion()
