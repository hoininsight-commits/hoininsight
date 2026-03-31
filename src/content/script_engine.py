import os
import json
from pathlib import Path
from datetime import datetime

class TodayScriptEngine:
    """
    Engine to synthesize Today's Market Story and Mentionables into a video script.
    Follows "Economic Hunter" (경제사냥꾼) content architecture.
    """
    
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.story_path = self.project_root / "data" / "story" / "today_story.json"
        self.mentionables_path = self.project_root / "data" / "story" / "impact_mentionables.json"
        self.benchmark_path = self.project_root / "data" / "ops" / "market_prediction_benchmark.json"
        self.signal_path = self.project_root / "data" / "ops" / "hoin_signal_today.json"
        
        self.output_dir = self.project_root / "data" / "content"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def _load_json(self, path):
        if not path.exists():
            return None
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None

    def run_synthesis(self):
        print("[TodayScriptEngine] Starting Script Synthesis with Causality Alignment...")
        
        story = self._load_json(self.story_path)
        mentionables = self._load_json(self.mentionables_path)
        benchmark = self._load_json(self.benchmark_path)
        signal = self._load_json(self.signal_path)
        
        # [STEP-D] Load Causality Chain
        causal_path = self.project_root / "data" / "ops" / "decision_causality_chain.json"
        causality = self._load_json(causal_path)
        
        if not story:
            print("[TodayScriptEngine] ❌ Error: Required input 'today_story.json' not found.")
            return None
            
        # 1. Hook (Enhanced with Causality Trigger)
        if causality:
            hook = f"지금 '{story.get('title')}' 현상 뒤에 숨겨진 진짜 트리거를 아십니까? 바로 {causality['trigger']} 때문입니다."
        else:
            hook = f"오늘 우리가 주목해야 할 시장의 가장 강력한 균열, 주제는 바로 '{story.get('title', '시장 긴급 점검')}'입니다."
        
        # 2. Situation (Enhanced with Structural Context)
        if causality:
            situation = f"현재 시장의 구조적 배경은 이렇습니다: {causality['structural_context']}. 단순한 숫자의 변화가 아닌 판의 변화가 시작되었습니다."
        else:
            market_summary = benchmark.get("benchmark_summary", {}).get("market_state", "중립적") if benchmark else "안정적인 흐름"
            situation = f"현재 시장은 {market_summary} 상태에 있습니다. 표면적인 지표들은 조용해 보이지만, 그 기저에서는 심각한 변화의 전조가 감지되고 있습니다."
        
        # 3. Structural Contradiction (Enhanced with Mechanism)
        if causality:
            contradiction = f"핵심 메커니즘은 이겁니다: {causality['mechanism']}. 이 구조적 모순이 시장의 방향성을 결정짓고 있습니다."
        else:
            summary = story.get("summary", "")
            contradiction = f"핵심적인 모순은 이겁니다: {summary}"
        
        # 4. Sector Impact
        sectors = story.get("impact_sectors", [])
        sector_str = ", ".join(sectors)
        sector_impact = f"이 구조적 긴장이 가장 먼저 타격할, 혹은 기회를 줄 영역은 {sector_str}입니다."
        
        # 5. Mentionable Stocks
        stocks = mentionables.get("mentionable_stocks", []) if mentionables else []
        stock_bullets = "\n".join([f"- {s['stock']} (신뢰도: {s['score']}): {s['reason']}" for s in stocks])
        mentionable_section = f"우리가 추적해야 할 핵심 종목 리스트입니다:\n{stock_bullets}"
        
        # 6. Operator Action (Enhanced with Decision Link)
        action = self._determine_action(signal)
        if causality:
            operator_action = f"운영자의 최종 결정은 [{action}]입니다. 판단 근거: {causality['decision_link']}"
        else:
            action_desc = {
                "WATCH": "관망하며 다음 신호를 기다리십시오.",
                "TRACK": "비중을 조절하며 추세 추종을 시작하십시오.",
                "FOCUS": "강력한 베팅 구간입니다. 모멘텀에 집중하십시오."
            }.get(action, "신호를 예의주시하십시오.")
            operator_action = f"운영자의 최종 결정은 [{action}]입니다. {action_desc}"

        # Combine into Markdown
        md_script = f"""# Today Market Story Script (Causality Aligned)
        
---
## [Hook]
{hook}

## [Situation: Structural Background]
{situation}

## [Mechanism: Structural Contradiction]
{contradiction}

## [Sector Impact]
{sector_impact}

## [Mentionable Stocks]
{mentionable_section}

## [Final Operator Decision]
{operator_action}
"""

        # [STEP-52] Check for Locked Theme
        locked_path = self.project_root / "data" / "operator" / "locked_brief.json"
        locked_theme = None
        if locked_path.exists():
             with open(locked_path, "r", encoding="utf-8") as f:
                 locked_theme = json.load(f).get("core_theme")
        
        # JSON Object
        json_output = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "theme": locked_theme if locked_theme else story.get("featured_theme", "Market Update"),
            "causality_link": True,
            "hook": hook,
            "situation": situation,
            "contradiction": contradiction,
            "sectors": sectors,
            "stocks": stocks,
            "operator_action": action,
            "full_script": md_script,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Save files
        with open(self.output_dir / "today_video_script.md", "w", encoding="utf-8") as f:
            f.write(md_script)
        with open(self.output_dir / "today_video_script.json", "w", encoding="utf-8") as f:
            json.dump(json_output, f, indent=2, ensure_ascii=False)

        print(f"[TodayScriptEngine] Script generated successfuly in {self.output_dir}")
        return json_output

    def _determine_action(self, signal):
        # Intensity based check
        if not signal: return "WATCH"
        
        intensity = signal.get("strength", 0)
        if intensity > 80: return "FOCUS"
        if intensity > 50: return "TRACK"
        return "WATCH"

if __name__ == "__main__":
    root = Path(__file__).parent.parent.parent
    engine = TodayScriptEngine(root)
    engine.run_synthesis()
