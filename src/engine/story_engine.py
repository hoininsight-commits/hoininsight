import os
import json
from datetime import datetime
from pathlib import Path

class MarketStoryEngine:
    """
    Engine for synthesizing market state, contradictions, and themes into a "Today's Story".
    Follows Economic Hunter style content structure.
    """
    
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.data_ops_dir = self.project_root / "data" / "ops"
        self.data_contra_dir = self.project_root / "data" / "contradictions"
        self.output_dir = self.project_root / "data" / "story"
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def _load_json(self, path):
        if not path.exists():
            return None
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None

    def run_all(self):
        print("[MarketStoryEngine] Starting Story Synthesis...")
        
        # 1. Load context
        benchmark = self._load_json(self.data_ops_dir / "market_prediction_benchmark.json") or {}
        contradictions = self._load_json(self.data_contra_dir / "contradiction_state.json") or {}
        topic_view = self._load_json(self.data_ops_dir / "topic_view_today.json") or {}
        capital_flow = self._load_json(self.data_ops_dir / "capital_flow_impact.json") or {}
        
        # 2. Extract key elements
        market_state = benchmark.get("benchmark_summary", {}).get("market_state", "Neutral")
        top_contra = self._get_top_contradiction(contradictions)
        
        # [STEP-52] Check for Locked Theme
        locked_path = self.project_root / "data" / "operator" / "locked_brief.json"
        locked_theme = None
        if locked_path.exists():
            try:
                with open(locked_path, "r", encoding="utf-8") as f:
                    locked_data = json.load(f)
                    if locked_data.get("consistency") == "LOCKED":
                        locked_theme = locked_data.get("core_theme")
                        print(f"[MarketStoryEngine] 🔒 Using Locked Theme: {locked_theme}")
            except Exception:
                pass
        
        featured_theme = self._get_featured_theme(topic_view)
        if locked_theme:
            # Force override theme name
            if featured_theme:
                featured_theme["title"] = locked_theme
            else:
                featured_theme = {"title": locked_theme}
        
        # 3. Generate Narrative
        story = self._generate_narrative(market_state, top_contra, featured_theme, capital_flow)
        
        # 4. Save results
        output_path = self.output_dir / "today_story.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(story, f, indent=2, ensure_ascii=False)
            
        print(f"[MarketStoryEngine] Story generated: {story['title']}. Saved to {output_path}")
        return story

    def _get_top_contradiction(self, contradictions):
        list_c = contradictions.get("contradictions", [])
        if not list_c:
            return None
        # Return the one with highest strength
        return max(list_c, key=lambda x: x.get("strength", 0))

    def _get_featured_theme(self, topic_view):
        # Prefer structural topics
        topics = topic_view.get("topics", [])
        for t in topics:
            if t.get("topic_type") == "ISSUE_SIGNAL":
                return t
        return topics[0] if topics else None

    def _generate_narrative(self, market_state, top_contra, featured_theme, capital_flow):
        title = "Daily Market Convergence"
        summary = "Markets are currently navigating standardized flows with no major structural disruptions."
        theme_name = "Market Equilibrium"
        sectors = ["Broad Market"]
        
        if top_contra:
            title = f"Structural Tension: {top_contra.get('name')}"
            summary = f"Current market is characterized by {market_state}. {top_contra.get('reason')}"
            sectors = top_contra.get("affected_sectors", sectors)
            
        if featured_theme:
            theme_name = featured_theme.get("title", "Emerging Market Focus")
            if not summary or len(summary) < 50:
                summary = featured_theme.get("one_line_summary", summary)
            
        # Refine summary based on flow
        flow_theme = capital_flow.get("top_capital_flow_theme", {})
        if flow_theme:
            impact_desc = f" Capital flow prioritizes {flow_theme.get('theme')} with {flow_theme.get('impact_direction')} impact."
            summary += impact_desc
            if flow_theme.get("primary_sector") not in sectors:
                sectors.append(flow_theme.get("primary_sector"))

        return {
            "title": title,
            "summary": summary,
            "featured_theme": theme_name,
            "impact_sectors": sectors,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

if __name__ == "__main__":
    import sys
    root = Path(__file__).parent.parent.parent
    engine = MarketStoryEngine(root)
    engine.run_all()
