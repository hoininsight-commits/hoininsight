import json
import os
from pathlib import Path
from datetime import datetime

class ConsistencyRepairEngine:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.brief_path = self.project_root / "data" / "ops" / "today_operator_brief.json"
        # Fallback to local data path if ops doesn't exist (e.g. during dev)
        if not self.brief_path.parent.exists():
            self.brief_path = self.project_root / "data" / "operator" / "today_operator_brief.json"
            
    def _load_json(self, rel_path):
        p = self.project_root / rel_path
        if not p.exists():
            return {}
        try:
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_json(self, rel_path, data):
        p = self.project_root / rel_path
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_structural_explanation(self, stock, core_theme):
        """Generates a theme-based structural explanation for a stock."""
        # Rule-based lookup for common pairings
        rules = {
            "AI Power Constraint": {
                "NVIDIA": "AI 연산 수요 증가 → GPU 수요 폭증 및 전력 효율 중요도 상승",
                "Microsoft": "AI 데이터센터 인프라 투자 확대 → 전력망 부하 증가의 직접적 원인",
                "Apple": "온디바이스 AI 전환 → 저전력 칩셋 및 기기 교체 주기 가속화",
                "Google": "자체 AI 가속기(TPU) 확장 → 데이터센터 전력 소비 효율화 압박",
                "Caterpillar": "데이터센터 및 그리드 인프라 확장 → 대형 발전기 및 건설 장비 수요 증가",
                "Amazon": "AWS 인프라 확장 → 재생 에너지 및 원자력 기반 안정적 전원 확보 추진",
                "Vertiv": "데이터센터 냉각 솔루션 → 전력 밀도 상승에 따른 필수 인프라",
                "NextEra Energy": "신재생 에너지 공급 → AI 전력 수요를 충당할 핵심 그리드 사업자"
            },
            "AI Evolution": {
                "NVIDIA": "알고리즘의 하드웨어 최적화 → 차세대 아키텍처 도입 속도 가속",
                "Microsoft": "Copilot 생태계 확산 → 소프트웨어 생산성 혁신의 상업화 단계 진입",
                "OpenAI": "차세대 LLM 모델링 → 범용 인공지능(AGI)을 향한 기술적 한계 돌파",
                "Tesla": "자율주행 FSD 고도화 → 물리 세계와의 상호작용을 통한 AI 진화"
            }
        }
        
        theme_rules = rules.get(core_theme, {})
        # If theme not found, try a generic mapping or fuzzy match
        if not theme_rules:
            # Simple fuzzy theme match
            for t in rules:
                if t in core_theme or core_theme in t:
                    theme_rules = rules[t]
                    break
        
        explanation = theme_rules.get(stock)
        
        # Fallback: Generic but theme-aligned explanation
        if not explanation:
            explanation = f"{core_theme} 테마와 긴밀히 연계된 핵심 밸류체인 수혜 분석 중"
            
        return explanation

    def run_repair(self):
        print("[RepairEngine] Starting Narrative Consistency Repair...")
        
        # 1. Load Core Theme (SSOT) - Priority to STEP-52 Locked Brief
        locked_path = self.project_root / "data" / "operator" / "locked_brief.json"
        core_theme = None
        
        if locked_path.exists():
            try:
                with open(locked_path, "r", encoding="utf-8") as f:
                    locked_data = json.load(f)
                    if locked_data.get("consistency") == "LOCKED":
                        core_theme = locked_data.get("core_theme")
                        print(f"[RepairEngine] 🔒 Using Locked Theme from STEP-52: {core_theme}")
            except Exception:
                pass
                
        if not core_theme:
            core_state = self._load_json("data/operator/core_theme_state.json")
            core_theme = core_state.get("core_theme", "AI Power Constraint")
        
        # 2. Load Current Brief
        if not self.brief_path.exists():
            print(f"[RepairEngine] ❌ Brief not found at {self.brief_path}. Creating a dummy one.")
            brief = {"metadata": {"generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}}
        else:
            with open(self.brief_path, "r", encoding="utf-8") as f:
                brief = json.load(f)

        # 3. Apply Repair Logic
        
        # A. Title Alignment
        display_title = brief.get("display_title", core_theme)
        # If title doesn't contain theme keywords, force override
        if not any(kw.lower() in display_title.lower() for kw in core_theme.split()):
             display_title = f"{core_theme}: Market Equilibrium Shift"
        
        # B. Narrative Alignment
        narrative = brief.get("narrative_brief", {})
        if narrative.get("featured_theme") != core_theme:
            narrative["featured_theme"] = core_theme
            narrative["title"] = display_title
            
        # C. Impact Map Fix (Placeholder Replacement & Forced Stock Injection)
        impact = brief.get("impact_map", {})
        impact["theme"] = core_theme
        stocks = impact.get("mentionable_stocks", [])
        
        # Ensure Caterpillar (CAT) is present for AI Power Constraint
        if core_theme == "AI Power Constraint":
            has_cat = any(s.get("ticker") == "Caterpillar" or s.get("name") == "Caterpillar" for s in stocks)
            if not has_cat:
                stocks.append({
                    "ticker": "Caterpillar",
                    "name": "Caterpillar",
                    "rationale": self.get_structural_explanation("Caterpillar", core_theme)
                })

        for s in stocks:
            rationale = s.get("rationale", "")
            if "High relevance" in str(rationale) or not rationale:
                s["rationale"] = self.get_structural_explanation(s.get("ticker", s.get("name")), core_theme)
        
        # D. Topic Alignment
        studio = brief.get("content_studio", {})
        current_topic = studio.get("selected_topic", "")
        # If topic is generic or mismatched (e.g. Policy Radar for AI Power), override if needed
        # In this repair engine, we force align the topic name to the theme if it's too divergent
        if "Radar" in current_topic and core_theme not in current_topic:
            studio["selected_topic"] = f"{core_theme} Frontier"

        # E. Reconstruct into Flat + Nested Structure (Requested in 5.F + UI Compatibility)
        repaired_brief = {
            # Flat structure requested by user
            "core_theme": core_theme,
            "display_title": display_title,
            "narrative": {
                "title": narrative.get("title", display_title),
                "summary": narrative.get("summary", ""),
                "explanation": narrative.get("explanation", ""),
                "situation": narrative.get("situation", ""),
                "contradiction": narrative.get("contradiction", ""),
                "sector_impact": narrative.get("sector_impact", [])
            },
            "topic": {
                "name": studio.get("selected_topic", "N/A"),
                "pressure": studio.get("topic_pressure", 0)
            },
            "script": {
                "hook": studio.get("script", {}).get("hook", f"Today we focus on {core_theme}"),
                "message": studio.get("script", {}).get("core_message", ""),
                "action": studio.get("script", {}).get("operator_action", "WATCH")
            },
            "impact": {
                "theme": core_theme,
                "stocks": stocks
            },
            "decision": brief.get("investment_decision", {}),
            "risk": brief.get("risk", {}),
            "allocation": brief.get("portfolio_allocation", {}),
            
            # Nested structure for UI Backward Compatibility
            "market_radar": {
                "theme": core_theme,
                "early_signal_score": brief.get("market_radar", {}).get("early_signal_score", 0.8),
                "evolution_stage": brief.get("market_radar", {}).get("evolution_stage", "EXPANSION"),
                "momentum_state": brief.get("market_radar", {}).get("momentum_state", "ACCELERATING"),
                "momentum_score": brief.get("market_radar", {}).get("momentum_score", 0.51),
                "momentum_drivers": ["AI GPU Demand", "Data Center Capex", "Grid Modernization"]
            },
            "narrative_brief": {
                "title": display_title,
                "featured_theme": core_theme,
                "summary": narrative.get("summary", ""),
                "explanation": narrative.get("explanation", ""),
                "situation": narrative.get("situation", ""),
                "contradiction": narrative.get("contradiction", ""),
                "sector_impact": narrative.get("sector_impact", [])
            },
            "impact_map": {
                "theme": core_theme,
                "mentionable_stocks": stocks, # rationale fixed above
                "sector_status": brief.get("impact_map", {}).get("sector_status", {})
            },
            "content_studio": {
                "selected_topic": studio.get("selected_topic", "N/A"),
                "topic_pressure": studio.get("topic_pressure", 0),
                "script": studio.get("script", {})
            },
            "metadata": {
                "repaired_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source_build": "LOCKED-ENGINE",
                "consistency_aligned_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }

        # 4. Save Outputs
        self._save_json("data/ops/today_operator_brief.json", repaired_brief)
        # Backup to operator folder
        self._save_json("data/operator/today_operator_brief.json", repaired_brief)
        
        # 5. Save Individual Repaired Files (for Re-Verification)
        # Save top_topic.json
        repaired_topic = {
            "selected_topic": repaired_brief["topic"]["name"],
            "topic_pressure": repaired_brief["topic"]["pressure"],
            "updated_at": repaired_brief["metadata"]["repaired_at"]
        }
        self._save_json("data/ops/top_topic.json", repaired_topic)
        
        # Save script_output.json (mapping to today_video_script structure)
        repaired_script = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "theme": core_theme,
            "hook": repaired_brief["script"]["hook"],
            "core_message": repaired_brief["script"]["message"],
            "operator_action": repaired_brief["script"]["action"],
            "updated_at": repaired_brief["metadata"]["repaired_at"]
        }
        self._save_json("data/ops/script_output.json", repaired_script)
        
        # Save mentionables.json (mapping to impact_mentionables structure)
        repaired_mentionables = {
            "theme": core_theme,
            "mentionable_stocks": stocks,
            "metadata": {
                "generated_at": repaired_brief["metadata"]["repaired_at"],
                "engine_version": "1.0.0-REPAIRED"
            }
        }
        self._save_json("data/ops/mentionables.json", repaired_mentionables)
        
        print(f"[RepairEngine] Narrative Consistency Repaired for {core_theme} (including individual files)")
        return repaired_brief

if __name__ == "__main__":
    import sys
    root = Path(__file__).parent.parent.parent
    sys.path.append(str(root))
    
    # Mock some data if needed for standalone test
    engine = ConsistencyRepairEngine(root)
    engine.run_repair()
