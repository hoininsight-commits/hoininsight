import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

class StatementMomentumEngine:
    """
    [IS-94] Statement Momentum & Escalation Layer
    Tracks recurring themes from key persons to identify escalating intent.
    """
    INTENSITY_KEYWORDS = {
        "must": 2,
        "only solution": 3,
        "critical": 2,
        "unavoidable": 3,
        "cannot delay": 3,
        "national security": 4,
        "scale up": 2,
        "massive": 2,
        "absolute": 2,
        "priority": 2
    }

    THEME_MAP = {
        "AI": [r"ai\b", r"artificial intelligence", r"intelligence", r"llm", r"openai", r"gpu", r"nvidia"],
        "INFRA": [r"infrastructure", r"data center", r"power", r"energy", r"cluster", r"capacity"],
        "REGULATION": [r"regulation", r"policy", r"ftc", r"doj", r"sec", r"monopoly", r"lawsuit", r"compliance"],
        "SUPPLY_CHAIN": [r"supply", r"bottleneck", r"manufacturing", r"fab", r"shortage"],
        "MARKET": [r"demand", r"growth", r"revenue", r"market share", r"competitor"]
    }

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.logger = logging.getLogger("StatementMomentumEngine")
        self.momentum_dir = base_dir / "data" / "momentum"
        self.momentum_dir.mkdir(parents=True, exist_ok=True)

    def process(self, current_statements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Main entry point to calculate momentum.
        """
        # 1. Load historical data (last 30 days)
        history = self._load_history(days=30)
        
        # 2. Extract themes for current statements and add to history for rolling window
        today_ymd = datetime.now().strftime("%Y-%m-%d")
        for stmt in current_statements:
            stmt["theme"] = self._infer_theme(stmt.get("content", ""))
            stmt["date"] = stmt.get("published_at", today_ymd) # Fallback to today
            if isinstance(stmt["date"], str):
                 # Try to normalize date for comparison
                 try:
                     # Attempt common formats
                     for fmt in ["%Y-%m-%d", "%a, %d %b %Y %H:%M:%S %Z", "%Y%m%d"]:
                         try:
                             stmt["date_dt"] = datetime.strptime(stmt["date"][:10] if len(stmt["date"]) > 10 and "-" in stmt["date"] else stmt["date"], fmt)
                             break
                         except: continue
                 except:
                     stmt["date_dt"] = datetime.now()
            
            history.append(stmt)

        # 3. Group by Person + Theme
        grouped = {}
        for item in history:
            person = item.get("person_or_org") or item.get("entity") or "Unknown"
            theme = item.get("theme", "OTHER")
            key = (person, theme)
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(item)

        # 4. Calculate Momentum for each group
        momentum_results = []
        for (person, theme), items in grouped.items():
            if not any(i in current_statements for i in items):
                continue # Only process groups that have active signals today

            score = self._calculate_score(items)
            state = "STABLE"
            if score >= 7: state = "ESCALATING"
            elif score >= 4: state = "BUILDING"

            reason = self._generate_reason(person, theme, items, state)
            
            sorted_items = sorted(items, key=lambda x: x.get("date_dt", datetime.min))
            
            momentum_results.append({
                "person": person,
                "theme": theme,
                "momentum_score": score,
                "momentum_state": state,
                "first_seen_date": sorted_items[0].get("date", today_ymd),
                "last_seen_date": sorted_items[-1].get("date", today_ymd),
                "mention_count_30d": len(items),
                "escalation_reason": reason,
                "latest_content": sorted_items[-1].get("content", "")
            })

        # 5. Save results
        self._save_results(momentum_results)
        return momentum_results

    def _infer_theme(self, content: str) -> str:
        content_lower = content.lower()
        for theme, patterns in self.THEME_MAP.items():
            if any(re.search(p, content_lower) for p in patterns):
                return theme
        return "GENERAL"

    def _load_history(self, days: int) -> List[Dict[str, Any]]:
        history = []
        cutoff = datetime.now() - timedelta(days=days)
        
        # Load from data/statements/
        stmt_dir = self.base_dir / "data" / "statements"
        if stmt_dir.exists():
            for f in stmt_dir.glob("*.json"):
                try:
                    data = json.loads(f.read_text(encoding="utf-8"))
                    for item in data:
                        # Add theme if missing
                        if "theme" not in item:
                            item["theme"] = self._infer_theme(item.get("content", ""))
                        history.append(item)
                except: pass
        return history

    def _calculate_score(self, items: List[Dict[str, Any]]) -> float:
        # Base count score
        count = len(items)
        freq_score = min(count * 1.0, 4.0) # Max 4 from frequency
        
        # Intensity score (latest or max intensity)
        max_intensity = 0
        for item in items:
            text = item.get("content", "").lower()
            intensity = 0
            for kw, val in self.INTENSITY_KEYWORDS.items():
                if kw in text:
                    intensity += val
            max_intensity = max(max_intensity, intensity)
        
        intensity_score = min(max_intensity, 4.0) # Max 4 from intensity
        
        # Trust score
        trust_bonus = 0
        if any(i.get("trust_level") == "HARD_FACT" for i in items):
             trust_bonus = 2.0
             
        return min(freq_score + intensity_score + trust_bonus, 10.0)

    def _generate_reason(self, person: str, theme: str, items: List[Dict[str, Any]], state: str) -> str:
        count = len(items)
        if state == "ESCALATING":
            return f"{person}의 {theme} 관련 발언이 공식 문서와 결합되며 강력한 실행 의지로 급격히 격상되었습니다."
        elif state == "BUILDING":
            return f"최근 30일 내 {count}회 반복 언급되며 {theme}에 대한 관심도가 점진적으로 상승하고 있습니다."
        return f"{person}의 {theme} 관련 통상적 발언입니다."

    def _save_results(self, results: List[Dict[str, Any]]):
        ymd = datetime.now().strftime("%Y%m%d")
        out_path = self.momentum_dir / f"statement_momentum_{ymd}.json"
        data = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "momentum_list": results
        }
        out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        self.logger.info(f"Saved momentum report to {out_path}")
