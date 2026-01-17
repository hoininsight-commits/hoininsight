"""
Phase 35: Deep Logic Analyzer (Simulated/Ready for Integration)
Since we are in a protected environment without external API access,
this version implements the LOGIC ARCHITECTURE but MOCKS the LLM call for demonstration.
"""

import json
from pathlib import Path
from typing import Dict, Any, List
import hashlib
from datetime import datetime

try:
    from src.learning.logic_evolver import LogicEvolver
except ImportError:
    pass

class DeepLogicAnalyzer:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        # Brain loading
        self.data_master = (base_dir / "docs/DATA_COLLECTION_MASTER.md").read_text()
        self.anomaly_logic = (base_dir / "docs/ANOMALY_DETECTION_LOGIC.md").read_text()

    def analyze(self, transcript: str, title: str) -> Dict[str, Any]:
        """
        In a real scenario, this sends the prompt to Gemini.
        Here, we mimic the expert reasoning demonstrated in the few-shot examples.
        """
        print(f"[DeepLogicAnalyzer] Analyzing transcript for: {title}")
        print("[DeepLogicAnalyzer] Loading Context: DATA_COLLECTION_MASTER & ANOMALY_DETECTION_LOGIC...")
        print("[DeepLogicAnalyzer] Simulating Expert Reasoning Process...")
        
        # Check title to route to appropriate mock response
        if "MOCK_MODE" in title or "MOCK MODE" in title: # Explicit mock trigger
            if "트럼프" in title or "파월" in title:
               return self._mock_trump_powell_case()
            elif "모건" in title or "장기 투자" in title:
               return self._mock_morgan_case()
            elif "워런 버핏" in title or "이란" in title or "Iran" in title:
               return self._mock_warren_buffett_case()
            elif "한화" in title or "인적 분할" in title:
               return self._mock_hanwha_case()
            elif "파크" in title or "Park" in title or "반도체" in title:
               return self._mock_park_systems_case()
            else:
               return self._mock_new_case_logic(title)
        else:
            # REAL Analysis Mode
            return self.analyze_heuristic(transcript, title)

    def analyze_heuristic(self, transcript: str, title: str) -> Dict[str, Any]:
        """
        Perform actual heuristic analysis using LogicEvolver patterns + KnowledgeBase checks.
        """
        # Lazy load LogicEvolver to avoid circular imports if any
        try:
            evolver = LogicEvolver(self.base_dir)
        except NameError:
             from src.learning.logic_evolver import LogicEvolver
             evolver = LogicEvolver(self.base_dir)

        patterns = evolver.discover_logic_patterns(transcript, title)
        
        proposals = []
        logic_gaps = []
        data_gaps = []
        
        # 1. Analyze Patterns for Gaps
        for p in patterns:
            # Check Data Gaps (Unknown Nouns) in Condition/Implication
            # detailed check would require NLP, here we use simple space splitting and check against KB headers
            terms = p['condition'].split() + p['implication'].split()
            for term in terms:
                # Minimal cleaning
                term = term.strip().replace("가", "").replace("이", "").replace("을", "").replace("를", "") 
                if len(term) < 2: continue
                
                # Check if term exists in KnowledgeBase (very simple check for now)
                # We assume KB has a 'contains' method or we scan raw text
                # For this version, we'll scan the raw loaded text
                if term not in self.data_master:
                    data_gaps.append(term)
            
            # Use pattern as Logic Gap candidate
            logic_gaps.append(p)

        # 2. Formulate Proposals
        # Deduplicate data gaps
        data_gaps = list(set(data_gaps))
        
        # Limit proposals to top 3 to avoid spam
        for gap_term in data_gaps[:3]:
            # Guess category
            cat = "| Uncategorized |"
            if "가격" in gap_term or "지수" in gap_term: cat = "| Market Data |"
            elif "정책" in gap_term: cat = "| Policy |"
            
            prop_content = f"{cat} {gap_term} | Source: {gap_term} | Unknown | Free | CANDIDATE | Found in: {title} |"
            
            proposals.append({
                "type": "DATA",
                "category": "DATA_UPDATE",
                "content": prop_content,
                "reason": f"System blindspot: '{gap_term}' detected in high-importance logic."
            })
            
        for p in logic_gaps[:2]:
            proposals.append({
                "type": "LOGIC",
                "category": "LOGIC_UPDATE",
                "content": f"IF {p['condition']} THEN {p['implication']} (Type: {p['type']})",
                "reason": f"New causal pattern detected: {p['original_sentence'][:50]}..."
            })
            
        # 3. Construct Result
        has_update = len(proposals) > 0
        
        return {
            "summary": f"Analyzed '{title}' - Found {len(data_gaps)} potential data gaps & {len(logic_gaps)} logic patterns.",
            "data_usage": [], # Can't accurately determine usage without full NLP yet
            "anomaly_detected": {
                "description": "Pattern-based Logic Discovery",
                "level": "L2 (Heuristic)"
            },
            "why_now_type": "Data-driven",
            "logic_gap_analysis": {
                "new_data_needed": len(data_gaps) > 0,
                "new_logic_needed": len(logic_gaps) > 0,
                "reason": f"Extracted {len(patterns)} explicit logic patterns."
            },
            "learned_rule": logic_gaps[0]['original_sentence'] if logic_gaps else "No explicit rule found.",
            "final_decision": "UPDATE_REQUIRED" if has_update else "LOG_ONLY",
            "proposals": proposals
        }

    def _mock_trump_powell_case(self):
        """Mock response for Trump vs Powell Case"""
        return {
            "summary": "미국 통화정책 신뢰 훼손(Independent Risk)에 따른 자본 이동",
            "data_usage": [
                {"axis": "Gov Policy", "usage": "Political Intervention (Fed Independence)"},
                {"axis": "Rates > Spread", "usage": "Risk Premium Spike"},
                {"axis": "Commodities > Gold", "usage": "System Hedge"}
            ],
             "anomaly_detected": {
                "description": "Policy Rate vs Market Rate Decoupling (Trust Crisis)",
                "level": "L3 (Hybrid driven)"
            },
            "why_now_type": "Hybrid-driven (Schedule + State)",
            "logic_gap_analysis": {
                "new_data_needed": False,
                "new_logic_needed": False,
                "reason": "Existing 'Policy Uncertainty' & 'Safe Haven Flow' logic covers this scenario."
            },
            "learned_rule": "정책 숫자가 변하지 않아도 정책 '독립성'이 의심받으면, 시장은 장기 프리미엄과 안전자산 이동으로 먼저 반응한다.",
            "final_decision": "LOG_ONLY"
        }

    def _mock_morgan_case(self):
         """Mock response for Morgan Stanley Capex Case"""
         return {
            "summary": "구조적 자본 상태 변화(State Shift)에 따른 장기 고정 자본 형성",
            "data_usage": [
                {"axis": "Global Supply Chain", "usage": "Decoupling context"},
                {"axis": "Gov Policy", "usage": "State Capitalism (Capex Support)"}
            ],
            "anomaly_detected": {
                "description": "Capex-Cycle Decoupling (No Recession Impact)",
                "level": "L3 (Hybrid driven)"
            },
            "why_now_type": "State-driven",
            "logic_gap_analysis": {
                "new_data_needed": False,
                "new_logic_needed": False,
                "reason": "Can be explained by existing (C) Capex logic."
            },
            "learned_rule": "정부가 자본 비용을 직접 부담하면, 민간 투자는 경기 민감도를 잃고 장기 고정 자본화된다.",
            "final_decision": "LOG_ONLY"
        }

    def _mock_warren_buffett_case(self):
         """Mock response for Warren Buffett & Iran Case - Updated with User's Insight"""
         return {
            "summary": "이란 사태는 단순 이벤트가 아닌 '자본 경로의 강제 재고정(Capital Route Reconfiguration)' 시그널임.",
            "data_usage": [
                {"axis": "Commodities > Oil", "usage": "Price Spike (L1 Effect)"},
                {"axis": "Equities > Energy", "usage": "Sector Rotation (L2 Effect)"}
            ],
            "anomaly_detected": {
                "description": "L3 STRUCTURAL ANOMALY: Energy Supply Path Collapse",
                "level": "L3 (State-Driven)"
            },
             "why_now_type": "Hybrid-driven (State + Political) - 공급 경로 붕괴 임계점",
            "logic_gap_analysis": {
                "new_data_needed": True,
                "new_logic_needed": True,
                "reason": "단순 유가/뉴스 모니터링으로는 '경로 붕괴'와 '자본 재고정'의 구조적 변화를 감지할 수 없음. 군사/물류/LNG계약 데이터 필수."
            },
            "learned_rule": "지정학 리스크가 물리적 경로(해협 봉쇄 등)를 위협할 때, 자본은 안전 자산이 아니라 '대체 공급 독점처(미국 에너지)'로 강제 이동한다.",
            "final_decision": "UPDATE_REQUIRED",
            "proposals": [
                {
                    "type": "DATA", 
                    "category": "DATA_UPDATE",
                    "content": "| 에너지/물류 | LNG 장기 공급 계약 추이 | Cheniere/EIA | Trend | Free | CANDIDATE | 대체 경로 독점화 확인 |"
                },
                {
                    "type": "DATA",
                    "category": "DATA_UPDATE",
                    "content": "| 운송/해운 | Tanker/BDI 운임 지수 | Bloomberg/Baltic | Index | Paid/Delayed | CANDIDATE | 공급망 물리적 병목 감지 |"
                },
                {
                    "type": "LOGIC",
                    "category": "LOGIC_UPDATE",
                    "content": "IF [Physical Route Risk] AND [No Alternative Path] THEN [Capital Forced to US Energy Assets]"
                }
            ]
        }
        
    def _mock_hanwha_case(self):
        """Mock response for Hanwha Structural Event Case"""
        return {
            "summary": "구조적 할인 해소(Event-Driven Restructuring)에 따른 자본 재평가",
            "data_usage": [
                 {"axis": "Corp Action > Buyback", "usage": "Signaling"},
                 {"axis": "Equities > Holding Co", "usage": "Discount Removal"}
            ],
             "anomaly_detected": {
                "description": "Governance-driven Value Unlock",
                "level": "L3 (Structural Event)"
            },
            "why_now_type": "State-driven (Internal Structuring)",
            "logic_gap_analysis": {
                "new_data_needed": True,
                "new_logic_needed": False, # Logic exists (L3), but sensors are missing
                "reason": "To detect this 'Pre-Event', we need Governance Data (Buyback/Stake Flow) which transforms Engine from Observer to Sensor."
            },
            "learned_rule": "구조적 이벤트(분할/승계)는 실적이 아니라 '자본/지배구조(자사주, 지분)'의 미세한 움직임으로 먼저 감지된다.",
            "final_decision": "UPDATE_REQUIRED",
             "proposals": [
                {
                    "type": "DATA", 
                    "category": "META_UPGRADE", # Special Tag
                    "content": "| 기업/지배구조 | 자사주 취득/소각 공시 | Dart/Exchange | Event | Free | CORE_CANDIDATE | 구조 이벤트 사전 감지 (Sensor Upgrade) |"
                },
                {
                    "type": "DATA",
                    "category": "META_UPGRADE",
                    "content": "| 기업/지배구조 | 대주주 지분 변동 | Dart | Event | Free | CORE_CANDIDATE | 승계/재편 사전 징후 포착 |"
                }
            ]
        }

    def _mock_park_systems_case(self):
         """Mock response for Park Systems (Atomic Microscopy) Logic"""
         return {
            "summary": "미세 공정 한계 돌파(Hybrid Bonding)에 따른 계측 장비 필수화",
            "data_usage": [
                {"axis": "Tech Cycle > Yield", "usage": "Defect Rate correlation"},
                {"axis": "Supply Chain > Equipment", "usage": "Sole Vendor Validation"}
            ],
            "anomaly_detected": {
                "description": "Atomic Level Inspection Demand Surge",
                "level": "L3 (Hybrid driven)"
            },
            "why_now_type": "Tech-driven",
            "logic_gap_analysis": {
                "new_data_needed": True,
                "new_logic_needed": True,
                "reason": "New dependency: Yield is now function of Atomic Flatness, not just optical resolution."
            },
            "learned_rule": "하이브리드 본딩 공정에서는 표면 거칠기(Roughness)가 수율의 핵심 변수이며, 이를 측정하는 원자현미경(AFM)은 선택이 아닌 필수다.",
            "final_decision": "UPDATE_REQUIRED",
            "proposals": [
                {
                    "type": "LOGIC",
                    "category": "LOGIC_UPDATE",
                    "content": "IF Process == 'Hybrid Bonding' THEN Quality_Check MUST_INCLUDE 'Atomic Force Microscopy'",
                    "reason": "Optical inspection fails at sub-nanometer roughness levels required for Cu-Cu bonding."
                },
                {
                    "type": "DATA",
                    "category": "DATA_UPDATE",
                    "content": "| Tech Supply Chain | AFM Penetration Rate | Source: Company Reports | Unknown | Free | CANDIDATE | Found in: Park Systems Analysis |",
                    "reason": "Missing data on Atomic Force Microscopy adoption rate in advanced packaging lines."
                }
            ]
        }

    def _mock_new_case_logic(self, title):
        """Mock for a new logic discovery case (Gold/Copper)"""
        return {
            "summary": "금/구리 괴리(Divergence)를 활용한 신규 침체 탐지 로직 제안",
            "data_usage": [
                 {"axis": "Commodities > Gold", "usage": "Safe Haven"},
                 {"axis": "Commodities > Copper", "usage": "Industrial"}
            ],
             "anomaly_detected": {
                "description": "Gold/Copper Ratio Breakout",
                "level": "L3"
            },
            "why_now_type": "Hybrid-driven",
            "logic_gap_analysis": {
                "new_data_needed": False,
                "new_logic_needed": True,
                "reason": "Gold/Copper divergence logic is missing explicitly."
            },
            "learned_rule": "구리 가격 하락과 금 가격 신고가가 동시 발생(비율 급등)하면 강력한 침체 신호이다.",
            "final_decision": "UPDATE_REQUIRED"
        }

