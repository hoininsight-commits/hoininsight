#!/usr/bin/env python3
"""
STEP-16: Structural Mentionables Engine
Links topics to stocks through hierarchical mapping (Topic -> Sector -> Supply Chain -> Stocks).
Strictly follows NO-LLM and DETERMINISTIC policy.
"""
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("StructuralMentionables")

# 1. Sector Mapping Rules
SECTOR_MAP = {
    "Inflation": ["Financials"],
    "Financial Regulation": ["Financials"],
    "Crypto Regulation": ["Financial Infrastructure"],
    "Semiconductor Supply Chain": ["Semiconductors"],
    "AI Infrastructure": ["Semiconductors", "Data Center"],
    "Energy Shock": ["Energy"],
    "Macro Shock Radar": ["Financials", "Safe Haven"],
    "Policy Radar": ["Financials", "Infrastructure"]
}

# 2. Supply Chain Mapping
SUPPLY_CHAIN_MAP = {
    "Financials": ["Banks", "Exchanges"],
    "Financial Infrastructure": ["Exchanges", "Banks"],
    "Semiconductors": ["Design", "Foundry", "Equipment", "Materials"],
    "Data Center": ["GPU", "Cloud", "Cooling"],
    "Energy": ["Upstream", "Midstream", "Downstream"],
    "Safe Haven": ["Gold", "Inverse"]
}

# 3. Stock Database
STOCK_DB = [
    {"name": "삼성전자", "ticker": "005930.KS", "sector": "Semiconductors", "supply_chain_position": "Foundry", "reason": "글로벌 파운드리 및 메모리 1위"},
    {"name": "SK하이닉스", "ticker": "000660.KS", "sector": "Semiconductors", "supply_chain_position": "Design", "reason": "HBM 등 차세대 메모리 선도"},
    {"name": "한미반도체", "ticker": "042700.KS", "sector": "Semiconductors", "supply_chain_position": "Equipment", "reason": "HBM향 TC 본더 핵심 장비 공급"},
    {"name": "원익IPS", "ticker": "240810.KQ", "sector": "Semiconductors", "supply_chain_position": "Equipment", "reason": "반도체 증착 장비 국산화 선두"},
    {"name": "ASML", "ticker": "ASML", "sector": "Semiconductors", "supply_chain_position": "Equipment", "reason": "EUV 노광 장비 독점 공급"},
    {"name": "TSMC", "ticker": "TSM", "sector": "Semiconductors", "supply_chain_position": "Foundry", "reason": "글로벌 파운드리 시장 점유율 1위"},
    {"name": "Nvidia", "ticker": "NVDA", "sector": "Data Center", "supply_chain_position": "GPU", "reason": "AI 연산용 GPU 시장 압도적 점유"},
    {"name": "AMD", "ticker": "AMD", "sector": "Data Center", "supply_chain_position": "GPU", "reason": "Nvidia의 강력한 경쟁자 및 CPU 강자"},
    {"name": "POSCO홀딩스", "ticker": "005490.KS", "sector": "Energy", "supply_chain_position": "Upstream", "reason": "리튬 등 이차전지 소재 밸류체인 구축"},
    {"name": "KB금융", "ticker": "105560.KS", "sector": "Financials", "supply_chain_position": "Banks", "reason": "국내 최대 금융 지주 및 금리 수혜"},
    {"name": "신한지주", "ticker": "055550.KS", "sector": "Financials", "supply_chain_position": "Banks", "reason": "주주 환원 및 포트폴리오 다각화"},
    {"name": "KODEX 골드선물", "ticker": "132030.KS", "sector": "Safe Haven", "supply_chain_position": "Gold", "reason": "금 가격 변동 추종 상장지수펀드"}
]

