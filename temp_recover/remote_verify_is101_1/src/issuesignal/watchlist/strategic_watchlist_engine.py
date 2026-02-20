import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any

class StrategicWatchlistEngine:
    """
    (IS-81) Generates 'Strategic Watchlist' content for daily market structure observation.
    Operates without confirmed 'Trust Locked' facts, focusing on schedules, 
    structural patterns, and macro scenarios.
    """
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.output_dir = base_dir / "data" / "watchlist"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate(self, as_of_date: str = None) -> Path:
        """
        Generates the daily watchlist JSON.
        """
        if not as_of_date:
            as_of_date = datetime.utcnow().strftime("%Y-%m-%d")
            
        print(f"[{as_of_date}] Generating Strategic Watchlist...")
        
        watchlist_items = []
        
        # 1. PREVIEW: Schedule Based (Mock/Input based)
        # In real impl, checking data/inputs/calendar or config
        preview_items = self._scan_schedules(as_of_date)
        watchlist_items.extend(preview_items)
        
        # 2. STRUCTURE: Pattern Memory Based
        structure_items = self._scan_patterns(as_of_date)
        watchlist_items.extend(structure_items)
        
        # 3. SCENARIO: Macro/Scenario Based
        scenario_items = self._scan_scenarios(as_of_date)
        watchlist_items.extend(scenario_items)
        
        # Final Payload
        payload = {
            "date": as_of_date,
            "watchlist": watchlist_items,
            "meta": {
                "generated_at": datetime.utcnow().isoformat(),
                "count": len(watchlist_items)
            }
        }
        
        output_path = self.output_dir / f"strategic_watchlist_{as_of_date}.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
            
        print(f"   Saved Watchlist: {output_path}")
        return output_path

    def _scan_schedules(self, ymd: str) -> List[Dict]:
        """Scan for upcoming key events (1-14 days)."""
        # [Placeholder Logic] - In future, read from `data/inputs/calendar`
        # For MVP, we allow manual injection via `data/inputs/watchlist_seeds.json` if exists,
        # or generate static fallback for testing if empty.
        
        items = []
        # Mock Schedule for MVP proof
        # Check if today is Monday (example)
        dt = datetime.strptime(ymd, "%Y-%m-%d")
        
        # Example Item 1
        items.append({
            "id": f"WL-{ymd.replace('-','')}-001",
            "type": "PREVIEW",
            "theme": "FOMC & Liquidity",
            "why_watch": "금리 결정 이후 단기 유동성 향방 결정",
            "expected_window": "This Week",
            "escalation_condition": "파월 의장 '공급망' 언급 시",
            "status": "WATCHING"
        })
        return items

    def _scan_patterns(self, ymd: str) -> List[Dict]:
        """Scan recent structural patterns."""
        # [Placeholder] Read `data/pattern_memory`
        # For IS-81 MVP, returning a fixed structure example
        return [{
            "id": f"WL-{ymd.replace('-','')}-002",
            "type": "STRUCTURE",
            "theme": "AI Capex Bottleneck",
            "why_watch": "빅테크 실적 발표 시즌, AI 수익화 지연 우려 vs Capex 지속",
            "expected_window": "2 Weeks",
            "escalation_condition": "주요 ASML/TSMC 수주 취소 루머 발생 시",
            "status": "WATCHING"
        }]

    def _scan_scenarios(self, ymd: str) -> List[Dict]:
        """Scan conditional scenarios."""
        return [{
            "id": f"WL-{ymd.replace('-','')}-003",
            "type": "SCENARIO",
            "theme": "Oil Price Spike (Hormuz)",
            "why_watch": "지정학적 리스크 임계치 근접 (WTI $80 접근)",
            "expected_window": "Indefinite",
            "escalation_condition": "WTI $85 돌파 및 주요국 긴급 성명",
            "status": "WATCHING"
        }]
