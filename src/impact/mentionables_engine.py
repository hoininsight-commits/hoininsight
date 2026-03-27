import os
import json
from pathlib import Path
from datetime import datetime

class MentionablesEngine:
    """
    Engine to detect affected sectors from Market Story and map them to specific stocks.
    Scores stocks based on Theme Relevance, Capital Flow, and Market Momentum.
    """
    
    # Simple Mapping for MVP
    SECTOR_STOCK_MAP = {
        "HBM Memory": ["SKHynix", "SamsungElectronics", "Micron"],
        "Advanced Packaging": ["TSMC", "ASE", "Amkor"],
        "Semiconductor Equipment": ["ASML", "AppliedMaterials", "LamResearch"],
        "Power Infrastructure": ["GeneralElectric", "Eaton", "SchneiderElectric"],
        "Data Center Construction": ["Equinix", "DigitalRealty", "Vertiv"],
        "AI Software": ["Microsoft", "NVIDIA", "Palantir"],
        "Nuclear Energy": ["ConstellationEnergy", "Cameco", "Vistra"],
        "EV Battery": ["LGEnergySolution", "SamsungSDI", "CATL"],
        "Memory Semiconductors": ["SKHynix", "SamsungElectronics", "Micron"],
        "Foundry": ["TSMC", "SamsungElectronics", "Intel"],
        "Technology": ["Microsoft", "NVIDIA", "Apple", "Google"],
        "Infrastructure": ["Caterpillar", "UnitedRentals", "QuantaServices"]
    }

    KEYWORD_SECTOR_MAP = {
        "HBM": "HBM Memory",
        "Packaging": "Advanced Packaging",
        "Semiconductor Equipment": "Semiconductor Equipment",
        "Power": "Power Infrastructure",
        "Data Center": "Data Center Construction",
        "AI": "AI Software",
        "Nuclear": "Nuclear Energy",
        "Battery": "EV Battery",
        "Foundry": "Foundry",
        "Chips": "Memory Semiconductors"
    }

    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.story_path = self.project_root / "data" / "story" / "today_story.json"
        self.benchmark_path = self.project_root / "data" / "ops" / "market_prediction_benchmark.json"
        self.flow_path = self.project_root / "data" / "ops" / "capital_flow_impact.json"
        self.output_path = self.project_root / "data" / "story" / "impact_mentionables.json"
        
        # Ensure output directory exists
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

    def _load_json(self, path):
        if not path.exists():
            return None
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None

    def run_analysis(self):
        print("[MentionablesEngine] Starting Analysis...")
        
        story = self._load_json(self.story_path)
        benchmark = self._load_json(self.benchmark_path)
        flow = self._load_json(self.flow_path)
        
        if not story:
            print("[MentionablesEngine] ❌ Error: Market Story not found.")
            return None

        # 1. Detect Sectors from Story
        detected_sectors = self._detect_sectors(story)
        
        # [STEP-52] Check for Locked Theme
        locked_path = self.project_root / "data" / "operator" / "locked_brief.json"
        locked_theme = None
        if locked_path.exists():
             with open(locked_path, "r", encoding="utf-8") as f:
                 locked_theme = json.load(f).get("core_theme")
                 print(f"[MentionablesEngine] 🔒 Using Locked Theme: {locked_theme}")
        
        # 2. Map Stocks & Score
        mentionable_stocks = []
        for sector in detected_sectors:
            stocks = self.SECTOR_STOCK_MAP.get(sector, [])
            for stock in stocks:
                score = self._calculate_score(stock, sector, story, benchmark, flow)
                mentionable_stocks.append({
                    "stock": stock,
                    "sector": sector,
                    "score": round(score, 1),
                    "reason": f"High relevance to {story.get('featured_theme', 'Theme')}"
                })

        # 3. Sort and Filter
        # Remove duplicates (keep highest score)
        unique_stocks = {}
        for item in mentionable_stocks:
            s_name = item["stock"]
            if s_name not in unique_stocks or item["score"] > unique_stocks[s_name]["score"]:
                unique_stocks[s_name] = item
        
        final_list = sorted(unique_stocks.values(), key=lambda x: x["score"], reverse=True)[:5]

        # 4. Save
        output = {
            "theme": story.get("featured_theme", "Market Focus"),
            "affected_sectors": detected_sectors,
            "mentionable_stocks": final_list,
            "metadata": {
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "engine_version": "1.0.0"
            }
        }
        
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
            
        print(f"[MentionablesEngine] Analysis complete. Saved to {self.output_path}")
        return output

    def _detect_sectors(self, story):
        sectors = set(story.get("impact_sectors", []))
        summary = story.get("summary", "").lower()
        title = story.get("title", "").lower()
        
        # Keyword based detection
        for kw, sector in self.KEYWORD_SECTOR_MAP.items():
            if kw.lower() in summary or kw.lower() in title:
                sectors.add(sector)
                
        return list(sectors)

    def _calculate_score(self, stock, sector, story, benchmark, flow):
        # score = 0.5 * theme_relevance + 0.3 * capital_flow + 0.2 * market_momentum
        
        # 1. Theme Relevance (Base 100)
        relevance = 100 if sector in story.get("impact_sectors", []) else 80
        
        # 2. Capital Flow (0-100)
        c_flow = 50 # Default neutral
        if flow:
            impact_direction = flow.get("top_capital_flow_theme", {}).get("impact_direction", "NEUTRAL")
            if impact_direction == "POSITIVE": c_flow = 90
            elif impact_direction == "NEGATIVE": c_flow = 20
        
        # 3. Momentum (0-100)
        momentum = 50 # Default
        if benchmark:
            risk_state = benchmark.get("risk_state", "Neutral")
            if risk_state == "ON": momentum = 90
            elif risk_state == "OFF": momentum = 20
            
        final_score = (0.5 * relevance) + (0.3 * c_flow) + (0.2 * momentum)
        return final_score

if __name__ == "__main__":
    root = Path(__file__).parent.parent.parent
    engine = MentionablesEngine(root)
    engine.run_analysis()