class StructuralMentionablesEngine:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.output_path = self.base_dir / "data/decision/mentionables.json"

    def _load_json(self, path: Path):
        if not path.exists():
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def run(self, topic_theme: str = None, mechanism_text: str = None):
        logger.info(f"Running Mentionables Engine for Theme: {topic_theme}")
        
        # 1. Identify Target Sectors
        target_sectors = SECTOR_MAP.get(topic_theme, [])
        if not target_sectors and mechanism_text:
            # Simple keyword matching if theme doesn't match directly
            m_text = mechanism_text.lower()
            if any(k in m_text for k in ["금리", "inflation", "fed", "연준", "tightening"]):
                target_sectors.extend(SECTOR_MAP["Inflation"])
            if any(k in m_text for k in ["반도체", "semiconductor", "chip", "nvidia", "tsmc"]):
                target_sectors.extend(SECTOR_MAP["Semiconductor Supply Chain"])
            if any(k in m_text for k in ["vix", "공포", "risk", "hazard", "shock", "hybrid"]):
                target_sectors.extend(SECTOR_MAP["Macro Shock Radar"])
            if any(k in m_text for k in ["수사", "횡령", "정부", "policy", "regulation"]):
                target_sectors.extend(SECTOR_MAP["Policy Radar"])
        
        target_sectors = list(set(target_sectors))
        logger.info(f"Identified Target Sectors: {target_sectors}")

        # 2. Filter Stocks based on Sectors
        mentionables = []
        for stock in STOCK_DB:
            if stock["sector"] in target_sectors:
                mentionables.append({
                    "name": stock["name"],
                    "ticker": stock["ticker"],
                    "theme": f"{stock['sector']} {stock['supply_chain_position']}",
                    "reason": stock["reason"],
                    "mechanism_link": stock["sector"],
                    "risk": f"{stock['sector']} 리스크 확인 필요"
                })

        # 3. Output as JSON
        output_data = {
            "generated_at": datetime.now().isoformat(),
            "theme": topic_theme,
            "mentionables": mentionables,
            "governance": {
                "deterministic": True,
                "no_llm": True,
                "structural_linkage": True
            }
        }

        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Successfully generated {len(mentionables)} mentionables at {self.output_path}")
        return mentionables

def main():
    # Use project root
    base_dir = Path(__file__).resolve().parent.parent.parent
    engine = StructuralMentionablesEngine(base_dir)
    
    # Try to load recent narrative to get theme
    narrative_path = base_dir / "data/decision/narrative_intelligence.json"
    narrative_data = engine._load_json(narrative_path)
    
    theme = None
    mechanism = None
    if narrative_data:
        # Check if theme is in narrative, otherwise use common fallbacks
        theme = narrative_data.get("theme")
        mechanism = narrative_data.get("storyline", {}).get("mechanism", "")
    
    # [STEP-18] Load Propagation Data for conditional execution
    propagation_path = base_dir / "data/ops/narrative_propagation.json"
    propagation_data = engine._load_json(propagation_path)
    propagation_map = {}
    if propagation_data and "results" in propagation_data:
        propagation_map = {res["topic_id"]: res for res in propagation_data["results"]}

    # [STEP-17] Also check for Predicted Topics
    prediction_path = base_dir / "data/ops/topic_predictions.json"
    prediction_data = engine._load_json(prediction_path)
    if prediction_data and "predictions" in prediction_data:
        for pred in prediction_data["predictions"]:
            p_theme = pred.get("theme")
            topic_id = pred.get("topic_id")
            
            # [STEP-18] Check Propagation Score
            prop_res = propagation_map.get(topic_id, {"propagation_score": 0})
            if prop_res["propagation_score"] <= 80:
                logger.info(f"Skipping Mentionables for {topic_id} (Score: {prop_res['propagation_score']})")
                continue
                
            if p_theme:
                logger.info(f"Processing Predicted Topic: {p_theme} (Score: {prop_res['propagation_score']})")
                engine.run(topic_theme=p_theme, mechanism_text=pred.get("prediction_reason"))

    # Process reactive narrative theme
    if theme or mechanism:
        # Note: Reactive topics might not have propagation score yet, allowed by default or checked if present
        engine.run(topic_theme=theme, mechanism_text=mechanism)

if __name__ == "__main__":
    main()
