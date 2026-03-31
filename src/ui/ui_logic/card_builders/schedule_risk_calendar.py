import json
import yaml
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any

class ScheduleRiskCalendar:
    """
    IS-102: Schedule Risk Calendar Layer
    Generates deterministic 90/180-day risk timelines for operators.
    """

    MARKET_SENSITIVITY = {
        "RATES": 0.2,
        "LIQUIDITY": 0.15,
        "VALUATION": 0.1,
        "EARNINGS": 0.1,
        "RISK_OFF": 0.15
    }

    def __init__(self, base_dir: Path = Path(".")):
        self.base_dir = base_dir
        self.registry_path = self.base_dir / "registry" / "schedules" / "schedule_registry_v1.yml"
        self.decision_dir = self.base_dir / "data" / "decision"
        self.ui_dir = self.base_dir / "data" / "ui"
        self.ui_dir.mkdir(parents=True, exist_ok=True)

    def load_yaml(self, path: Path) -> Dict[str, Any]:
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}

    def load_json(self, name: str) -> Any:
        f = self.decision_dir / name
        if f.exists():
            try:
                return json.loads(f.read_text(encoding='utf-8'))
            except:
                return {}
        return {}

    def calculate_score(self, item: Dict[str, Any], today: datetime, hero_theme: str) -> float:
        base_weight = item.get("base_weight", 0.0)
        try:
            item_date = datetime.strptime(item["date"], "%Y-%m-%d").date()
        except:
            return 0.0
            
        today_date = today.date()
        diff = (item_date - today_date).days
        
        if diff < 0: return 0.0 # Past event
        
        # Proximity Score
        proximity = 0.0
        if diff <= 60: proximity = 0.2
        elif diff <= 90: proximity = 0.1
        
        # Theme Boost
        theme_boost = 0.0
        if hero_theme:
            # Check if any tag matches hero_theme
            tags = item.get("tags", [])
            if hero_theme in tags or any(t.lower() in hero_theme.lower() for t in tags):
                theme_boost = 0.2
        
        # Market Sensitivity (picked from first affected axis)
        sensitivity = 0.0
        axes = item.get("affected_axes", [])
        if axes:
            sensitivity = self.MARKET_SENSITIVITY.get(axes[0], 0.1)
            
        final_score = base_weight + proximity + theme_boost + sensitivity
        
        # Estimate Cap
        if item.get("date_type") == "ESTIMATE":
            final_score = min(final_score, 0.6)
            
        return round(final_score, 2)

    def run(self, today_str: str = None):
        if today_str:
            today = datetime.strptime(today_str, "%Y-%m-%d")
        else:
            today = datetime.now()

        registry = self.load_yaml(self.registry_path)
        hero_summary = self.load_json("../ui/hero_summary.json") # From data/ui
        if not hero_summary:
            # Fallback to topic lock if ui/hero_summary not yet available
            hero_lock = self.load_json("hero_topic_lock.json")
            hero_theme = hero_lock.get("hero_topic", {}).get("theme", "")
        else:
            # Maybe extract theme from headline or summary
            hero_theme = hero_summary.get("headline", "")

        schedules = registry.get("schedules", [])
        
        results_90 = []
        results_180 = []
        
        today_date = today.date()
        
        for item in schedules:
            score = self.calculate_score(item, today, hero_theme)
            if score <= 0: continue
            
            item_date = datetime.strptime(item["date"], "%Y-%m-%d").date()
            diff = (item_date - today_date).days
            
            scored_item = item.copy()
            scored_item["final_score"] = score
            scored_item["theme_boost"] = 0.2 if score > item.get("base_weight", 0.0) + 0.1 else 0.0 # Approx
            
            if diff <= 90:
                results_90.append(scored_item)
            if diff <= 180:
                results_180.append(scored_item)

        # Generate 90d asset
        out_90 = {
            "as_of": today.strftime("%Y-%m-%d"),
            "window_days": 90,
            "items": sorted(results_90, key=lambda x: x["date"])
        }
        (self.ui_dir / "schedule_risk_calendar_90d.json").write_text(json.dumps(out_90, indent=2, ensure_ascii=False), encoding='utf-8')

        # Generate 180d asset
        out_180 = {
            "as_of": today.strftime("%Y-%m-%d"),
            "window_days": 180,
            "items": sorted(results_180, key=lambda x: x["date"])
        }
        (self.ui_dir / "schedule_risk_calendar_180d.json").write_text(json.dumps(out_180, indent=2, ensure_ascii=False), encoding='utf-8')

        # Generate Top N (7)
        top_7 = sorted(results_180, key=lambda x: x["final_score"], reverse=True)[:7]
        top_n_items = []
        for i, item in enumerate(top_7, 1):
            top_n_items.append({
                "rank": i,
                "date": item["date"],
                "title": item["title"],
                "one_liner": item["risk_mechanism"],
                "final_score": item["final_score"]
            })
            
        out_top_n = {
            "as_of": today.strftime("%Y-%m-%d"),
            "top_n": 7,
            "items": top_n_items
        }
        (self.ui_dir / "upcoming_risk_topN.json").write_text(json.dumps(out_top_n, indent=2, ensure_ascii=False), encoding='utf-8')
        
        print(f"[CALENDAR] Generated assets in {self.ui_dir}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default=".", help="Base directory")
    parser.add_argument("--date", help="Today's date YYYY-MM-DD")
    args = parser.parse_args()
    
    cal = ScheduleRiskCalendar(Path(args.base))
    cal.run(args.date)
