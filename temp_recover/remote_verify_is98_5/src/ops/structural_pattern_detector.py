from typing import Dict, Any, List, Optional
import json
import hashlib
from pathlib import Path
from datetime import datetime
from enum import Enum

class StructuralPattern(Enum):
    SYSTEM_TRUST_STRESS = "SYSTEM_TRUST_STRESS"
    REAL_RATE_TENSION = "REAL_RATE_TENSION"
    LIQUIDITY_ROTATION = "LIQUIDITY_ROTATION"
    PANIC_LIQUIDATION_PRECURSOR = "PANIC_LIQUIDATION_PRECURSOR"
    POLICY_CLOCK_CONVERGENCE = "POLICY_CLOCK_CONVERGENCE"

class StructuralPatternDetector:
    """
    Step 86: Cognitive Layer for detecting recurring structural patterns.
    Does NOT predict prices. Identify regime patterns.
    """
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.snapshot_dir = base_dir / "data" / "snapshots" / "patterns"
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        
    def detect_and_save(self, date: str, final_decision_card: Dict[str, Any]) -> Path:
        """
        Runs detection logic and saves the snapshot.
        """
        active_patterns = self._detect_patterns(final_decision_card)
        
        snapshot = {
            "date": date,
            "meta": {
                "generated_at": datetime.now().isoformat() + "Z",
                "engine_version": "v1.0"
            },
            "active_patterns": active_patterns,
            "pattern_count": len(active_patterns)
        }
        
        # Add hash
        content_str = json.dumps(snapshot, sort_keys=True)
        snapshot["pattern_hash"] = hashlib.sha256(content_str.encode()).hexdigest()
        
        file_path = self.snapshot_dir / f"{date}.json"
        file_path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False), encoding="utf-8")
        
        return file_path

    def _detect_patterns(self, card: Dict[str, Any]) -> List[Dict[str, Any]]:
        patterns = []
        
        # Flatten signals for analysis
        signals_text = str(card) # Simple string dump for keyword search (can be more structured)
        top_topics = card.get("top_topics", [])
        
        # 1. SYSTEM_TRUST_STRESS
        # Keywords: Central Bank, Fed, Gold, Independence, Trust, Crisis
        trust_keywords = ["중앙은행", "Fed", "금리 인하", "신뢰", "독립성", "개입", "System", "Trust", "Gold", "금"]
        if self._check_keywords(signals_text, trust_keywords, threshold=2):
             patterns.append({
                 "pattern_type": StructuralPattern.SYSTEM_TRUST_STRESS.value,
                 "confidence": "HIGH" if "붕괴" in signals_text or "Crisis" in signals_text else "MEDIUM",
                 "narrative": "중앙은행의 통제력이나 시스템 신뢰에 대한 의구심이 확산되고 있습니다.",
                 "signals": ["Central Bank Narrative", "Safe Haven Interest"]
             })

        # 2. REAL_RATE_TENSION
        # Keywords: Inflation, CPI, Sticky, 10Y, Bond, Valuation, PER
        rate_keywords = ["물가", "인플레이션", "수익률", "국채", "Valuation", "PER", "Real Rate", "Sticky"]
        if self._check_keywords(signals_text, rate_keywords, threshold=2):
             patterns.append({
                 "pattern_type": StructuralPattern.REAL_RATE_TENSION.value,
                 "confidence": "HIGH" if "Sticky" in signals_text or "고착화" in signals_text else "MEDIUM",
                 "narrative": "실질 금리와 인플레이션 경로의 불확실성이 자산 가치 평가를 압박하고 있습니다.",
                 "signals": ["Sticky Inflation", "Rate Volatility"]
             })

        # 3. LIQUIDITY_ROTATION
        # Keywords: Capex, Infra, Energy, Rotation, Growth to Value, Physical
        rotation_keywords = ["Capex", "인프라", "에너지", "전력", "Rotation", "실물", "Commodity"]
        has_infra_topic = any("공급망" in t.get("title", "") or "Infrastructure" in str(t) for t in top_topics)
        
        if has_infra_topic or self._check_keywords(signals_text, rotation_keywords, threshold=2):
             patterns.append({
                 "pattern_type": StructuralPattern.LIQUIDITY_ROTATION.value,
                 "confidence": "HIGH",
                 "narrative": "성장 스토리에서 실물/인프라 필수재로의 자금 이동(Rotation)이 관측됩니다.",
                 "signals": ["Infrastructure Capex", "Physical Asset Demand"]
             })

        # 4. PANIC_LIQUIDATION_PRECURSOR
        # Keywords: Margin call, Cash, Sell everything, Safe asset sell, Crash
        panic_keywords = ["마진콜", "현금", "투매", "청산", "Liquidation", "Panic", "안전자산 매도"]
        if self._check_keywords(signals_text, panic_keywords, threshold=1):
             patterns.append({
                 "pattern_type": StructuralPattern.PANIC_LIQUIDATION_PRECURSOR.value,
                 "confidence": "MEDIUM", # Default medium for precursors
                 "narrative": "모든 자산이 동반 매도되는 유동성 청산(Liquidation) 징후가 포착됩니다.",
                 "signals": ["Cash Raising", "Broad Selling"]
             })
             
        # 5. POLICY_CLOCK_CONVERGENCE
        # Keywords: Deadline, Election, FOMC, Date, D-Day
        clock_keywords = ["D-Day", "일정", "선거", "발표", "Deadline", "기한", "만기"]
        if self._check_keywords(signals_text, clock_keywords, threshold=2):
              patterns.append({
                 "pattern_type": StructuralPattern.POLICY_CLOCK_CONVERGENCE.value,
                 "confidence": "MEDIUM",
                 "narrative": "다수의 정책/일정 데드라인이 겹치며 시간 압박이 시장을 지배하고 있습니다.",
                 "signals": ["Policy Deadlines", "Time Compression"]
             })
             
        return patterns

    def _check_keywords(self, text: str, keywords: List[str], threshold: int = 1) -> bool:
        count = 0
        for k in keywords:
            if k in text:
                count += 1
        return count >= threshold
