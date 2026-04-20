# src/analysis/hunter_enricher.py
# HOIN Insight Hunter Analyst Enricher (v1.0)
# 목적: 모든 하위 분석 모듈을 통합하여 시그널 객체를 구조적 정보로 풍성하게 만듦

import json
from pathlib import Path
from src.analysis.surface_structure import SurfaceStructureLayer
from src.analysis.consequence_chain import ConsequenceChain
from src.analysis.flow_interpreter import FlowInterpreter
from src.analysis.beneficiary_mapper import BeneficiaryMapper
from src.analysis.why_now import WhyNowProjector

class HunterEnricher:
    def __init__(self):
        pass

    def enrich(self, signal: dict) -> dict:
        """Detector 결과(토픽)를 사냥꾼의 구조적 분석 데이터로 보강"""
        print("  🏹 경제사냥꾼 구조 분석 강화 레이어 가동...")
        
        # 1. Surface vs Structure
        ss = SurfaceStructureLayer.analyze(signal)
        signal["surface"] = ss["surface"]
        signal["structure"] = ss["structure"]
        
        # 2. Flow Interpretation
        signal["flow_interpretation_hunter"] = FlowInterpreter.interpret(signal)
        
        # 3. Chain of Consequence
        signal["consequence_chain"] = ConsequenceChain.build(signal)
        
        # 4. Beneficiary
        signal["beneficiary"] = BeneficiaryMapper.map(signal)
        
        # 5. Why Now
        signal["why_now_hunter"] = WhyNowProjector.project(signal)
        
        return signal