def main():
    base_dir = Path(__file__).parent.parent.parent
    analyzer = DeepLogicAnalyzer(base_dir)
    
    # Test Case 1: Trump/Powell
    print("\n--- TEST CASE 1: Trump vs Powell ---")
    res1 = analyzer.analyze("...", "트럼프 대 파월 싸움")
    print(json.dumps(res1, indent=2, ensure_ascii=False))
    
    if res1['final_decision'] == "LOG_ONLY":
        print("✅ Effect: No System Change (Observation Log Created)")

    # Test Case 2: New Logic Discovery
    print("\n--- TEST CASE 2: Unknown Logic ---")
    res2 = analyzer.analyze("...", "금과 구리의 기이한 움직임")
    print(json.dumps(res2, indent=2, ensure_ascii=False))

    if res2['final_decision'] == "UPDATE_REQUIRED":
         print("🚨 Effect: New Evolution Proposal Created (Needs Approval)")

    # Test Case 3: Complex Evolution (Data + Logic)
    print("\n--- TEST CASE 3: Warren Buffett & Iran ---")
    res3 = analyzer.analyze("...", "워런 버핏과 이란 사태")
    print(json.dumps(res3, indent=2, ensure_ascii=False))
    
    if res3['final_decision'] == "UPDATE_REQUIRED":
         print("🚨 Effect: New Evolution Proposal Created (Needs Approval - MULTI ITEM)")
         if "proposals" in res3:
             for p in res3["proposals"]:
                 print(f"   + [PROPOSAL] Type: {p['type']} -> {p['content'][:50]}...")

    # Test Case 4: Meta-Evolution (Engine Upgrade)
    print("\n--- TEST CASE 4: Hanwha Structure (Engine Upgrade) ---")
    res4 = analyzer.analyze("...", "한화 인적 분할과 지배구조")
    print(json.dumps(res4, indent=2, ensure_ascii=False))

    if res4['final_decision'] == "UPDATE_REQUIRED":
         print("🚨 Effect: META-UPGRADE Proposal Created (Needs Critical Approval)")
         if "proposals" in res4:
             for p in res4["proposals"]:
                 print(f"   + [CORE UPGRADE] {p['content'][:60]}...")

if __name__ == "__main__":
    main()
